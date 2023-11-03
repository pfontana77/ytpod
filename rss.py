import os
import xml.etree.ElementTree as ET

# Base URL for the podcast links
BASE_URL = "http://localhost:8080/"


def update_feed():
    print("Updating RSS feeds...")

    # Scan the 'output' folder for channel directories
    for channel_name in os.listdir("output"):
        channel_dir = os.path.join("output", channel_name)
        if os.path.isdir(channel_dir):
            print(f"Processing channel: {channel_name}")

            # Create the root element and the channel
            rss = ET.Element("rss", version="2.0")
            channel = ET.SubElement(rss, "channel")
            ET.SubElement(channel, "title").text = f"{channel_name} Audio Podcast"
            ET.SubElement(
                channel, "description"
            ).text = f"{channel_name} Audio Podcast from YT"

            # Scan the channel directory for MP3 files
            print(f"Scanning '{channel_dir}' folder for MP3 files...")
            for filename in os.listdir(channel_dir):
                if filename.endswith(".mp3"):
                    print(f"Found MP3 file: {filename}")
                    item = ET.SubElement(channel, "item")
                    ET.SubElement(item, "title").text = filename
                    # Utilizza la costante BASE_URL quando costruisci l'URL
                    ET.SubElement(
                        item, "link"
                    ).text = f"{BASE_URL}{channel_name}/{filename}"
                    ET.SubElement(
                        item, "description"
                    ).text = f"Description of {filename}"

            # Save the modified RSS feed to a file
            rss_file_path = os.path.join(channel_dir, "feed.xml")
            print(f"Saving the modified RSS feed to '{rss_file_path}'...")
            tree = ET.ElementTree(rss)
            tree.write(rss_file_path)


if __name__ == "__main__":
    update_feed()
