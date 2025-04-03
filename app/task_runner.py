from queue import Queue
from threading import Thread, Event
import time
import os
import json

class ThreadPool:
    """ThreadPool class to manage a pool of threads for processing jobs."""
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
        for i in range(num_threads):
            thread = TaskRunner(self.queue, self.job_statuses, self.graceful_shutdown, i)
            self.threads.append(thread)

    def start(self):
        """Start the thread pool."""
        for thread in self.threads:
            thread.start()

    def shutdown(self):
        """Shutdown the thread pool gracefully."""
        if self.graceful_shutdown.is_set():
            for thread in self.threads:
                thread.join()

class TaskRunner(Thread):
    """TaskRunner class to process jobs in the queue."""
    def __init__(self, queue, job_statuses, graceful_shutdown, i):
        super().__init__()
        self.queue = queue
        self.job_statuses = job_statuses
        self.graceful_shutdown = graceful_shutdown
        self.id = i

    def save_data(self, data, job_id):
        """Save the job result to a file."""
        with open(f'results/{job_id}.json', 'w') as f:
            json.dump(data, f)
        self.job_statuses[job_id] = "done"

    def start_job(self):
        """Start a job from the queue."""
        j = self.queue.get()
        if j is None:
            return
        job_id = j.job_id
        job_result = j.do_job()
        self.save_data(job_result, job_id)

    def run(self):
        """Run the task runner."""
        while not self.graceful_shutdown.is_set():
            self.start_job()
        print(f"Thread {self.id} shutting down gracefully.")
