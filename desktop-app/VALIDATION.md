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
