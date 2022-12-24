import logging
import os
import google.cloud.logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler

def setup_logger(name: str, log_file:str = '/data/discord.log', level = logging.INFO):
    if (int(os.environ.get("PRODUCTION", 0)) == 1):
        client = google.cloud.logging.Client()
        handler = CloudLoggingHandler(client)
    else:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
