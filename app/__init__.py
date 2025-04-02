import os
import logging
import time
from queue import Queue
from threading import Thread, Event, Lock
from logging.handlers import RotatingFileHandler
from flask import Flask
from app.task_runner import ThreadPool
from app.data_ingestor import DataIngestor

if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)

job_queue = Queue()
job_statuses = {}
shutdown_event = Event()

webserver.counter_lock = Lock()
webserver.job_counter = 0
webserver.job_queue = job_queue
webserver.job_statuses = job_statuses
webserver.shutdown_event = shutdown_event

webserver.task_runner = ThreadPool(webserver)

webserver.task_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

from app import routes

