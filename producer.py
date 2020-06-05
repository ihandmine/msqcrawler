import os
import json
import functools
from abc import ABC

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import pymysql

from nsq import Writer, Error

from dequeue.redis_dequeue import PriorityQueue, get_redis_from_settings


class BaseHandler(tornado.web.RequestHandler, ABC):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @property
    def nsq(self):
        return self.application.nsq

    @property
    def queue(self):
        _queue = self.application.Queue(get_redis_from_settings(self.schedule.settings), 'spider')
        return _queue

    def finish_pub(self, conn, data, topic, msg):
        print(data)
        if isinstance(data, Error):
            # try to re-pub message again if pub failed
            self.nsq.pub(topic, msg)


class KeywordHandler(BaseHandler):
    def get(self):
        """
        msg = '{"spider": "keyword_us", "topic": "keyword", "url": "", "meta": {"keyword": ""}}'.encode('utf-8')
        :return:
        """
        pass


class ReviewHandler(BaseHandler):
    def get(self):
        """
        msg = '{"spider": "review_us", "topic": "review", "url": "", "meta": {"asin": ""}}'.encode('utf-8')
        :return:
        """
        pass


class BestsellerHandler(BaseHandler):
    def get(self):
        """
        msg = '{"spider": "bestseller_us", "topic": "bestseller", "url": "", "meta": {"node": ""}}'.encode('utf-8')
        :return:

        """
        pass


class QuestionHandler(BaseHandler):
    def get(self):
        """
        msg = '{"spider": "question_us", "topic": "question", "url": "", "meta": {"asin": ""}}'.encode('utf-8')
        :return:
        """
        pass


class AnswerHandler(BaseHandler):
    def get(self):
        """
        msg = '{"spider": "answer_us", "topic": "answer", "url": "", "meta": {"question_id": ""}}'.encode('utf-8')
        :return:
        """
        pass


class ListingHandler(BaseHandler):
    def get(self):
        """
        msg = '{"spider": "local_spider", "topic": "qiushispider", "url": "http://192.168.5.222:9501/", "meta": {}}'.encode('utf-8')
        msg = '{"spider": "qiushi", "topic": "qiushispider", "url": "https://www.qiushibaike.com/text/", "meta": {}}'.encode('utf-8')
        msg = '{"spider": "listing_us", "topic": "listing", "url": "https://www.amazon.com/dp/B019U00D7K", "meta": {"asin": "B019U00D7K"}}'.encode('utf-8')

        self.nsq.pub(topic, msg)  # pub
        self.nsq.mpub(topic, [msg, msg_cn])  # mpub
        self.nsq.dpub(topic, 60, msg)  # dpub
        """

        urls = {
            'us': 'https://www.amazon.com',
            'uk': 'https://www.amazon.co.uk',
        }
        topic = 'spider'
        country = ''
        if "country" in self.request.arguments:
            country = self.get_argument('country', 'us')

        def struct_msg(asin):
            return (self.schedule.settings['MESSAGE_MODEL'] % {
                'spider': 'listing_' + country,
                'target_topic': 'listing',
                'url': urls[country] + '/dp/' + asin,
                'meta': json.dumps({'asin': asin})
            }).encode('utf-8')

        if "asin" in self.request.arguments:
            asin = self.get_argument('asin')
            msg = struct_msg(asin)
            callback = functools.partial(self.finish_pub, topic=topic, msg=msg)
            self.nsq.pub(topic, msg, callback=callback)
            self.write(msg)
        else:
            if self.get_argument('type') == "file":
                filename = "asins.txt"
                if not os.path.exists(filename):
                    raise FileNotFoundError('[define] %s file not found' % filename)
                with open(filename, 'r') as f:
                    asins = f.read().split('\n')
                msgs = [struct_msg(asin) for asin in asins]
                self.write({"messages": msgs.insert(0, {"length": len(msgs)})})
            elif self.get_argument('type') == "sql":
                conn = pymysql.connect(
                    host='192.168.5.215',
                    user='cc',
                    password="mysql123",
                    database='spider_db_xc',
                    port=3306
                )
                cursor = conn.cursor()
                query_sql = """
                    SELECT
                        asin
                    FROM
                        xc_amazon_listing_{country}
                    WHERE
                        add_date_time > DATE_FORMAT( DATE_SUB( now(), INTERVAL 1 DAY ), "%Y-%m-%d" )
                        AND add_date_time < DATE_FORMAT( now(), "%Y-%m-%d" )
                    GROUP BY
                        asin
                """.format(country=country)
                effect_row = cursor.execute(query_sql)
                result = [item[0] for item in cursor.fetchall()]
                msgs = [struct_msg(asin) for asin in result]
                self.write({"length": effect_row, "messages": [json.loads(ms.decode('utf-8')) for ms in msgs if isinstance(ms, bytes)]})
            else:
                raise KeyError('[define] not found key type')
            callback = functools.partial(self.finish_pub, topic=topic, msg=msgs)
            if self.schedule.settings['USE_REDIS']:
                for msg in msgs:
                    self.queue.push(msg.decode('utf-8'), 0)
            else:
                self.nsq.mpub(topic, msgs, callback=callback)


class Application(tornado.web.Application):
    def __init__(self, handlers, **settings):
        self.nsq = Writer(['192.168.5.134:4150'])
        self.Queue = PriorityQueue
        # self.nsq = Writer(['127.0.0.1:4150'])
        super(Application, self).__init__(handlers, **settings)


class Publisher(object):
    def __init__(self):
        self.writer = Writer(['192.168.5.134:4150'])
        self.topic = ''
        self.message = ''

    @classmethod
    def run_web_spider(cls, schedule=None):
        if schedule:
            ListingHandler.schedule = schedule
        application = Application([
            (r"/listing", ListingHandler),
            (r"/keyword", KeywordHandler),
            (r"/review", ReviewHandler),
            (r"/question", QuestionHandler),
            (r"/answer", AnswerHandler),
            (r"/bestseller", BestsellerHandler)
        ])
        application.listen(8888)

    @tornado.gen.coroutine
    def do_pub(self):
        yield tornado.gen.sleep(0.05)
        topic = self.topic
        if isinstance(self.message, bytes):
            msg = self.message.decode('utf-8')
        else:
            msg = self.message.body
        self.writer.pub(topic, msg, self.finish_pub)
        yield tornado.gen.sleep(0.05)

    def start(self, topic, message):
        self.topic = topic
        self.message = message
        tornado.ioloop.IOLoop.current().spawn_callback(self.do_pub)
        # tornado.ioloop.IOLoop.current().run_sync(self.do_pub)
        # tornado.ioloop.IOLoop.instance().run()

    def finish_pub(self, conn, data):
        print(data)
        # if isinstance(data, Error):
        #     self.writer.pub(topic, msg)


if __name__ == "__main__":
    from scheduler import Scheduler
    s = Scheduler()
    Publisher.run_web_spider(s)
    tornado.ioloop.IOLoop.current().start()
