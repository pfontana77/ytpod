import yt_dlp

def download_episodes():
    CHANNEL_URL = "https://www.youtube.com/channel/UCgG9BnqkGnU-ouYa5eAOdEw"

    ydl_opts = {
        "format": "bestaudio",
        "extractaudio": True,
        "audioformat": "bestaudio",
        "outtmpl": "output/%(title)s.%(ext)s",
        "ignoreerrors": True,
        "verbose": True,
        #"max_downloads": 5,
        #"noplaylist": True,
        "playlistend": 5,
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        print("Starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([CHANNEL_URL])
        print("Download completed")
    except yt_dlp.utils.DownloadError as e:
        print("Download completed or reached the maximum limit")

# Call the function
if __name__ == "__main__":
    print("Executing main script...")
    download_episodes()