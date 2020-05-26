# encoding: utf-8
import logging
import redis
import random

logger = logging.getLogger('proxy_cache')


class Proxy(object):
    def __init__(self):
        self.r = redis.StrictRedis(
            host='192.168.5.216',
            port=6380,
            password='erpteam_redis',
            db=15)
        self.cache = []

    def get_proxy(self, redis_key):
        while len(self.cache) < 5:
            result = self.r.zrangebyscore(redis_key, 100, 100)
            if result:
                p = 'http://' + random.choice(result)
                logger.info(u'get proxy from redis score 100-100: {}'.format(p))
            else:
                p = 'http://' + random.choice(self.r.zrevrange(redis_key, 0, 100))
                logger.info(u'get proxy from redis score 0-100: {}'.format(p))
            self.cache.append(p)


proxy_cache = Proxy()
