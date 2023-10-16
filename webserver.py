from flask import Flask, send_from_directory
import download_episodes_from_channel as dec
import rss
import os

app = Flask(__name__)

def download_and_update():
    dec.download_episodes()  # Scarica gli episodi
    rss.update_feed()  # Aggiorna il feed RSS

@app.route('/<channel>/feed.xml')
def serve_feed(channel):
    return send_from_directory(os.path.join('output', channel), 'feed.xml')

@app.route('/<channel>/<filename>')
def serve_file(channel, filename):
    print(f"Serving file: {filename}")
    return send_from_directory(os.path.join('output', channel), filename, as_attachment=True, mimetype='audio/mp3')

if __name__ == '__main__':
    download_and_update()  # Chiama la funzione qui
    print("Starting Flask app on host='0.0.0.0', port=8080")
    app.run(host='0.0.0.0', port=8080)
