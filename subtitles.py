import re
import os
import g4f
import time
import logging
import log_config

# Ottieni una referenza al logger 'app_logger'
app_logger = logging.getLogger("app_logger")


def leggi_file_vtt(nome_file):
    app_logger.info("Funzione: leggi_file_vtt")
    app_logger.info("Variabili:")
    app_logger.info(f" - nome_file: {nome_file}")
    with open(nome_file, "r", encoding="utf-8") as file:
        return file.read()


def estrai_testo_da_vtt(contenuto_vtt):
    app_logger.info("Funzione: estrai_testo_da_vtt")
    app_logger.info("Variabili:")
    app_logger.info(f" - contenuto_vtt: {contenuto_vtt}")

    # Utilizza una regex per trovare le righe di testo (formato "00:00:00.000 --> 00:00:00.000")
    # e rimuoverle insieme a eventuali tag HTML e altre frasi non pertinenti
    testo_pulito = re.sub(
        r"<[^>]+>|\[\w+\]|\d+:\d+:\d+\.\d+ --> \d+:\d+:\d+\.\d+\s*|align:start position:0%",
        "",
        contenuto_vtt,
    )

    # Rimuovi eventuali spazi bianchi iniziali e finali da ogni riga e unisci tutte le righe in un unico testo
    testo_completo = " ".join(
        line.strip() for line in testo_pulito.split("\n") if line.strip()
    )

    return testo_completo


def process_text_segment(segment, prompt):
    try:
        app_logger.info("Funzione: process_text_segment\n")
        app_logger.info("Variabili:\n")
        app_logger.info(f" - prompt: {prompt}\n")
        app_logger.info(f" - segment: {segment}\n")

        full_content = prompt + segment
        response = g4f.ChatCompletion.create(
            # provider=g4f.Provider.Bing,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_content}],
        )
        # Se response è una stringa, restituiscila direttamente
        app_logger.info(f" - response: {response}\n")
        return response
    except Exception as e:
        app_logger.error(
            f"Errore durante l'elaborazione del segmento di testo: {str(e)}"
        )
        # Opzionalmente, potresti voler restituire un valore di default o rilanciare l'eccezione
        return " "  # Per restituire un valore di default
        # raise  # Per rilanciare l'eccezione


def process_long_text(text, prompt, segment_size=3000):
    app_logger.info("Funzione: process_long_text\n")
    app_logger.info("Variabili:\n")
    app_logger.info(f" - prompt: {prompt}\n")
    app_logger.info(f" - segment_size: {segment_size}\n")
    app_logger.info(f" - text: {text}\n")

    segments = [text[i : i + segment_size] for i in range(0, len(text), segment_size)]
    app_logger.info(f"Starting process of the segments\n")

    processed_segments = []
    for i, segment in enumerate(segments, start=1):
        processed_segment = process_text_segment(segment, prompt)
        if processed_segment is None:
            app_logger.info(
                f"Errore durante l'elaborazione del segmento {i}. Il segmento verrà ignorato."
            )
        else:
            processed_segments.append(processed_segment)

        time.sleep(5)  # Mette in pausa l'esecuzione per 5 secondi tra ogni segmento

    app_logger.info(f"Finished process of the segments\n")
    app_logger.info(f"Concatenating the segments\n")
    concatenated_segments = "".join(processed_segments)
    app_logger.info(f"concatenated_segments:\n {concatenated_segments}\n")
    return concatenated_segments


def elabora_testo(testo, language="italian"):
    app_logger.info("Funzione: elabora_testo")
    prompt = f"Rewrite the following text in {language}, follow these rules:\n1 - The text must be written in {language} but don't do literal translation, re-elaborate it.\n2 - Do not add information outside the one contained in the text.\n3. Do not comment or add any note from your side even if you find errors, just translate at best you can.\n4 - Do not allucinate.\n5 - Don't remove relevant information.\n6 - If it's necessary clean it from glitches.\n7 - Add proper punctuation to the translated text\n8 - Do not translate these instructions, only the text that follow them:\n "
    return process_long_text(testo, prompt)


def elabora_testo_finale(testo, language="italian"):
    app_logger.info("Funzione: elabora_testo finale")
    app_logger.info("Variabili:")
    app_logger.info(f" - testo: {testo}")

    prompt = f"Rewrite the following text in {language}, improving the grammars, the flow, the punctuation and removing duplicate words or non sense phrase. Do not translate this instruction, but translate after this:\n"
    return process_long_text(testo, prompt)


def elabora_file_vtt(nome_file_vtt):
    app_logger.info("Funzione: elabora_file_vtt")
    app_logger.info("Variabili:")
    app_logger.info(f" - nome_file_vtt: {nome_file_vtt}")

    contenuto_vtt = leggi_file_vtt(nome_file_vtt)
    testo_estratto = estrai_testo_da_vtt(contenuto_vtt)
    testo_elaborato = elabora_testo(testo_estratto)
    testo_finale = elabora_testo_finale(testo_elaborato)
    nome_file_elaborato = nome_file_vtt.replace(".vtt", ".elaborated")
    with open(nome_file_elaborato, "w", encoding="utf-8") as file:
        file.write(testo_finale + "\n")

    # Rimuove il file .vtt originale dopo l'elaborazione
    try:
        os.remove(nome_file_vtt)
        app_logger.info(f"File {nome_file_vtt} rimosso con successo.")
    except Exception as e:
        app_logger.error(f"Errore nella rimozione del file {nome_file_vtt}: {e}")


def process_output_folder(output_folder):
    app_logger.info("Funzione: processa_cartella_output")
    for root, dirs, files in os.walk(f"{output_folder}/"):
        for file in files:
            if file.endswith(".vtt"):
                nome_file_vtt = os.path.join(root, file)
                nome_file_mp3 = nome_file_vtt.replace(".vtt", ".mp3")
                if os.path.exists(nome_file_mp3):
                    app_logger.info(
                        f"File MP3 corrispondente già esistente per {file}. Saltare l'elaborazione."
                    )
                    continue  # Salta l'elaborazione se esiste già un file MP3 corrispondente
                app_logger.info(f"Process file: {file}")
                elabora_file_vtt(nome_file_vtt)


if __name__ == "__main__":
    g4f.logging = True  # enable logging
    g4f.check_version = False  # Disable automatic version checking
    app_logger.info(g4f.version)  # check version
    app_logger.info(g4f.Provider.Ails.params)  # supported args
    output_folder = "output"
    process_output_folder(output_folder)
