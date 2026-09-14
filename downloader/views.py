from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from pytubefix import YouTube, Playlist
from pytubefix.exceptions import VideoUnavailable, RegexMatchError
import yt_dlp
from pathlib import Path
from django.conf import settings
from django.http import Http404

def get_client_ip(request):
    """
    Returns the IP of the request, accounting for the possibility of being behind a proxy.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@ensure_csrf_cookie
def home(request):
    print(f"someone is opening the link from {get_client_ip(request)}")
    return render(request, "home.html")






def get_all_mp4(metadata):
    formats = metadata.get("formats", [])

    best_per_resolution = {}  # resolution -> best stream so far

    for f in formats:
        if f.get("ext") != "mp4":
            continue

        resolution = f.get("resolution")
        tbr = f.get("tbr") or 0  # total bitrate, higher = better quality

        if resolution not in best_per_resolution or tbr > (best_per_resolution[resolution].get("tbr") or 0):
            best_per_resolution[resolution] = f

    return list(best_per_resolution.values())

def get_all_mp4_with_audio(metadata):

    formats = metadata.get("formats", [])

    seen_resolutions = set()
    new_formats = []

    for f in formats:
        # Must be mp4, and must have BOTH video and audio codecs present
        is_mp4 = f.get("ext") == "mp4"
        has_video = f.get("vcodec") not in (None, "none")
        has_audio = f.get("acodec") not in (None, "none")

        resolution = f.get("resolution")

        if is_mp4 and has_video and has_audio and resolution not in seen_resolutions:
            seen_resolutions.add(resolution)
            new_formats.append(f)

    return new_formats

def get_all_audio(metadata):
    formats = metadata.get("formats", [])

    seen = set()
    audio_formats = []

    for f in formats:
        # Audio-only streams: has audio codec but no video codec
        has_audio = f.get("acodec") not in (None, "none")
        is_audio_only = f.get("vcodec") in (None, "none")
        isnt_webm = f.get("ext") != "webm"
        abr = f.get("abr")  # audio bitrate
        ext = f.get("ext")

        key = (ext, abr)

        if has_audio and is_audio_only and isnt_webm and key not in seen:
            seen.add(key)
            audio_formats.append(f)

    return audio_formats





def show_download_options(request):
    def is_valid_youtube_url(url):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'extract_flat': False,
            'youtube_include_dash_manifest': False,  # <-- skips fetching DASH manifest (big speedup)
            'nocheckcertificate': True,
            'socket_timeout': 10,
            'extractor_args': {
                'youtube': {
                    'skip': ['hls', 'dash'],  # <-- skips HLS and DASH formats (only fetches direct streams)
                }
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                metadata = ydl.extract_info(url, download=False)
                return {"valid": True, "reason": None} , metadata
        except yt_dlp.utils.DownloadError as e:
            reason = str(e)
            if "not available" in reason:
                return {"valid": False, "reason": "Video is not available in your region or has been removed"}
            elif "private" in reason:
                return {"valid": False, "reason": "Video is private"}
            elif "age" in reason:
                return {"valid": False, "reason": "Video is age-restricted"}
            else:
                return {"valid": False, "reason": "Invalid or inaccessible URL"}
    link = request.POST.get("link")

    if not link:
        return JsonResponse({"type": "error", "message": "No link provided"}, status=400)

    try:
        result , metadata= is_valid_youtube_url(link)
        if result["valid"]:
            if "playlist" in link:
                print("playlist detected")
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'extract_flat': True,  # only fetches metadata, doesn't resolve each video (big speedup)
                    'youtube_include_dash_manifest': False,
                    'nocheckcertificate': True,
                    'socket_timeout': 10,
                }

                # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                #     metadata = ydl.extract_info(link, download=False)

                vids = []
                length = 0

                for vid in metadata.get("entries", []):
                    duration = vid.get("duration") or 0
                    length += int(duration)
                    vids.append({
                        "title": vid.get("title"),
                        "watch_url": vid.get('original_url'),
                        "thumbnail": vid.get("thumbnail"),
                        "length": duration,
                    })

                    length = length // 60
                return JsonResponse({
                    "type": "playlist",
                    "title": metadata.get("title", "Playlist"),
                    "length": length,
                    "videos": vids,
                })
            else:
                print("video detected")



                videos = get_all_mp4(metadata)
                audios = get_all_audio(metadata)
                video_options = []
                for stream in videos:
                    is_progressive = stream.get("acodec") not in (None, "none")
                    video_options.append({
                        "resolution": stream.get("format_note"),
                        "url": stream.get("url"),
                        "is_progressive": is_progressive,
                        "filesize": stream.get("filesize"),
                    })
                # lv = []
                # lresolutions = []
                # yt = YouTube(link , client="WEB_EMBED")
                # resolutionsvid = yt.streams.order_by('resolution').filter(mime_type='video/mp4')
                # audio_tracks = yt.streams.get_default_audio_track()
                #
                # for j in resolutionsvid:
                #     if j.is_progressive:
                #         lv.append(j)
                #         lresolutions.append(j.resolution)
                #     elif "av01" in j.video_codec:
                #         if j.resolution not in lresolutions:
                #             lv.append(j)
                #
                # # Serialize video streams to plain dicts
                # video_options = []
                # for stream in lv:
                #     video_options.append({
                #         "resolution": stream.resolution,
                #         "url": stream.url,
                #         "is_progressive": stream.is_progressive,
                #         "filesize": stream.filesize,
                #     })
                #
                # Serialize audio streams to plain dicts
                audio_options = []
                if audios:
                    try:
                        for stream in audios:
                            audio_options.append({
                                "abr": stream.get("abr"),
                                "url": stream.get("url"),
                                "filesize": stream.get("filesize"),
                            })
                    except TypeError:
                        # Single stream object, not iterable
                        audio_options.append({
                            "abr": audios.get("abr"),
                            "url": audios.get("url"),
                            "filesize": audios.get("filesize"),
                        })


                title = metadata.get("title")
                thumbnail = metadata.get("thumbnail")
                return JsonResponse({
                    "type": "video",
                    "embed_id" : f"https://www.youtube.com/embed/{ metadata.get("id")}",
                    "title": title,
                    "thumbnail": thumbnail,
                    "resolutions": video_options,
                    "audio": audio_options,
                })



            #--------------------------------> pytube version
        # elif "playlist" in link:
        #     print("playlist detected")
        #     vids = []
        #     length = 0
        #     p = Playlist(link)
        #     for vid in p.videos:
        #         vids.append({
        #             "title": vid.title,
        #             "watch_url": vid.watch_url,
        #             "thumbnail": vid.thumbnail_url,
        #             "length": vid.length,
        #         })
        #         length += int(vid.length)
        #     length = length // 60
        #
        #     return JsonResponse({
        #         "type": "playlist",
        #         "title": p.title if hasattr(p, 'title') else "Playlist",
        #         "length": length,
        #         "videos": vids,
        #     })
        else:
            return JsonResponse({"type": "error", "message": result["reason"]}, status=400)

    except Exception as e:
        print(f"Error processing link: {e}")
        return JsonResponse({"type": "error", "message": "Failed to process the link. Please try again."}, status=500)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Sitemap: https://sdownloader.duckdns.org/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def download(request):
    stream = request.POST.get("stream")
    return redirect(stream.url)


def download_app(request):
    archive = Path(settings.BASE_DIR) / 'desktop-app' / 'dist' / 'S-Downloader-Windows-x64.zip'
    try:
        archive_file = archive.open('rb')
    except FileNotFoundError:
        raise Http404('The Windows app download is not available yet.') from None
    response = FileResponse(archive_file, as_attachment=True,
                            filename=archive.name, content_type='application/zip')
    response['Cache-Control'] = 'no-cache'
    return response