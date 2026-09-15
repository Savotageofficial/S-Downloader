"""Lossless media pairing, processing and verification."""
import json
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
ACTIVE_STATES = {'choosing', 'downloading', 'merging', 'verifying'}
PROTOCOLS = {'http', 'https', 'm3u8', 'm3u8_native', 'http_dash_segments'}


def media_tool(name):
    bundled = ROOT / 'vendor' / 'ffmpeg' / f'{name}.exe'
    if bundled.is_file():
        return str(bundled)
    if not getattr(sys, 'frozen', False) and (installed := shutil.which(name)):
        return installed
    raise RuntimeError('FFmpeg tools are missing. Extract the complete application package again.')


def has_codec(fmt, name):
    return fmt.get(name) not in (None, 'none')


def pair_audio(video, audios):
    """Prefer compatible audio, preserving yt-dlp's best-last ordering."""
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}.get(video.get('ext'))
    if audio_ext:
        for audio in reversed(audios):
            if audio.get('ext') == audio_ext:
                return audio, video['ext']
    return (audios[-1] if audios else None), 'mkv'


def _selection(fmt, audios, link):
    """Describe a future download using metadata only."""
    video = has_codec(fmt, 'vcodec')
    audio = None
    container = fmt.get('ext') or 'mkv'
    unavailable = ''
    if video and not has_codec(fmt, 'acodec'):
        audio, container = pair_audio(fmt, audios)
        if audio is None:
            unavailable = 'No audio track is available for this video.'
    elif not video:
        audio = fmt
    return {
        'link': link,
        'video_id': str(fmt['format_id']) if video else None,
        'audio_id': str(audio['format_id']) if audio else None,
        'container': container,
        'unavailable_reason': unavailable,
    }, audio if video else None


def _estimated_size(*tracks):
    sizes = [track.get('filesize') or track.get('filesize_approx') for track in tracks]
    return sum(sizes) if all(size is not None for size in sizes) else None


def _format_row(fmt, token, selection, paired_audio):
    tracks = (fmt, paired_audio) if paired_audio is not None else (fmt,)
    return {
        'id': token,
        'format_id': str(fmt['format_id']),
        'resolution': f"{fmt['height']}p" if fmt.get('height') else fmt.get('format_note', 'Video'),
        'format_note': fmt.get('format_note'),
        'container': selection['container'],
        'fps': fmt.get('fps'),
        'codec': (fmt.get('vcodec') or '').split('.')[0],
        'has_audio': not selection['unavailable_reason'],
        'unavailable_reason': selection['unavailable_reason'],
        'filesize': _estimated_size(*tracks),
        'abr': f"{round(fmt.get('abr') or 0)} kbps ({fmt.get('ext')})",
    }


def format_choices(metadata, link):
    """Build UI rows and opaque selections; never fetch or probe media."""
    videos, audios = [], []
    for fmt in metadata.get('formats') or []:
        if (fmt.get('has_drm') or not fmt.get('format_id') or not fmt.get('url')
                or fmt.get('protocol') not in PROTOCOLS):
            continue
        if has_codec(fmt, 'vcodec'):
            videos.append(fmt)
        elif has_codec(fmt, 'acodec'):
            audios.append(fmt)
    videos.sort(key=lambda fmt: (fmt.get('height') or 0, fmt.get('fps') or 0), reverse=True)

    selections = {}
    rows = []
    for formats in (videos, reversed(audios)):
        group = []
        for fmt in formats:
            token = secrets.token_urlsafe(24)
            selection, paired_audio = _selection(fmt, audios, link)
            selections[token] = selection
            group.append(_format_row(fmt, token, selection, paired_audio))
        rows.append(group)
    return rows[0], rows[1], selections


class DownloadCanceled(Exception):
    pass


def run_media(args, cancel):
    """Drain process pipes and support cancellation while FFmpeg runs."""
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, encoding='utf-8', errors='replace',
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)) as process:
        try:
            while True:
                if cancel.is_set():
                    raise DownloadCanceled('Download canceled.')
                try:
                    output, error = process.communicate(timeout=.25)
                    break
                except subprocess.TimeoutExpired:
                    pass
        except BaseException:
            process.kill()
            process.communicate()
            raise
        if process.returncode:
            raise RuntimeError(f'Media processing failed: {error.strip()[-1500:]}')
        return output


def combine_audio(video_path, audio_path, output_path, cancel):
    # Same role as the prototype's combine_audio, with no decoding/re-encoding.
    run_media([media_tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
               '-i', str(video_path), '-i', str(audio_path), '-map', '0:v:0', '-map', '1:a:0',
               '-c', 'copy', str(output_path)], cancel)


def verify_media(path, video, cancel):
    output = run_media([media_tool('ffprobe'), '-v', 'error', '-show_entries',
                        'stream=codec_type', '-of', 'json', str(path)], cancel)
    types = {s['codec_type'] for s in json.loads(output).get('streams', [])}
    if 'audio' not in types or video and 'video' not in types:
        raise RuntimeError('The finished file is missing an expected audio or video track.')
