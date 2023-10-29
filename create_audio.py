import os
from gtts import gTTS


def create_audio_from_folder(output_folder):
    # Scansione delle sottocartelle e dei file nella cartella 'output'
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            try:
                # Verifica se il file è un .elaborated
                if file.endswith(".elaborated"):
                    path_vtt = os.path.join(root, file)

                    # Leggi il contenuto del file .elaborated
                    with open(path_vtt, "r", encoding="utf-8") as f:
                        testo = f.read()

                    # Crea un oggetto gTTS con il testo
                    tts = gTTS(text=testo, lang="it")

                    # Nome del file MP3
                    nome_file_audio = os.path.splitext(file)[0] + ".mp3"
                    path_mp3 = os.path.join(root, nome_file_audio)

                    # Salva l'audio in un file MP3
                    tts.save(path_mp3)

                    # Elimina il file .elaborated originale dopo la conversione in MP3
                    os.remove(path_vtt)

            except Exception as e:
                print(
                    f"Errore durante la conversione del file {file} in audio: {str(e)}"
                )


# Cartella 'output'
output_folder = "output"

# Chiamata alla funzione
create_audio_from_folder(output_folder)
