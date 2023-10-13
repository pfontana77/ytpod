import os
import xml.etree.ElementTree as ET

def update_feed():
    print("Updating RSS feed...")
    
    # Create the root element and the channel
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'Limes Audio Podcast'
    ET.SubElement(channel, 'description').text = 'Limes Audio Podcast from YT'

    # Scan the 'output' folder for MP3 files
    print("Scanning 'output' folder for MP3 files...")
    for filename in os.listdir('output'):
        if filename.endswith('.mp3'):
            print(f"Found MP3 file: {filename}")
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = filename
            ET.SubElement(item, 'link').text = f'https://369b-5-170-140-75.ngrok-free.app:80/output/{filename}'
            ET.SubElement(item, 'description').text = f'Description of {filename}'

    # Save the modified RSS feed to a file
    print("Saving the modified RSS feed to 'feed.xml'...")
    tree = ET.ElementTree(rss)
    tree.write('feed.xml')

if __name__ == '__main__':
    update_feed()