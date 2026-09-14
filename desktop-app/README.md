# S-Downloader Desktop

Windows desktop version of the existing React website, with its original dark theme, animated background, logo, search, video options and playlist screens. Downloads run locally with yt-dlp through a pywebview bridge; no Django server or deployed website is required.

## Use the app

Extract **S-Downloader-Windows-x64.zip**, keep the entire extracted folder together, then open **S-Downloader.exe**. Paste a YouTube HTTPS URL to see the embedded video player and download options. Press Play to watch inside the app, with YouTube's playback controls and fullscreen support. Choose a stream and a destination folder to download. Progress, cancel, errors and the final file path appear in the app. Playlist entries open their individual player and download options. Playback requires internet and a video whose owner permits embedding.

Requires Windows 10/11 x64 and Microsoft Edge WebView2 Runtime (https://developer.microsoft.com/en-us/microsoft-edge/webview2/). Python and Node are bundled. Internet is needed for analysis, thumbnails and downloads. The interface itself is bundled locally. Streams marked **No Audio** save video only, matching the website; automatic merging/conversion and bulk playlist downloads are not implemented. Partial downloads are retained for retry/resume. Closing the app asks for confirmation.

## Build on Windows

Install Python 3.12 x64 and Node.js 22+ first. From this directory:

```powershell
.\build.ps1 -Python py -Npm 'C:\Program Files\nodejs\npm.cmd'
```

Use a Python 3.12 executable path instead of `py` if another version is the default. The script creates an isolated environment, installs dependencies, builds React, runs backend tests, bundles the app using PyInstaller, and produces `dist\S-Downloader-Windows-x64.zip`. The whole ZIP is the downloadable product; the EXE alone is insufficient.

For development after building:

```powershell
.\.venv\Scripts\python.exe main.py
```

Edit `frontend/src` and run `npm run build` inside `frontend` to refresh the interface. `backend.py` handles URL validation, extraction, opaque stream selections, folder selection, progress and cancellation. No website code or database is changed.

`assets/app.ico` is generated from the site's existing `Logo.png`, preserving the logo and transparency at 16, 24, 32, 48, 64, 128 and 256 pixels. The build embeds it in the Windows executable, and the native window uses the same icon.

The package is portable and unsigned; no installer or code-signing certificate is included. Sign release binaries with your publisher certificate before broad distribution. Review bundled dependency licenses. Update yt-dlp in `requirements.txt`, install it into the virtual environment, regenerate `requirements-lock.txt` with `pip freeze`, and rebuild when YouTube changes its extraction requirements.

## Validation

`python -m unittest discover -s tests -v` tests URL restrictions, playlist duration, stream selection, concurrent download rejection, completion and failure with deterministic extractor fixtures. A real download and the native folder picker must also be checked on a connected Windows desktop before publishing a release.

For an optional live embedded-player check, run `.\.venv\Scripts\python.exe tests\playback_probe.py --visible`. This opens a temporary WebView2 window, plays a public sample video muted, writes `dist/playback-check.json`, and closes the window. It uses the built React interface with fixture video metadata.
