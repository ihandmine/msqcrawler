import time

from queue import Queue
from threading import Thread

from concurrent import futures
from concurrent.futures import ThreadPoolExecutor


class ThreadPool(Thread):
    """50个线程"""
    max_workers = Queue(maxsize=50)

    def __init__(self, scheduler, message):
        super(ThreadPool, self).__init__()
        self.scheduler = scheduler
        self.message = message
        self.setDaemon(True)
        ThreadPool.max_workers.put(message)

    def run(self):
        try:
            self.scheduler.process_spider_item(self.message)
        except Exception as e:
            print('error: ', e)
        finally:
            ThreadPool.max_workers.get()

    @classmethod
    def wait(cls):
        while cls.max_workers.qsize() > 0:
            time.sleep(1)


class ThreadPoolExecutorDefine(object):

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.thread_pool = ThreadPoolExecutor(8)
        self.jobs = {}

    @property
    def executor(self):
        return self.thread_pool

    def run(self, message):
        future = self.executor.submit(self.scheduler.process_spider_item, message)
        return future

    def map(self, queue):
        self.executor.map(self.scheduler.process_spider_item, queue)

    def finish(self, future):
        try:
            future.result().finish()
        except Exception as e:
            print('[define] finish is failed', e)

    def clear(self):
        for job in futures.as_completed(self.jobs):
            del self.jobs[job]
            del job

