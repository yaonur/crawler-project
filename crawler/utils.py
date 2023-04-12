import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import urllib

def get_logger():
	logger=logging.getLogger(__name__)
	logging_level=os.getenv(key='LOGGING_LEVEL',default='DEBUG')
	formatter = logging.Formatter('%(asctime)s --> %(levelname)s - %(message)s')
	logger.setLevel(level=logging_level)

	# TODO: use sentry 
	c_handler=logging.StreamHandler()
	c_handler.setLevel(level=logging_level)
	c_handler.setFormatter(formatter)
	file_handler=RotatingFileHandler('crawler.log',maxBytes=1024*1024,backupCount=0)
	file_handler.setLevel(logging.ERROR)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	logger.addHandler(c_handler)

	return logger

def check_url(anchor,domain):
	if Path(anchor).suffix:
		return False
	elif anchor.startswith("//"):
		return "https:"+anchor
	elif anchor.startswith("/"):
		return "https://"+domain+anchor
	elif domain in urllib.parse.urlparse(anchor).netloc:
		return anchor
	return False