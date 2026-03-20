import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "trading_bot", log_file: str = "logs/trading.log"):
    """Sets up a logger that outputs to both console and a rotating file."""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating: 5MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
