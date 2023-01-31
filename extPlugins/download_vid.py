from yt_dlp import YoutubeDL


def length_filter(info, *, incomplete):
    """Download only videos shorter than x seconds, or known duration"""
    duration = info.get('duration')
    # print("\n\nDuration is {}\n\n".format(duration))

    if duration and (duration >= 601 or duration < 60): 
        '''Videos longer than 8:21 [Mirrors - Justin Timberlake] or shorter than 1:00
        [Yugi-Oh 5D's Opening 5] are not downloaded'''    
        return 'Invalid file duration'

# def bitrate_setter(info, *, incomplete):
#     duration = info.get('duration')
#     if duration and duration > 270:
#         bitrate = 128

def my_hook(d):
    if d['status'] == 'finished':
        print('\nDone downloading, now converting ...\n')

# def hook2(d):
#     if d['status'] == 'finished':
#         print('\nDone converting and embedding, now playing ...\n')

async def downloadVideo(URL: str, duration:int = None) -> int | str: 
    # print("Duration is", duration)
    
    
    if duration and duration > 270 and duration < 450: #UNCOMMENT THIS
        bitrate = 128
    elif duration and duration > 450:
        bitrate = 108    
    else:
        bitrate = 192
    # bitrate = 192

    # print("Bitrate", bitrate)
    # ℹ️ See help(yt_dlp.YoutubeDL) for a list of available options and public functions
    ydl_opts = {
        # 'ffmpeg_location': 'C:\\ffmpeg',
        # 'verbose': True,
        # 'postprocessor_args':'EmbedThumbnail',
        
        # 'keepvideo': True,
        'ignoreerrors': True, 
        'audio_quality': 0,
        'format': 'm4a/bestaudio/best', #MAKE IT BESTAUDIO/BEST
        'noplaylist': True,
        'extractor_retries': 2,
        'windowsfilenames': True,
        'match_filter': length_filter,
        # 'writethumbnail': True,
        # 'skip_download': True, # MAKE NOTICE OF THIS
        'progress_hooks': [my_hook],
        # 'postprocessor_hooks': [hook2],
        'outtmpl': './videos/%(title)s.%(ext)s'
        # ,
        # 'postprocessors': [
        # {  # Extract audio using ffmpeg
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': bitrate,
        # },
        # { #Embedding thumbnail using ffmpeg and AtomicParsley
        #     'key': 'EmbedThumbnail',
        # },
        # ]
    }
    
    
 

    with YoutubeDL(ydl_opts) as ydl:

        error_code = ydl.download(URL)
        print(error_code)

if __name__ == "__main__":
    import asyncio
    asyncio.run(downloadVideo("https://www.youtube.com/watch?v=1dNkQoE76nY"))
    