import multiprocessing
import json
import subprocess
import sys
from pathlib import Path


def main():
    import webview
    from backend import DesktopApi
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    if len(sys.argv) == 3 and sys.argv[1] == '--self-test':
        # Exercise frozen imports and bundled resources without opening a window.
        import clr
        import yt_dlp_ejs
        from yt_dlp.version import __version__ as downloader_version
        from media import media_tool
        assert (root / 'ui' / 'index.html').is_file()
        assert (root / 'assets' / 'app.ico').is_file()
        assert (root / 'ui' / 'static' / 'downloader' / 'pictures' / 'Logo.png').is_file()
        version = subprocess.check_output([str(root / 'vendor' / 'node.exe'), '--version'],
                                          creationflags=subprocess.CREATE_NO_WINDOW, text=True).strip()
        assert DesktopApi().analyze('file:///test')['type'] == 'error'
        ffmpeg_version = subprocess.check_output([media_tool('ffmpeg'), '-version'],
                                                creationflags=subprocess.CREATE_NO_WINDOW, text=True).splitlines()[0]
        subprocess.check_output([media_tool('ffprobe'), '-version'],
                                creationflags=subprocess.CREATE_NO_WINDOW, text=True)
        Path(sys.argv[2]).write_text(json.dumps({'ok': True, 'node': version,
                                               'python': sys.version, 'frontend': True,
                                               'yt_dlp': downloader_version, 'ffmpeg': ffmpeg_version}), encoding='utf-8')
        return
    entry = root / 'ui' / 'index.html'
    if not entry.is_file():
        raise RuntimeError('Frontend is missing. Run the build script first.')
    api = DesktopApi()
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('SDownloader.Desktop')
    window = webview.create_window('S-Downloader', str(entry), js_api=api,
                                  width=1180, height=820, min_size=(760, 600),
                                  background_color='#0a0a0f', confirm_close=True)
    api._window = window
    window.events.closed += api.cancel_download
    # YouTube embeds need an HTTP page origin/referrer, including in the packaged app.
    webview.start(gui='edgechromium', debug=False, http_server=True,
                  icon=str(root / 'assets' / 'app.ico'))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
