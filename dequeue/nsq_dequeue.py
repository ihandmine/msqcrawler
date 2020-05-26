from nsq import Reader


class Dequeue(object):

    @classmethod
    def start_listen(cls, topic, callback):
        Reader(
            message_handler=callback,
            # nsqd_tcp_addresses=['192.168.5.134:4150'],
            lookupd_http_addresses=['192.168.5.134:4161'],
            # lookupd_http_addresses=['127.0.0.1:4161'],
            topic=topic,
            channel='channel1',
            max_in_flight=16,
            # timeout=60*3,
            # output_buffer_size=1024*5
        )

    @classmethod
    def start_listen_gnsq(cls, topic, callback):
        import gnsq
        consumer = gnsq.Consumer(
            message_handler=callback,
            # nsqd_tcp_addresses=['192.168.5.134:4150'],
            lookupd_http_addresses=['192.168.5.134:4161'],
            # lookupd_http_addresses=['127.0.0.1:4161'],
            topic=topic,
            channel='channel1',
            max_in_flight=8,
        )
        consumer.start()

    @classmethod
    def start_listen_gnsq_map(cls, topic, callback):
        import gevent.pool
        import gnsq
        from gnsq.contrib.queue import QueueHandler
        consumer = gnsq.Consumer(
            # nsqd_tcp_addresses=['192.168.5.134:4150'],
            lookupd_http_addresses=['192.168.5.134:4161'],
            # lookupd_http_addresses=['127.0.0.1:4161'],
            topic=topic,
            channel='channel1',
            max_in_flight=16,
        )
        queue = QueueHandler(maxsize=16)
        consumer.on_message.connect(queue)
        consumer.start(block=False)
        pool = gevent.pool.Pool(16)
        pool.map(callback, queue)

