import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from queue import Queue
from threading import Thread, Event
if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)

job_queue = Queue()
job_statuses = {}
shutdown_event = Event()
job_counter = 0
counter_lock = Thread.Lock()
webserver.task_runner = ThreadPool(job_queue, job_statuses, shutdown_event, job_counter, counter_lock)

webserver.task_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

from app import routes
