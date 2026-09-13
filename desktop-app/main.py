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
        assert (root / 'ui' / 'index.html').is_file()
        assert (root / 'ui' / 'static' / 'downloader' / 'pictures' / 'Logo.png').is_file()
        version = subprocess.check_output([str(root / 'vendor' / 'node.exe'), '--version'],
                                          creationflags=subprocess.CREATE_NO_WINDOW, text=True).strip()
        assert DesktopApi().analyze('file:///test')['type'] == 'error'
        Path(sys.argv[2]).write_text(json.dumps({'ok': True, 'node': version,
                                               'python': sys.version, 'frontend': True}), encoding='utf-8')
        return
    entry = root / 'ui' / 'index.html'
    if not entry.is_file():
        raise RuntimeError('Frontend is missing. Run the build script first.')
    api = DesktopApi()
    window = webview.create_window('S-Downloader', str(entry), js_api=api,
                                  width=1180, height=820, min_size=(760, 600),
                                  background_color='#0a0a0f', confirm_close=True)
    api._window = window
    window.events.closed += api.cancel_download
    webview.start(gui='edgechromium', debug=False)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
