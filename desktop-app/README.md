# S-Downloader Desktop

Windows desktop version of the existing React website, with its original dark theme, animated background, logo, search, video options and playlist screens. Downloads run locally with yt-dlp through a pywebview bridge; no Django server or deployed website is required.

## Use the app

Extract **S-Downloader-Windows-x64.zip**, keep the entire extracted folder together, then open **S-Downloader.exe**. Paste a YouTube HTTPS URL, choose a stream, and choose a destination folder. Progress, cancel, errors and the final file path appear in the app. Playlist entries open their individual download options.

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

The package is portable and unsigned; no installer or code-signing certificate is included. Sign release binaries with your publisher certificate before broad distribution. Review bundled dependency licenses. Update yt-dlp in `requirements.txt`, install it into the virtual environment, regenerate `requirements-lock.txt` with `pip freeze`, and rebuild when YouTube changes its extraction requirements.

## Validation

`python -m unittest discover -s tests -v` tests URL restrictions, playlist duration, stream selection, concurrent download rejection, completion and failure with deterministic extractor fixtures. A real download and the native folder picker must also be checked on a connected Windows desktop before publishing a release.
