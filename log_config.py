import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.INFO):
    """Configura un logger con un nome specifico, un file di log e un livello di log."""
    logger = logging.getLogger(name)
    logger.setLevel(level)  # Imposta il livello di log

    # Crea un handler per scrivere i log su file
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(level)  # Imposta il livello di log per il file handler

    # Crea un formatter e lo assegna al file handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Aggiungi solo il file handler al logger
    logger.addHandler(file_handler)
