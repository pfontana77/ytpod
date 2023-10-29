from flask import Flask, Response, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
import os
import logging
import threading
import subprocess
import download_episodes_from_channel as dec
import rss


# Configura il sistema di log
logger = logging.getLogger("app_logger")
logger.setLevel(logging.ERROR)  # Imposta il livello di log globale a ERROR

# Crea un handler per scrivere i log su file
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(
    logging.ERROR
)  # Imposta il livello di log per il file handler a ERROR

# Crea un handler per scrivere i log sulla console
console_handler = logging.StreamHandler()
console_handler.setLevel(
    logging.ERROR
)  # Imposta il livello di log per il console handler a ERROR

# Crea un formatter e lo assegna ad entrambi gli handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Aggiungi gli handler al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = Flask(__name__)
# Crea un lock globale
task_lock = threading.Lock()


def scheduled_task():
    # Tenta di acquisire il lock, restituisce False se il lock è già acquisito
    if not task_lock.acquire(blocking=False):
        print("Un altro task è in esecuzione. Questo task sarà ignorato.")
        return

    try:
        # Altrimenti, esegui il task
        print("Nessun altro task in esecuzione. Esecuzione del task programmato...")
        dec.download_episodes()  # Scarica gli episodi
        rss.update_feed()  # Aggiorna il feed RSS
    finally:
        # Rilascia il lock alla fine del task
        task_lock.release()


def delete_downloaded_file():
    try:
        os.remove("downloaded.txt")
        print("File downloaded.txt deleted.")
    except FileNotFoundError:
        print("File downloaded.txt not found.")


def append_to_channel_lists(text):
    file_name = "channel_lists.cfg"
    try:
        with open(file_name, "a") as f:
            f.write(f"\n{text}")
            return True  # Restituisce True se l'append è riuscito
    except Exception as e:
        print(f"Errore durante l'append al file {file_name}: {str(e)}")
        return False  # Restituisce False se si è verificato un errore


def print_channel_list():
    channel_list = "Elenco dei canali:\n"
    try:
        with open("channel_lists.cfg", "r") as file:
            for line_number, line in enumerate(file, start=1):
                cleaned_line = line.strip()
                if cleaned_line:  # Ignora le righe vuote
                    channel_list += f"{line_number}. {cleaned_line}\n"
                else:
                    channel_list += f"{line_number}. (riga vuota)\n"
    except FileNotFoundError as e:
        logging.error(f"File 'channel_lists.cfg' non trovato: {str(e)}")
        channel_list = "Il file channel_lists.cfg non è stato trovato."
    except Exception as e:
        logging.error(
            f"Errore durante la lettura del file 'channel_lists.cfg': {str(e)}"
        )
        channel_list = f"Errore durante la lettura del file channel_lists.cfg: {str(e)}"
    return channel_list


def upgrade_g4f():
    print(f"Upgrading g4f: ")
    try:
        result = subprocess.run(
            ["pip", "install", "--upgrade", "g4f"],
            check=True,
            text=True,
            capture_output=True,
        )
        print(f"Upgrade successful: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Upgrade failed: {e.stderr}")
        logging.error(f"Upgrade failed: {e.stderr}")


@app.route("/append_to_channel_lists/<string:text>")
def append_to_channel_lists_route(text):
    success = append_to_channel_lists(text)
    if success:
        return f"Appended '{text}' to channel_lists.cfg."
    else:
        return f"Failed to append '{text}' to channel_lists.cfg."


@app.route("/print_channel_list")
def print_channel_list_route():
    channel_list = print_channel_list()
    return Response(channel_list, mimetype="text/plain")


@app.route("/view_log")
def view_log():
    try:
        with open("app.log", "r", encoding="utf-8") as file:
            log_content = file.read()
        return Response(log_content, mimetype="text/plain")
    except FileNotFoundError as e:
        message = f"File app.log non trovato: {str(e)}"
        logging.error(message)
        return message, 404
    except Exception as e:
        message = f"Errore durante la lettura del file app.log: {str(e)}"
        logging.error(message)
        return message, 500


@app.route("/delete_downloaded")
def delete_downloaded():
    delete_downloaded_file()
    return "File downloaded.txt deleted."


@app.route("/<channel>/feed.xml")
def serve_feed(channel):
    return send_from_directory(os.path.join("output", channel), "feed.xml")


@app.route("/<channel>/<filename>")
def serve_file(channel, filename):
    print(f"Serving file: {filename}")
    return send_from_directory(
        os.path.join("output", channel),
        filename,
        as_attachment=False,
        mimetype="audio/mp3",
    )


@app.route("/trigger_scheduled_task")
def trigger_scheduled_task_route():
    try:
        scheduled_task()
        return "Scheduled task triggered successfully."
    except Exception as e:
        logging.error(
            f"Errore durante l'esecuzione manuale del task programmato: {str(e)}"
        )
        return (
            f"Errore durante l'esecuzione manuale del task programmato: {str(e)}",
            500,
        )


if __name__ == "__main__":
    # print("Running initial task...")
    # scheduled_task()

    scheduler = BackgroundScheduler()
    now = datetime.datetime.now()
    print(f"Current time: {now}")
    first_run = datetime.datetime(now.year, now.month, now.day, 23, 50)
    print(f"First run time: {first_run}")
    trigger = IntervalTrigger(hours=2, start_date=first_run)
    print(f"Trigger set every 2 hours starting from: {first_run}")
    scheduler.add_job(scheduled_task, trigger, max_instances=1)
    print("Podcast task added to the scheduler")
    print("Scheduing daily upgrade of g4f...")
    scheduler.add_job(upgrade_g4f, "cron", hour=0, minute=50, id="upgrade_g4f")
    print("Daily g4f upgrade added to the scheduler")
    print("Starting Flask app on host='0.0.0.0', port=80")
    app.run(host="0.0.0.0", port=80)
