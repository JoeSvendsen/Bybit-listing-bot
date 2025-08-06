import logging
import os
from dotenv import load_dotenv

def setup_logging():
    load_dotenv()
    loglevel = os.environ.get('BOT_LOGLEVEL', 'INFO').upper()
    logfile = os.environ.get('BOT_LOGFILE', '')
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers
    )
