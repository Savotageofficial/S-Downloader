# S-Downloader


<img alt="S-Downloader Banner" src="S-Downloader-Banner.png" title="Banner" />


**S-Downloader** is a free, web-based YouTube video and playlist downloader built with Django. It lets users paste a YouTube URL and download videos (or entire playlists) quickly and securely, without needing any extra software.

🔗 Live demo: [s-downloader-test.vercel.app](https://s-downloader-test.vercel.app/)

## Features

- Download single YouTube videos
- Download full YouTube playlists
- Fast, simple, and free — just paste a link and go
- Clean, minimal web interface
- Deployed serverlessly on Vercel

## Tech Stack

- **Backend:** [Django](https://www.djangoproject.com/) 6.0
- **Downloading engine:** [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [pytubefix](https://github.com/JuanBindez/pytubefix)
- **Static file serving:** [WhiteNoise](http://whitenoise.evans.io/)
- **Frontend:** HTML/CSS/JS templates (`templates/`, `static/`, `frontend/`)
- **Deployment:** [Vercel](https://vercel.com/) (serverless, see `vercel.json`)
- **Dependency management:** [Pipenv](https://pipenv.pypa.io/) (`Pipfile` / `Pipfile.lock`)

## Project Structure

```
S-Downloader/
├── downloader/         # Main Django app (views, URLs, download logic)
├── frontend/            # Frontend assets/source
├── static/              # Static source files
├── staticfiles/         # Collected static files (for deployment)
├── templates/            # HTML templates
├── manage.py             # Django management script
├── Pipfile / Pipfile.lock # Python dependencies (Pipenv)
├── requirements.txt       # Python dependencies (pip)
├── vercel.json            # Vercel deployment configuration
└── db.sqlite3              # Local SQLite database
```

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` or [Pipenv](https://pipenv.pypa.io/)
- `ffmpeg` installed and available on your `PATH` (required by `yt-dlp` for merging/converting media)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Savotageofficial/S-Downloader.git
   cd S-Downloader
   ```

2. Install dependencies:

   Using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

   Or using `pipenv`:
   ```bash
   pipenv install
   pipenv shell
   ```

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Open your browser at `http://127.0.0.1:8000/`.

## Usage

1. Open the app in your browser.
2. Paste a YouTube video or playlist URL into the input field.
3. Choose your desired format/quality (if available).
4. Click download and let S-Downloader fetch the media for you.

## Deployment

This project is configured for one-click deployment on [Vercel](https://vercel.com/) via `vercel.json`. Push to your connected repository or run:

```bash
vercel --prod
```

WhiteNoise handles static file serving in production, so no separate static file host is required.

## Disclaimer

This tool is intended for downloading content you have the right to download (e.g. your own videos, Creative Commons content, or content where the copyright holder has given permission). Please respect YouTube's Terms of Service and applicable copyright laws in your jurisdiction when using this tool.

## License

No license has been specified for this project yet. Consider adding one (e.g. MIT) if you plan to accept contributions or allow reuse.

## Author

**Safwat** ([@Savotageofficial](https://github.com/Savotageofficial))
