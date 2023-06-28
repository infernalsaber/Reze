"""The extension of the plugin to download a youtube video's audio"""
from yt_dlp import YoutubeDL


def length_filter(info, *, incomplete):
    """Download only videos shorter than x seconds, or known duration"""
    duration = info.get("duration")

    if duration and (duration >= 601 or duration < 60):
        # Videos longer than 8:21 [Mirrors - Justin Timberlake] or shorter than 1:00
        # [Yugi-Oh 5D's Opening 5] are not downloaded
        return "Invalid file duration"


def my_hook(download):
    """Status of the downloading process"""
    if download["status"] == "finished":
        print("\nDone downloading, now converting ...\n")


# def hook2(d):
#     if d['status'] == 'finished':
#         print('\nDone converting and embedding, now playing ...\n')


async def download_video(url: str, duration: int = None) -> int | str:
    """Download the video"""
    # print("Duration is", duration)

    if duration and 270 < duration < 450:  # UNCOMMENT THIS
        bitrate = 128
    elif duration and duration > 450:
        bitrate = 108
    else:
        bitrate = 192

    ydl_opts = {
        # 'verbose': True,
        # 'postprocessor_args':'EmbedThumbnail',
        # 'keepvideo': True,
        "ignoreerrors": True,
        "audio_quality": 0,
        "format": "m4a/bestaudio/best",  # MAKE IT BESTAUDIO/BEST
        "noplaylist": True,
        "extractor_retries": 2,
        "windowsfilenames": True,
        "match_filter": length_filter,
        # 'writethumbnail': True,
        # 'skip_download': True, # MAKE NOTICE OF THIS
        "progress_hooks": [my_hook],
        # 'postprocessor_hooks': [hook2],
        "outtmpl": "./videos/%(title)s.%(ext)s",
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            },
            {  # Embedding thumbnail using ffmpeg and AtomicParsley
                "key": "EmbedThumbnail",
            },
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)
        print(error_code)
