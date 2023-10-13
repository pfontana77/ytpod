from flask import Flask, send_from_directory
import download_episodes_from_channel as dec
import rss
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime

app = Flask(__name__)

def scheduled_task():
    dec.download_episodes()  # Scarica gli episodi
    rss.update_feed()  # Aggiorna il feed RSS

@app.route('/feed.xml')
def serve_feed():
    return send_from_directory('.', 'feed.xml')

@app.route('/output/<filename>')
def serve_file(filename):
    print(f"Serving file: {filename}")
    return send_from_directory('output', filename, as_attachment=True, mimetype='audio/mp3')

if __name__ == '__main__':
    # Inizializza lo scheduler in background
    scheduler = BackgroundScheduler()

    # Calcola il tempo attuale
    now = datetime.datetime.now()
    print(f"Current time: {now}")

    # Calcola la prima esecuzione alle 23:50
    first_run = datetime.datetime(now.year, now.month, now.day, 23, 50)
    print(f"First run time: {first_run}")

    # Imposta il trigger per ogni 4 ore
    trigger = IntervalTrigger(hours=2, start_date=first_run)
    print(f"Trigger set every 2 hours starting from: {first_run}")

    # Aggiungi l'attività con il trigger allo scheduler
    scheduler.add_job(scheduled_task, trigger)
    print("Scheduled task added to the scheduler")

    # Avvia l'app Flask
    print("Starting Flask app on host='0.0.0.0', port=80")
    app.run(host='0.0.0.0', port=80)