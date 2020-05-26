import ndjson
import signal
import tornado.ioloop

from kafka import KafkaProducer


class KafkaData:
    def __init__(self, settings):
        self.config = {
            'bootstrap_servers': ['192.168.5.134:9092']
        }
        self.producer = KafkaProducer(**self.config)
        self.cache = {}
        self.close_flag = 0

    def multi_data_handler(self, item):
        topic, value = item
        if not self.cache.get(topic):
            self.cache[topic] = []
        self.cache[topic].append(value)
        if len(self.cache[topic]) >= 1:
            _data = ndjson.dumps(self.cache[topic])
            # print(_data)
            self.send(topic, _data)
            self.cache[topic] = []

    def single_data_handler(self, item):
        topic, value = item
        _data = ndjson.dumps([value, ])
        # print(_data)
        self.send(topic, _data)

    def send(self, topic, value, key=b''):
        if not isinstance(value, bytes):
            value = value.encode('utf-8')
        future = self.producer.send(topic, key=key, value=value, partition=0)
        result = future.get(timeout=10)
        # print(result)

    def close_spider(self):
        signal.signal(signal.SIGTERM, self._handle_term_signal)
        signal.signal(signal.SIGINT, self._handle_term_signal)

    def _handle_term_signal(self, sig_num, frame):
        print('程序关闭', sig_num, frame)
        tornado.ioloop.IOLoop.instance().stop()




