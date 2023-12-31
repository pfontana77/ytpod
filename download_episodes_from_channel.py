import yt_dlp
import csv
from subtitles import process_output_folder
from create_audio import create_audio_from_folder
import rss
import logging
import os

# Ottieni una referenza al logger 'app_logger'
app_logger = logging.getLogger("app_logger")


def download_episodes():
    output_folder = "output"
    # Legge gli URL dei canali e gli indicatori dal file di configurazione
    with open("channel_lists.cfg", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        channels = [(row[0], int(row[1])) for row in reader if row]

    for channel_url, download_audio in channels:
        # Estrai il nome del canale dal URL
        channel_name = channel_url.split("@")[-1].split("/")[0]
        # Crea il percorso della cartella di output usando il nome del canale
        channel_output_folder = os.path.join(output_folder, channel_name)

        if download_audio:
            ydl_opts = {
                "format": "bestaudio",
                "extractaudio": True,
                "audioformat": "mp3",
                "outtmpl": os.path.join(channel_output_folder, "%(title)s.%(ext)s"),
                "ignoreerrors": True,
                "verbose": True,
                "playlistend": 5,
                "noplaylist": True,
                "download_archive": "downloaded.txt",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        else:
            ydl_opts = {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "skip_download": True,
                "subtitleslangs": ["en"],
                "playlistend": 5,
                "noplaylist": True,
                "download_archive": "downloaded.txt",
                "outtmpl": os.path.join(channel_output_folder, "%(title)s.%(ext)s"),
            }

        try:
            app_logger.info(
                f"Starting {( 'download' if download_audio else 'subtitle extraction' )} for channel: {channel_url}"
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([channel_url])
            app_logger.info(
                f"{('Download' if download_audio else 'Subtitle extraction')} completed for channel: {channel_url}"
            )
            process_output_folder(output_folder)
            create_audio_from_folder(output_folder)
            rss.update_feed()
        except yt_dlp.utils.DownloadError as e:
            app_logger.info(
                f"{('Download' if download_audio else 'Subtitle extraction')} completed or reached the maximum limit for channel: {channel_url}"
            )


if __name__ == "__main__":
    output_folder = "output"
    app_logger.info("Executing download_episodes...")
    download_episodes()

