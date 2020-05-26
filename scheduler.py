import asyncio
import json
import tornado.ioloop

from tornado import gen

from pool import Thread, ThreadPoolExecutorDefine
from dequeue.nsq_dequeue import Dequeue as nsq_queue
from dequeue.redis_dequeue import Dequeue as redis_queue
from kafka_data import KafkaData
from engine import Engine
from producer import Publisher
from utils.misc import get_settings
from utils.watchdog import start_observer, load_filter_spider
from spider import FollowRequest


class Scheduler(object):

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance.settings = get_settings()
        return instance

    def __init__(self):
        self.spiders = {}
        if self.settings['USE_REDIS']:
            self.dequeue = redis_queue.start_listen
        else:
            self.dequeue = nsq_queue.start_listen
        self.kafka = KafkaData(self.settings)
        self.engine = Engine
        self.topic = self.settings["NSQ_TOPIC"]
        self.thread_pool = ThreadPoolExecutorDefine(self)
        self.messages = []
        self.target_topic = ''
        self.loop = None

    def observer(self):
        load_filter_spider(self)
        start_observer(self.settings["SPIDER_DIR"], self)

    def web(self):
        Publisher.run_web_spider(self)

    def runtime(self):
        # Thread(target=self.observer).start()
        Thread(target=self.dequeue, args=(self.topic, self.process_message_multi)).start()
        self.observer()
        # self.web()
        self.kafka.close_spider()
        tornado.ioloop.IOLoop.instance().start()

    @gen.coroutine
    def process_message_coroutine(self, message):
        if self.settings['ASYNC_HTTP']:
            result = yield self.process_spider_item(message)
        else:
            result = yield self.thread_pool.run(message)
        raise gen.Return(result)

    def process_message_multi(self, message):
        message.enable_async()

        result_future = self.process_message_coroutine(message)

        def coroutine_callback(msg):
            msg.finish()

        def handle_future(future):
            io_loop = tornado.ioloop.IOLoop.current()
            io_loop.add_callback(coroutine_callback, message)

        result_future.add_done_callback(handle_future)

    def process_spider_item(self, message):
        if not self.spiders:
            load_filter_spider(self)
        message_parse = json.loads(message.body.decode('utf-8'))
        self.target_topic = message_parse['topic']
        url = message_parse['url']
        meta = message_parse['meta']
        callfunc = "parse"

        spider_iter = self.spiders[message_parse['spider']]

        try:
            engine = self.engine()
            if engine.async_settings and engine.async_method == "tornado":
                return engine.runtime(url, spider_iter, meta, callfunc, callback=self.runner)

            elif engine.async_settings and engine.async_method == "asyncio":

                def hand_msg(future):
                    future.result().finish()
                if not self.loop:
                    self.loop = asyncio.get_event_loop()

                self.messages.append(engine.async_runtime(url, spider_iter, meta, callfunc, message, callback=self.runner))
                tasks = []
                if len(self.messages) == 8:
                    for corn in self.messages:
                        task = self.loop.create_task(corn)
                        task.add_done_callback(hand_msg)
                        tasks.append(task)

                    self.messages = []
                    self.loop.run_until_complete(asyncio.wait(tasks))
            else:
                engine.runtime(url)
                parse = getattr(spider_iter(engine.response, meta), callfunc)
                self.runner(parse, spider_iter)
            del engine
        except Exception as e:
            Publisher().start(self.topic, message)
            print('process_spider_item: ', e)

    def runner(self, parse, spider_iter):
        for item in parse():
            if not isinstance(item, FollowRequest):
                self.kafka.single_data_handler([self.target_topic, item])
                print('item: ', item)
            else:
                url, meta, spider_name = item
                message = self.settings['MESSAGE_MODEL'] % {
                    'spider': spider_iter.name,
                    'target_topic': self.target_topic,
                    'url': url,
                    'meta': json.dumps(meta)
                }
                Publisher().start(self.topic, message)


if __name__ == "__main__":
    s = Scheduler()
    s.runtime()
