import os
import logging
import time
from queue import Queue
from threading import Event, Lock
from logging.handlers import RotatingFileHandler
from flask import Flask
from app.task_runner import ThreadPool
from app.data_ingestor import DataIngestor

class UTCFormatter(logging.Formatter):
    """Custom formatter to use UTC for timestamps."""
    converter = time.localtime

    def formatTime(self, record, datefmt=None):
        """Format the time in UTC."""
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return s

if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)

job_queue = Queue()
job_statuses = {}
shutdown_event = Event()

webserver.job_counter = 0
webserver.job_queue = job_queue
webserver.job_statuses = job_statuses
webserver.shutdown_event = shutdown_event

webserver.task_runner = ThreadPool(webserver)

webserver.task_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

logging_file = 'file.log'
if os.path.exists(logging_file):
    os.remove(logging_file)
format = '%(asctime)s - %(levelname)s - %(message)s'
handler = RotatingFileHandler(logging_file, maxBytes=5 * 1024 * 1024, backupCount=3)
handler.setLevel(logging.INFO)
formatter = UTCFormatter(format)
handler.setFormatter(formatter)

webserver.logger = logging.getLogger('webserver')
webserver.logger.setLevel(logging.INFO)
webserver.logger.addHandler(handler)
webserver.logger.info('Server started')

from app import routes
