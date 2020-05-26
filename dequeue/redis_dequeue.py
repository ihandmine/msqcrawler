import six
import redis
import tornado.ioloop
import tornado.gen

from dequeue import Usage as usage
from utils.misc import load_object, get_settings


REDIS_CLS = redis.StrictRedis
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
}

SETTINGS_PARAMS_MAP = {
    'REDIS_URL': 'url',
    'REDIS_HOST': 'host',
    'REDIS_PORT': 'port',
    'REDIS_ENCODING': 'encoding',
}
START_URLS_KEY = '%(name)s:start_urls'


def get_redis_from_settings(conf):
    params = REDIS_PARAMS.copy()
    params.update(usage.getdict(conf, 'REDIS_URL'))
    for source, dest in SETTINGS_PARAMS_MAP.items():
        val = usage.get(conf, source)
        if val:
            params[dest] = val

    if isinstance(params.get('redis_cls'), six.string_types):
        params['redis_cls'] = load_object(params['redis_cls'])

    return get_redis(**params)


def get_redis(**kwargs):
    redis_cls = kwargs.pop('redis_cls', REDIS_CLS)
    url = kwargs.pop('url', None)
    if url:
        return redis_cls.from_url(url)
    else:
        return redis_cls(**kwargs)


class Base(object):
    def __init__(self, server, topic, serializer=None):
        if serializer is None:
            serializer = usage
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)

        self.server = server
        self.spider = topic
        self.key = START_URLS_KEY % {'name': topic}
        self.serializer = serializer

    def _encode_message(self, message):
        """Encode a request object"""
        return self.serializer.dumps(message)

    def _decode_message(self, encoded_message):
        """Decode an request previously encoded"""
        obj = self.serializer.loads(encoded_message)
        return obj

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, message, priority):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)


class PriorityQueue(Base):
    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, message, priority):
        data = self._encode_message(message)
        score = priority
        self.server.execute_command('ZADD', self.key, score, data)

    def pop(self, timeout=0):
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_message(results[0])


class Message(object):

    def __init__(self, reader, body):
        self._async_enabled = False
        self._has_responded = False
        self.body = body.encode('utf-8')
        self.reader = reader

    def enable_async(self):
        self._async_enabled = True

    def is_async(self):
        return self._async_enabled

    def has_responded(self):
        return self._has_responded

    def finish(self):
        assert not self._has_responded
        self._has_responded = True
        self.reader.once_read()
        # tornado.ioloop.IOLoop.current().spawn_callback(self.reader.once_read_tor)


class Reader(object):
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance.settings = get_settings()
        return instance

    def __init__(self, topic, message_handler, max_in_flight):
        self.max_in_flight = max_in_flight
        self.server = get_redis_from_settings(self.settings)
        self.queue = PriorityQueue(self.server, topic)
        self.message_handler = None
        if message_handler:
            self.set_message_handler(message_handler)

    def read(self):
        for _ in range(self.max_in_flight):
            message = Message(self, self.queue.pop())
            self.message_handler(message)

    def once_read(self):
        message = Message(self, self.queue.pop())
        self.message_handler(message)

    def set_message_handler(self, message_handler):
        assert callable(message_handler), 'message_handler must be callable'
        self.message_handler = message_handler

    @tornado.gen.coroutine
    def once_read_tor(self):
        yield tornado.gen.sleep(0.05)
        message = Message(self, self.queue.pop())
        self.message_handler(message)
        yield tornado.gen.sleep(0.05)


class Dequeue(object):

    @classmethod
    def start_listen(cls, topic, callback):
        reader = Reader(
            topic=topic,
            message_handler=callback,
            max_in_flight=8
        )
        import tornado.ioloop
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.add_callback(reader.read)


