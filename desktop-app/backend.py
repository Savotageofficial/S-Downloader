"""Local download service; only server-issued stream IDs can be downloaded."""
import secrets
import shutil
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

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
    result = {'quiet': True, 'no_warnings': True, 'socket_timeout': 20,
              'retries': 3, 'windowsfilenames': True, 'cachedir': False}
    if runtime:
        result['js_runtimes'] = {'node': {'path': runtime}}
    return result


class DesktopApi:
    def __init__(self):
        self._window = None
        self._streams = {}
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._status = {'state': 'idle', 'progress': 0, 'message': ''}

    def analyze(self, link):
        try:
            link = validate_url(link)
            opts = options() | {'extract_flat': 'in_playlist', 'skip_download': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                metadata = ydl.extract_info(link, download=False)
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
            video, audio, streams = {}, {}, {}
            for fmt in metadata.get('formats') or []:
                has_video = fmt.get('vcodec') not in (None, 'none')
                has_audio = fmt.get('acodec') not in (None, 'none')
                if fmt.get('has_drm') or not fmt.get('format_id'):
                    continue
                # Direct streams need no external muxer and preserve the website's No Audio label.
                if fmt.get('protocol') not in ('https', 'http'):
                    continue
                if has_video and fmt.get('ext') == 'mp4':
                    key = (fmt.get('height'), has_audio)
                    if key not in video or (fmt.get('tbr') or 0) > (video[key].get('tbr') or 0):
                        video[key] = fmt
                elif has_audio and not has_video and fmt.get('ext') != 'webm':
                    audio[(fmt.get('ext'), fmt.get('abr'))] = fmt

            def serialize(fmt):
                token = secrets.token_urlsafe(24)
                streams[token] = (link, fmt['format_id'])
                return {'id': token, 'resolution': fmt.get('format_note') or f"{fmt.get('height', '?')}p",
                        'is_progressive': fmt.get('acodec') not in (None, 'none'),
                        'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                        'abr': f"{round(fmt.get('abr') or 0)} kbps ({fmt.get('ext')})"}

            result = {'type': 'video', 'title': metadata.get('title'), 'thumbnail': metadata.get('thumbnail'),
                      'resolutions': [serialize(f) for f in sorted(video.values(), key=lambda f: f.get('height') or 0, reverse=True)],
                      'audio': [serialize(f) for f in audio.values()]}
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
            if self._status['state'] in ('choosing', 'downloading'):
                return {'error': 'A download is already running.'}
            selection = self._streams.get(stream_id)
            if not selection:
                return {'error': 'Analyze the video again before downloading.'}
            self._status = {'state': 'choosing', 'progress': 0, 'message': 'Choose a download folder…'}
        try:
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
            threading.Thread(target=self._download, args=(*selection, folder), daemon=True).start()
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

    def _download(self, link, format_id, folder):
        def progress(data):
            if self._cancel.is_set():
                raise RuntimeError('Download canceled.')
            total = data.get('total_bytes') or data.get('total_bytes_estimate') or 0
            downloaded = data.get('downloaded_bytes') or 0
            self._set(progress=min(100, round(downloaded / total * 100, 1)) if total else 0,
                      message='Saving file…' if data['status'] == 'finished' else f'Downloaded {downloaded / 1048576:.1f} MB')
        try:
            opts = options() | {'format': format_id, 'noplaylist': True, 'overwrites': False,
                                'outtmpl': str(folder / '%(title).150B [%(id)s] [%(format_id)s].%(ext)s'),
                                'progress_hooks': [progress]}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
            if self._cancel.is_set():
                self._set(state='canceled', message='Download canceled. Partial files can resume on retry.')
            else:
                self._set(state='complete', progress=100, message=f'Saved to {filename}')
        except Exception as exc:
            self._set(state='canceled' if self._cancel.is_set() else 'error',
                      message='Download canceled. Partial files can resume on retry.' if self._cancel.is_set() else str(exc))
