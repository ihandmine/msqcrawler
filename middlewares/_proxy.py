import random
import logging

# from scrapy.exceptions import IgnoreRequest
from scrapy.utils.project import get_project_settings
from .proxy_cache import proxy_cache

logger = logging.getLogger('proxy')


class ProxyMiddleware(object):
    """
    给请求加上代理
    """

    def __init__(self, settings):
        self.use_proxy = settings.getbool('USE_PROXY')
        self.setting = get_project_settings()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        country = 'keyword' if 'keyword' in spider.name else ''
        if not country:
            country = 'us' if spider.name.split('_')[-1] == 'au' else spider.name.split('_')[-1]
        redis_key = 'proxies_' + country if not spider.name.startswith('ebay') else 'ebay_proxies'

        # xc_offerlisting爬虫代理使用专用的
        if spider.name.startswith('xc_offerlisting_us'):
            redis_key = 'offer_us'

        try:
            proxy_cache.get_proxy(redis_key)
            proxy = random.choice(proxy_cache.cache)
        except:
            spider.crawler.engine.close_spider(spider, 'not available proxy')
        if self.use_proxy:
            request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        if response.status not in [200, 404, 302]:
            if request.meta['proxy'] in proxy_cache.cache:
                proxy_cache.cache.remove(request.meta['proxy'])
            else:
                country = 'us' if spider.name.split('_')[-1] == 'au' else spider.name.split('_')[-1]
                redis_key = 'proxies_' + country if not spider.name.startswith('ebay') else 'ebay_proxies'

                # xc_offerlisting爬虫代理使用专用的
                if spider.name.startswith('xc_offerlisting_us'):
                    redis_key = 'offer_us'
                
                proxy_cache.get_proxy(redis_key)
                request.meta['proxy'] = random.choice(proxy_cache.cache)
            logger.info('status code: {0}, cache update, retry_times: {1}, url: {2}'.format(response.status, request.meta.get, request.url))
        return response
