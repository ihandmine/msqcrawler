import re
import logging

from scrapy.exceptions import IgnoreRequest
from retry import PtxRetryMiddleware
from ..exception import IpError

logger = logging.getLogger('verify')


class VerifyMiddleware(object):
    """
    验证程序是否被判定为爬虫
    """

    def __init__(self, settings):
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        self._retry = getattr(PtxRetryMiddleware(settings), '_retry')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        raise NotImplementedError


class AmazonVerifyMiddleware(VerifyMiddleware):
    """
    亚马逊, ebay网站的验证
    """

    def process_response(self, request, response, spider):
        reason = ''
        if response.xpath("*//form[@action='/errors/validateCaptcha']/div/div/div/div/img") or response.xpath('//*[@id="frameBot"]'):
            reason = IpError()
            if 'proxy' in request.meta:
                logger.info(u'被判定为爬虫, cache update, retry_times: {0}, url: {1}, proxy: {2}'.format(request.meta.get, request.url, request.meta['proxy']))
            else:
                logger.info(u'本地网络被判定为爬虫')

        if not re.search('Amazon|amazon|ebay', response.body):
            reason = IpError()
            if request.url.startswith('https://cgi.ebay') or request.url.endswith('cm_cr_dp_d_pdp'):
                if len(response.body) < 2000:
                    reason = ''
                    logger.info(u'无效链接: {0}'.format(request.url))
            else:
                logger.info(u'ip需要验证, cache update, retry_times: {0}, url: {1}, proxy: {2}'.format(request.meta.get, request.url, request.meta['proxy']))

        if response.url.startswith('https://ls.madisonvillecisd.org') \
            or response.url.startswith('https://gateway.zscloud') \
            or response.url.startswith('https://mobilefilter') \
            or response.url.startswith('https://rocket.newpal.k12.in.us'):
            reason = IpError()

        if isinstance(reason, IpError):
            reply = self._retry(request, reason, spider)
            if reply is not None:
                return reply
            else:
                raise IgnoreRequest
        return response
