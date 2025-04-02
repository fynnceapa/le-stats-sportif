from queue import Queue
from threading import Thread, Event
import time
import os
import json

class ThreadPool:
    def __init__(self, webserver):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        # Note: the TP_NUM_OF_THREADS env var will be defined by the checker
        self.webserver = webserver
        self.queue = webserver.job_queue
        self.job_statuses = webserver.job_statuses
        self.graceful_shutdown = webserver.shutdown_event
        
        self.threads = []

        if os.getenv("TP_NUM_OF_THREADS") is not None:
            num_threads = int(os.getenv("TP_NUM_OF_THREADS"))
        else:
            num_threads = os.cpu_count()
        for i in range(num_threads):
            thread = TaskRunner(self.queue, self.job_statuses, self.graceful_shutdown, i)
            self.threads.append(thread)

    def start(self):
        for thread in self.threads:
            print(f"Starting thread {thread.id}")
            thread.start()

    def shutdown(self):
        self.graceful_shutdown.set()
        for thread in self.threads:
            thread.join()

class TaskRunner(Thread):
    def __init__(self, queue, job_statuses, graceful_shutdown, id):
        super().__init__()
        self.queue = queue
        self.job_statuses = job_statuses
        self.graceful_shutdown = graceful_shutdown
        self.id = id
    
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
        print(f"Thread {self.id} is shutting down")
