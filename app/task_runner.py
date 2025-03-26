from queue import Queue
from threading import Thread, Event
import os
import json
import time


class ThreadPool:
    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        # Note: the TP_NUM_OF_THREADS env var will be defined by the checker
        if 'TP_NUM_OF_THREADS' in os.environ:
            self.num_threads = int(os.environ['TP_NUM_OF_THREADS'])
        else:
            self.num_threads = os.cpu_count()
        self.task_queue = Queue()
        self.threads = []
        self.shutdown_event = Event()
        self._create_threads()
        
    def _create_threads(self):
        for _ in range(self.num_threads):
            thread = TaskRunner()
            self.threads.append(thread)
            thread.start()

    def add_task(self, task):
        # Add task to the queue
        self.task_queue.put(task)

    def wait_completion(self):
        # Wait for all tasks to be completed
        self.task_queue.join()

    def shutdown(self):
        # Shutdown the ThreadPool
        # This should also stop all the threads in the pool
        self.shutdown_event.set()
        for _ in range(self.num_threads):
            self.task_queue.put(None)
        for thread in self.threads:
            thread.join()
        self.task_queue.join()

class TaskRunner(Thread):
    def __init__(self):
        # TODO: init necessary data structures 
        pass

    def run(self):
        while True:
            # TODO
            # Get pending job
            # Execute the job and save the result to disk
            # Repeat until graceful_shutdown
            pass
