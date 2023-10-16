import yt_dlp

def download_episodes():
    # Legge gli URL dei canali dal file di configurazione
    with open('channel_lists.cfg', 'r') as file:
        channels = [line.strip() for line in file]

    ydl_opts = {
        "format": "bestaudio",
        "extractaudio": True,
        "audioformat": "bestaudio",
        "outtmpl": "output/%(uploader)s/%(title)s.%(ext)s",
        "ignoreerrors": True,
        "verbose": True,
        "playlistend": 5,
        "noplaylist": True,
        "download_archive": "downloaded.txt",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    for channel_url in channels:
        try:
            print(f"Starting download for channel: {channel_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([channel_url])
            print("Download completed for channel: {channel_url}")
        except yt_dlp.utils.DownloadError as e:
            print(f"Download completed or reached the maximum limit for channel: {channel_url}")

if __name__ == "__main__":
    print("Executing main script...")
    download_episodes()