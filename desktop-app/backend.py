"""Local download service; only server-issued stream IDs can be downloaded."""
import os
import shutil
import sys
import threading
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse

import yt_dlp
from media import ACTIVE_STATES, DownloadCanceled, combine_audio, format_choices, media_tool, verify_media

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


def validate_url(url):
    parsed = urlparse(url if isinstance(url, str) else '')
    if parsed.scheme != 'https' or parsed.hostname not in {
        'youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com', 'youtu.be'
    } or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Paste a valid HTTPS YouTube video or playlist link.')
    return url


def options():
    node = ROOT / 'vendor' / 'node.exe'
    runtime = str(node) if node.is_file() else shutil.which('node')
    result = {'quiet': True, 'no_warnings': True, 'noprogress': True, 'socket_timeout': 20,
              'retries': 3, 'windowsfilenames': True, 'cachedir': False}
    if runtime:
        result['js_runtimes'] = {'node': {'path': runtime}}
    return result


def extract_youtube_info(link):
    """Validate existence and reuse the metadata for the format list."""
    link = validate_url(link)
    # Format checks can fetch media samples even with download=False.
    metadata_options = options() | {
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'simulate': True,
        'check_formats': False,
    }
    with yt_dlp.YoutubeDL(metadata_options) as ydl:
        metadata = ydl.extract_info(link, download=False)
    if not metadata or not metadata.get('title'):
        raise ValueError('This YouTube video or playlist is unavailable.')
    return metadata


def is_valid_youtube_link(link: str) -> bool:
    try:
        extract_youtube_info(link)
        return True
    except Exception:
        return False


class DesktopApi:
    def __init__(self):
        self._window = None
        self._streams = {}
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._status = {'state': 'idle', 'progress': 0, 'message': ''}

    def analyze(self, link):
        try:
            metadata = extract_youtube_info(link)
            if metadata.get('_type') in ('playlist', 'multi_video'):
                videos = []
                for entry in metadata.get('entries') or []:
                    if not entry:
                        continue
                    url = entry.get('webpage_url') or entry.get('url')
                    try:
                        validate_url(url)
                    except (ValueError, TypeError):
                        continue
                    thumbnails = entry.get('thumbnails') or []
                    videos.append({'title': entry.get('title') or 'Video', 'watch_url': url,
                                   'thumbnail': entry.get('thumbnail') or (thumbnails[-1]['url'] if thumbnails else None),
                                   'length': entry.get('duration') or 0})
                return {'type': 'playlist', 'title': metadata.get('title'), 'videos': videos,
                        'length': int(sum(v['length'] for v in videos) // 60)}
            videos, audios, streams = format_choices(metadata, link)
            result = {'type': 'video', 'title': metadata.get('title'), 'thumbnail': metadata.get('thumbnail'),
                      'embed_id': f"https://www.youtube.com/embed/{quote(str(metadata['id']), safe='')}" if metadata.get('id') else None,
                      'resolutions': videos, 'audio': audios}
            with self._lock:
                self._streams = streams
            return result
        except Exception as exc:
            return {'type': 'error', 'message': str(exc)}

    def get_status(self):
        with self._lock:
            return dict(self._status)

    def start_download(self, stream_id):
        with self._lock:
            if self._status['state'] in ACTIVE_STATES:
                return {'error': 'A download is already running.'}
            selection = self._streams.get(stream_id)
            if not selection:
                return {'error': 'Analyze the video again before downloading.'}
            if selection['unavailable_reason']:
                return {'error': selection['unavailable_reason']}
            self._status = {'state': 'choosing', 'progress': 0, 'message': 'Choose a download folder…'}
        try:
            media_tool('ffmpeg')
            media_tool('ffprobe')
            import webview
            folders = self._window.create_file_dialog(webview.FileDialog.FOLDER)
            if not folders:
                self._set(state='idle', message='Download canceled.')
                return {'canceled': True}
            folder = Path(folders[0]).resolve()
            if not folder.is_dir():
                raise ValueError('The selected folder is unavailable.')
            self._cancel.clear()
            self._set(state='downloading', progress=0, message='Starting download…')
            threading.Thread(target=self._download, args=(dict(selection), folder), daemon=True).start()
            return {'ok': True}
        except Exception as exc:
            self._set(state='error', message=str(exc))
            return {'error': str(exc)}

    def cancel_download(self):
        self._cancel.set()
        return {'ok': True}

    def _set(self, **values):
        with self._lock:
            self._status.update(values)

    def _check_canceled(self):
        if self._cancel.is_set():
            raise DownloadCanceled('Download canceled.')

    def _download(self, selection, folder):
        try:
            media_tool('ffmpeg')
            media_tool('ffprobe')
            self._check_canceled()
            if selection.get('unavailable_reason'):
                raise ValueError(selection['unavailable_reason'])
            selected_ids = [i for i in (selection['video_id'], selection['audio_id']) if i]
            if not selected_ids:
                raise ValueError('No downloadable stream selected.')
            with tempfile.TemporaryDirectory(prefix='.sdownloader-', dir=folder) as temp:
                temp = Path(temp)
                paths = []
                for index, format_id in enumerate(selected_ids):
                    self._check_canceled()
                    track = 'video' if selection['video_id'] and index == 0 else 'audio'
                    self._set(state='downloading', message=f'Downloading {track}…')

                    def progress(data):
                        self._check_canceled()
                        total = data.get('total_bytes') or data.get('total_bytes_estimate') or 0
                        downloaded = data.get('downloaded_bytes') or 0
                        fraction = min(1, downloaded / total) if total else 0
                        if data['status'] == 'finished':
                            fraction = 1
                        self._set(progress=round(90 * (index + fraction) / len(selected_ids), 1),
                                  message=f'Downloading {track}: {downloaded / 1048576:.1f} MB')

                    finished = []
                    opts = options() | {'format': format_id, 'noplaylist': True,
                                        'ffmpeg_location': media_tool('ffmpeg'),
                                        'outtmpl': str(temp / '%(title).120B [%(id)s] [%(format_id)s].%(ext)s'),
                                        'progress_hooks': [progress], 'post_hooks': [finished.append]}
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(selection['link'], download=True)
                        path = Path(finished[-1] if finished else ydl.prepare_filename(info))
                    if not path.is_file() or not path.stat().st_size:
                        raise RuntimeError('The downloaded stream is empty or missing.')
                    paths.append(path)
                self._check_canceled()
                if len(paths) == 2:
                    output = temp / f'combined.{selection["container"]}'
                    self._set(state='merging', progress=95, message='Combining video and audio without re-encoding…')
                    combine_audio(paths[0], paths[1], output, self._cancel)
                else:
                    output = paths[0]
                self._set(state='verifying', progress=99, message='Checking the finished file…')
                verify_media(output, bool(selection['video_id']), self._cancel)
                self._check_canceled()
                filename = paths[0].with_suffix(output.suffix).name
                destination = folder / filename
                number = 1
                while True:
                    if destination.exists():
                        destination = folder / f'{Path(filename).stem} ({number}){Path(filename).suffix}'
                        number += 1
                        continue
                    try:
                        # Windows rename refuses to overwrite an existing destination.
                        os.rename(output, destination)
                        break
                    except FileExistsError:
                        continue
                self._set(state='complete', progress=100, message=f'Saved to {destination}')
        except Exception as exc:
            canceled = self._cancel.is_set() or isinstance(exc, DownloadCanceled)
            self._set(state='canceled' if canceled else 'error',
                      message='Download canceled. Temporary files removed.' if canceled else str(exc))
