# Validation performed

- Application icon: all 7 icon images embedded in the rebuilt Windows executable match `assets/app.ico` byte-for-byte. The icon is converted from the original website logo. The frozen runtime self-test also verifies the bundled icon exists.

- React production build: passed (Vite 6.4.3).
- Backend unit tests: all 7 passed.
- Frozen Windows executable self-test: passed; verified Python/.NET imports, bundled HTML/logo, input validation and bundled Node v24.14.0 execution. Result: `dist/self-test.json`.
- Live YouTube analysis: passed for the public video `jNQXAC9IVRw`, returning 3 video stream options and 2 audio options.
- Windows x64 portable ZIP: generated successfully.
- Embedded playback update: production frontend build and all 7 backend tests passed, including the embed URL response. A live visible WebView2 check rendered the React video screen and confirmed YouTube player state `1` (playing) for `jNQXAC9IVRw`. Result: `dist/playback-check.json`. The initial hidden-window run buffered; the visible-window run played successfully.
- Download 403 fix: reproduced HTTP 403 with yt-dlp 2026.3.17 on `KOwsVDogscY` format 18. Updated to yt-dlp 2026.8.19; the old combined format is no longer offered. Completed full downloads of the current 360p video-only format 134 (10,231,469 bytes) and M4A audio format 140 (6,229,078 bytes) for the same user-supplied link. All 7 backend tests still pass. Re-analyze links in the new application to use current format choices.

Not verified: folder picker interaction, cancellation during a real transfer, fullscreen interaction, or operation on a clean second PC. Perform these release checks before publicly distributing the unsigned portable build.

## Automatic audio merging update

- Keeps yt-dlp for validation, extraction and downloads; no pytubefix or MoviePy dependency.
- All 11 current tests passed, including real H264/AAC packet-hash comparison before and after stream copying.
- React production build passed.
- Live user-supplied video KOwsVDogscY returned 34 video options, all with audio available.
- Full format 134 download: MP4, 10,885,255 bytes, H264 video + AAC audio, 385.103 seconds.
- Full format 243 download: WebM, 15,380,406 bytes, VP9 video + Opus audio, 385.061 seconds.
- ffprobe verified both tracks in both outputs. No temporary download directories remained. Report: build/audio-merge-live-check/verification.json.
- Cancellation and failure cleanup verified with deterministic tests; real network cancellation and operation on a clean second PC remain manual checks.
- Rebuilt Windows executable self-test passed with bundled yt-dlp 2026.08.19, Node v24.14.0 and FFmpeg/ffprobe 8.1.2.

## Media cleanup and metadata-only analysis

- Refactored format selection and UI serialization into separate pure helpers, with a shared size calculation and container value.
- Explicitly disabled yt-dlp format probing during metadata extraction; download=False, skip_download and simulate remain enabled for analysis only.
- All 13 tests passed, including real yt-dlp selection of a format marked __needs_testing with media network requests, downloads and FFmpeg calls guarded against. No live media downloads were used for this update.

## Windows installer

- Inno Setup 6.7.3 compiles a per-user Windows setup wizard with an always-visible directory chooser, optional desktop shortcut, Start menu entry, launch option and uninstaller.
- The bundled official WebView2 bootstrapper has a verified Microsoft Authenticode signature. Setup detects existing WebView2 and only invokes the bootstrapper when needed. .NET Framework 4.8 is checked before installation.
- Installed into a custom folder containing spaces; installed app self-test passed (Python/.NET, frontend, Node, FFmpeg and ffprobe).
- Confirmed installed Python.Runtime.dll has no Zone.Identifier stream.
- Reinstalled successfully as an upgrade, then uninstalled. App executable, shortcut and uninstall registry entry were removed; an unrelated user file was preserved.
- Not tested on a clean second PC: missing-WebView2 download/install, missing-.NET messaging, SmartScreen behavior. The installer is unsigned.

## Installer branding and Program Files default

- Version 1.0.1 replaces the default welcome and header artwork with the original logo and preserves its aspect ratio.
- Uses the Windows Program Files directory by default, administrator privileges, all-user shortcuts and machine-wide WebView2 detection. Folder selection remains enabled.
- Version 1.0.1 compiled successfully. Administrator-level installation test was not run because execution approval was declined; the previous per-user installer lifecycle test does not verify this new scope.
