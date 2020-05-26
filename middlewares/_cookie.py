
import logging

from .retry import PtxRetryMiddleware
from .cookie_cache import cookie_cache


logger = logging.getLogger('cookie')


class BaseCookieMiddleware(object):
    """
    给请求加上cookie, 定位信息
    """

    def __init__(self, settings):
        self.use_cookie = settings.getbool('USE_COOKIES')
        self._retry = getattr(PtxRetryMiddleware(settings), '_retry')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        raise NotImplementedError

    def process_response(self, request, response, spider):
        raise NotImplementedError


class CookiesMiddleware(BaseCookieMiddleware):
    '''
    cookie 改变定位的具体实现
    '''

    def process_request(self, request, spider):
        if self.use_cookie:
            try:
                self.country = "us" if spider.name.split('_')[-1] == "au" else spider.name.split('_')[-1]
                cookie_cache.get_cookie_cache(self.country)
                if cookie_cache.cookiecache:
                    cookie = cookie_cache.cookiecache[0]
            except Exception as e:
                spider.crawler.engine.close_spider(spider, 'No cookie information was obtained %s' % e)
            else:
                request.cookies = cookie

    def process_response(self, request, response, spider):
        if spider.name.endswith('_au') or spider.name.startswith('xc_offerlisting_'):
            return response

#        if self.use_cookie:
#            addre = ''.join(response.xpath('//*[@id="glow-ingress-line2"]/text()').extract())
#            address = re.search(cookie_cache.countryCode[self.country], addre) or ""
#            if address:
#                address = address.group()
#            logger.info(u'当前cookie定位信息为: {}'.format(cookie_cache.codeCountry.get(address)))
#            if not address:
#                reason = u'当前cookie定位信息错误'
#                if addre:
#                    try:
#                        cookie_cache.cookiecache = []
#                    except Exception as e:
#                        # print(u'移除失败 : %s' % e)
#                        pass
#                    logger.info(u'移除已过期存在cookiecache中的cookie')
#                reply = self._retry(request, reason, spider)
#                if reply is not None:
#                    return reply
#                else:
#                    raise IgnoreRequest
        return response

