
# DOWNLOADER_MIDDLEWARES = {
#     # Engine side
#     'scrapy_redis_ptx.downloadermiddlewares.timeout.TimeoutMiddleware': 320,
#     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
#     'scrapy_redis_ptx.downloadermiddlewares.retry.PtxRetryMiddleware': 550,
#     'scrapy_redis_ptx.downloadermiddlewares.useragent.RandomUserAgentMiddleware': 560,
#     'scrapy_redis_ptx.downloadermiddlewares._cookie.CookiesMiddleware': 565,
#     'scrapy_redis_ptx.downloadermiddlewares.verify.AmazonVerifyMiddleware': 570,
#     'scrapy_redis_ptx.downloadermiddlewares._proxy.ProxyMiddleware': 745,
#     'scrapy_redis_ptx.downloadermiddlewares.rollback.RollbackProxyMiddleware': 950,
#     # Downloader side
# }

DOWNLOADER_MIDDLEWARES = {
    'middlewares.useragent.RandomUserAgentMiddleware': 560,
}

ASYNC_HTTP = True
ASYNC_METHOD = 'tornado'
# ASYNC_METHOD = 'asyncio'
NSQ_TOPIC = "spider"
SPIDER_DIR = "./spiders"
FILTER_SPIDER = [
    # 'LocalSpider',
    # 'QiushiSpider',
    'Listing[A-Z][a-z]Spider'
]
MESSAGE_MODEL = """{"spider": "%(spider)s", "topic": "%(target_topic)s", "url": "%(url)s", "meta": %(meta)s}"""

USE_REDIS = False
REDIS_URL = 'redis://:erpteam_redis@192.168.5.216:6381/15'

MYSQL_ARGS = {
    'database': 'spider_db',
    'user': 'cc',
    'password': 'mysql123',
    'host': '192.168.5.237',
    'port': 3306,
    'charset': 'utf8mb4',
    # 'max_connections': 8,
    # 'stale_timeout': 300,
}
