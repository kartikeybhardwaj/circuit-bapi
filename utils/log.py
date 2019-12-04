import logging
from logging.handlers import RotatingFileHandler
from constants.logpath import log_path

handler = RotatingFileHandler(log_path, maxBytes=5242880, backupCount=10)
formatter = logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger("circuit_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
