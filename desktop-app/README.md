# S-Downloader Desktop

Windows desktop version of the existing React website, with its original dark theme, animated background, logo, search, video options and playlist screens. Downloads run locally with yt-dlp through a pywebview bridge; no Django server or deployed website is required.

## Use the app

Run **S-Downloader-Setup-1.0.1-x64.exe**. Choose an installation folder, optionally create a desktop shortcut, and finish the wizard. Setup requests administrator permission and installs for all users and adds an entry in Windows Settings > Apps for uninstalling. WebView2 is installed automatically if missing (internet required). The optional portable ZIP must be extracted with its complete folder intact. Paste a YouTube HTTPS URL to see the embedded video player and download options. Press Play to watch inside the app, with YouTube's playback controls and fullscreen support. Choose a stream and a destination folder to download. Progress, cancel, errors and the final file path appear in the app. Playlist entries open their individual player and download options. Playback requires internet and a video whose owner permits embedding.

Requires Windows 10 version 2004 or newer / Windows 11 x64, .NET Framework 4.8 or later, and Microsoft Edge WebView2 Runtime (https://developer.microsoft.com/en-us/microsoft-edge/webview2/). Python, Node, FFmpeg and ffprobe are bundled. Internet is needed for analysis, thumbnails and downloads. The interface itself is bundled locally. Video-only streams automatically download a compatible audio track and combine it into one file using FFmpeg stream copying, without re-encoding. MP4 prefers M4A audio; WebM prefers WebM audio. Other pairings use MKV to preserve the original codecs. Videos that already include audio download directly. A video with no available audio track is disabled. Temporary tracks are removed after completion, failure or cancellation. Bulk playlist downloads are not implemented. Closing the app asks for confirmation.

## Build on Windows

Install Python 3.12 x64 and Node.js 22+ first. From this directory:

```powershell
.\build.ps1 -Python py -Npm 'C:\Program Files\nodejs\npm.cmd' -FfmpegDir 'C:\ffmpeg\bin'
```

Supply a Windows x64 FFmpeg distribution containing ffmpeg.exe and ffprobe.exe in its bin directory and LICENSE in its parent directory. The -FfmpegDir argument is optional when vendor/ffmpeg already contains these files.

Use a Python 3.12 executable path instead of `py` if another version is the default. The script creates an isolated environment, installs dependencies, builds React, runs backend tests, bundles the app using PyInstaller, and produces `dist\S-Downloader-Windows-x64.zip`. The whole ZIP is the downloadable product; the EXE alone is insufficient.

For development after building:

```powershell
.\.venv\Scripts\python.exe main.py
```

Edit `frontend/src` and run `npm run build` inside `frontend` to refresh the interface. `backend.py` uses yt-dlp to fetch metadata and confirm that the link exists, reusing that result for the format list. Metadata requests disable downloads and media-sample probing; they still fetch YouTube metadata and manifests. `media.py` handles audio pairing, stream copying and final track verification. `backend.py` handles URL validation, extraction, opaque stream selections, folder selection, progress and cancellation. No website code or database is changed.

`assets/app.ico` is generated from the site's existing `Logo.png`, preserving the logo and transparency at 16, 24, 32, 48, 64, 128 and 256 pixels. The build embeds it in the Windows executable, and the native window uses the same icon.

The installer and portable package are unsigned. The installer avoids manually extracting blocked DLLs, but does not remove Windows SmartScreen or publisher warnings. A code-signing certificate is not included. Sign release binaries with your publisher certificate before broad distribution. Review bundled dependency licenses. Update yt-dlp in `requirements.txt`, install it into the virtual environment, regenerate `requirements-lock.txt` with `pip freeze`, and rebuild when YouTube changes its extraction requirements.

## Validation

`python -m unittest discover -s tests -v` runs 13 tests covering validation, format pairing, playlists, concurrent downloads, cleanup, cancellation and a real FFmpeg stream-copy check that compares encoded packet hashes.

For a live MP4 and WebM download check, run:

```powershell
.\.venv\Scripts\python.exe tests\live_media_check.py 'https://www.youtube.com/watch?v=KOwsVDogscY' build\audio-merge-live-check
```

This downloads two complete videos and writes a verification report. See VALIDATION.md for completed checks and remaining manual release checks.

## Build the installer

After building the app, install Inno Setup 6 and run:

```powershell
.\build-installer.ps1 -Version 1.0.1
```

Use `-Compiler 'C:\path\to\ISCC.exe'` if it is installed elsewhere. The script downloads the official WebView2 bootstrapper if absent, checks its Microsoft digital signature, and compiles `installer/S-Downloader.iss`. Output: `dist/S-Downloader-Setup-1.0.1-x64.exe` and its SHA256 file. Keep the installer AppId unchanged between versions so upgrades find the previous installation. The folder selection page remains available during upgrades. Both wizard artwork areas use the original S-Downloader logo, with its proportions preserved.

The default folder is the Windows Program Files directory (normally C:\Program Files\S-Downloader). Users can browse to another folder. Setup requires administrator permission and creates shortcuts for all users. Earlier per-user installations should be uninstalled before switching to this all-user installer. It checks .NET Framework 4.8 and provides an actionable error if missing. The supported Windows versions normally include it. Uninstall removes installed app files and shortcuts, leaving unrelated user files intact. It does not uninstall the shared WebView2 runtime.

For a disposable local installation/upgrade/uninstall check, run `tests/check-installer.ps1`. It refuses to run when an existing S-Downloader installation or shortcut is detected. A clean second-PC test remains necessary to validate missing-prerequisite and Windows reputation behavior.
