from queue import Queue
from threading import Thread, Event
import time
import os
import json

class ThreadPool:
    def __init__(self, webserver):

        self.webserver = webserver
        self.queue = webserver.job_queue
        self.job_statuses = webserver.job_statuses
        self.graceful_shutdown = webserver.shutdown_event

        self.threads = []

        if os.getenv("TP_NUM_OF_THREADS") is not None:
            num_threads = int(os.getenv("TP_NUM_OF_THREADS"))
        else:
            num_threads = os.cpu_count()
        self.threads = [
            TaskRunner(self.queue, self.job_statuses, self.graceful_shutdown)
            for _ in range(num_threads)
        ]

    def start(self):
        for thread in self.threads:
            thread.start()

    def shutdown(self):
        self.graceful_shutdown.set()
        for thread in self.threads:
            thread.join()

class TaskRunner(Thread):
    def __init__(self, queue, job_statuses, graceful_shutdown):
        super().__init__()
        self.queue = queue
        self.job_statuses = job_statuses
        self.graceful_shutdown = graceful_shutdown

    def save_data(self, data, job_id):
        with open(f'results/{job_id}.json', 'w') as f:
            json.dump(data, f)
        self.job_statuses[job_id] = "done"

    def start_job(self):
        j = self.queue.get()
        if j is None:
            return
        job_id = j.job_id
        job_result = j.do_job()
        self.save_data(job_result, job_id)

    def run(self):
        while not self.graceful_shutdown.is_set():
            self.start_job()
