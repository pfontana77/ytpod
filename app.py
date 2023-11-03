from flask import Flask, Response, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
import os
import threading
import subprocess
import download_episodes_from_channel as dec
import rss
import log_config
import logging

# Configura il sistema di log
log_config.setup_logger("werkzeug", "flask.log", logging.DEBUG)  # Logger per Flask
log_config.setup_logger(
    "app_logger", "app.log", logging.INFO
)  # Logger per il tuo codice

# Ottieni i logger configurati
flask_logger = logging.getLogger("werkzeug")  # Logger per Flask
app_logger = logging.getLogger("app_logger")  # Logger per il tuo codice

# Crea un'istanza dell'applicazione Flask
app = Flask(__name__)

# Crea un lock globale
task_lock = threading.Lock()


def scheduled_task():
    if not task_lock.acquire(blocking=False):
        app_logger.warning("Un altro task è in esecuzione. Questo task sarà ignorato.")
        return

    try:
        app_logger.info(
            "Nessun altro task in esecuzione. Esecuzione del task programmato..."
        )
        dec.download_episodes()
        rss.update_feed()
    finally:
        task_lock.release()


def delete_downloaded_file():
    try:
        os.remove("downloaded.txt")
        app_logger.info("File downloaded.txt deleted.")
    except FileNotFoundError:
        app_logger.warning("File downloaded.txt not found.")


def append_to_channel_lists(text):
    file_name = "channel_lists.cfg"
    try:
        with open(file_name, "a") as f:
            f.write(f"\n{text}")
            return True
    except Exception as e:
        app_logger.error(f"Errore durante l'append al file {file_name}: {str(e)}")
        return False


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
        app_logger.error(f"File 'channel_lists.cfg' non trovato: {str(e)}")
        channel_list = "Il file channel_lists.cfg non è stato trovato."
    except Exception as e:
        app_logger.error(
            f"Errore durante la lettura del file 'channel_lists.cfg': {str(e)}"
        )
        channel_list = f"Errore durante la lettura del file channel_lists.cfg: {str(e)}"
    return channel_list


def upgrade_g4f():
    app_logger.info("Upgrading g4f: ")
    try:
        result = subprocess.run(
            ["pip", "install", "--upgrade", "g4f"],
            check=True,
            text=True,
            capture_output=True,
        )
        app_logger.info(f"Upgrade successful: {result.stdout}")
    except subprocess.CalledProcessError as e:
        app_logger.error(f"Upgrade failed: {e.stderr}")


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
        app_logger.error(message)
        return message, 404
    except Exception as e:
        message = f"Errore durante la lettura del file app.log: {str(e)}"
        app_logger.error(message)
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
    try:
        app_logger.info(f"Serving file: {filename}")
        return send_from_directory(
            os.path.join("output", channel),
            filename,
            as_attachment=False,
            mimetype="audio/mp3",
        )
    except FileNotFoundError as e:
        app_logger.error(f"File not found: {str(e)}")
        return f"File {filename} not found", 404
    except Exception as e:
        app_logger.error(f"An error occurred while serving the file: {str(e)}")
        return f"An error occurred: {str(e)}", 500


@app.route("/trigger_scheduled_task")
def trigger_scheduled_task_route():
    try:
        scheduled_task()
        return "Scheduled task triggered successfully."
    except Exception as e:
        app_logger.error(
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
    app_logger.info(f"Current time: {now}")
    first_run = datetime.datetime(now.year, now.month, now.day, 23, 50)
    app_logger.info(f"First run time: {first_run}")
    trigger = IntervalTrigger(hours=2, start_date=first_run)
    app_logger.info(f"Trigger set every 2 hours starting from: {first_run}")
    scheduler.add_job(scheduled_task, trigger, max_instances=1)
    app_logger.info("Podcast task added to the scheduler")
    app_logger.info("Scheduing daily upgrade of g4f...")
    scheduler.add_job(upgrade_g4f, "cron", hour=0, minute=50, id="upgrade_g4f")
    app_logger.info("Daily g4f upgrade added to the scheduler")
    app_logger.info("Starting Flask app on host='0.0.0.0', port=8080")
    scheduler.start()
    app.run(host="0.0.0.0", port=8080)
