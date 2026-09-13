import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend import DesktopApi, validate_url


class FakeYDL:
    metadata = {}
    def __init__(self, opts): self.opts = opts
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def extract_info(self, *args, **kwargs): return self.metadata
    def prepare_filename(self, info): return 'saved.mp4'


class BackendTests(unittest.TestCase):
    def test_only_https_youtube(self):
        for url in ['file:///etc/passwd', 'http://youtube.com/watch?v=x',
                    'https://youtube.com.evil.example/x', 'https://127.0.0.1',
                    'https://user@youtube.com/x', 'https://youtube.com:8443/x']:
            with self.assertRaises(ValueError): validate_url(url)
        self.assertEqual(validate_url('https://youtu.be/abc'), 'https://youtu.be/abc')

    @patch('backend.yt_dlp.YoutubeDL', FakeYDL)
    def test_formats_preserve_audio_and_hide_raw_urls(self):
        base = {'ext': 'mp4', 'height': 720, 'vcodec': 'avc', 'protocol': 'https', 'url': 'https://cdn.example/video'}
        FakeYDL.metadata = {'title': 'Test', 'formats': [
            base | {'format_id': '1', 'acodec': 'none', 'tbr': 20},
            base | {'format_id': '2', 'acodec': 'aac', 'tbr': 10},
            base | {'format_id': '3', 'acodec': 'none', 'tbr': 30}]}
        api = DesktopApi()
        result = api.analyze('https://youtu.be/abc')
        self.assertEqual(result['type'], 'video')
        self.assertEqual(len(result['resolutions']), 2)
        self.assertEqual({s['is_progressive'] for s in result['resolutions']}, {True, False})
        self.assertNotIn('url', result['resolutions'][0])
        self.assertEqual({v[1] for v in api._streams.values()}, {'2', '3'})

    @patch('backend.yt_dlp.YoutubeDL', FakeYDL)
    def test_playlist_duration_and_unavailable_entries(self):
        FakeYDL.metadata = {'_type': 'playlist', 'entries': [None,
            {'url': 'https://youtu.be/a', 'duration': 90},
            {'url': 'https://youtu.be/b', 'duration': 90}]}
        result = DesktopApi().analyze('https://www.youtube.com/playlist?list=abc')
        self.assertEqual(result['length'], 3)
        self.assertEqual(len(result['videos']), 2)

    def test_unknown_stream_rejected(self):
        self.assertIn('error', DesktopApi().start_download('invented-id'))

    def test_duplicate_download_rejected(self):
        api = DesktopApi()
        api._status['state'] = 'downloading'
        self.assertIn('error', api.start_download('id'))

    @patch('backend.yt_dlp.YoutubeDL', side_effect=RuntimeError('Network unavailable'))
    def test_download_failure_is_reported(self, mock):
        api = DesktopApi()
        with tempfile.TemporaryDirectory() as folder:
            api._download('https://youtu.be/a', '1', Path(folder))
        self.assertEqual(api.get_status()['state'], 'error')
        self.assertIn('Network unavailable', api.get_status()['message'])

    @patch('backend.yt_dlp.YoutubeDL', FakeYDL)
    def test_download_completion(self):
        api = DesktopApi()
        with tempfile.TemporaryDirectory() as folder:
            api._download('https://youtu.be/a', '1', Path(folder))
        self.assertEqual(api.get_status()['state'], 'complete')


if __name__ == '__main__': unittest.main()
