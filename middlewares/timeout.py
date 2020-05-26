import logging

from twisted.internet.error import TimeoutError

logger = logging.getLogger('Timeout')


class TimeoutMiddleware(object):
    """
    超时处理
    """

    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutError):
            if 'proxy' in request.meta:
                logger.info(u' %s 请求超时，当前代理为 %s' % (request.url, request.meta['proxy']))
            return request
