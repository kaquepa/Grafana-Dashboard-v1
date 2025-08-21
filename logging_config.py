import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


class LoggingConfig:
    def __init__(self):
        try:
            log_dir = Path("Logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "Logging.log"
             
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024, # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            stream_handler = logging.StreamHandler()
            logging.basicConfig(
                level=logging.INFO,
                handlers=[file_handler, stream_handler]
            )
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

        except Exception as e:
            logging.error(f"Error creating log directory: {e}")

LoggingConfig()
