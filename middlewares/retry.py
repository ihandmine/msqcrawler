# -*- coding: utf-8 -*-

import re
import logging
import random


from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.python import global_object_name

from proxy_cache import proxy_cache

from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.web.client import ResponseFailed
from ..exception import IpError


logger = logging.getLogger('retry')


class PtxRetryMiddleware(RetryMiddleware):
    """
    建议代替原来的RetryMiddleware
    """

    def cheack_redirect(self, request, response, spider, line_place=''):
        """
        检查重定向的链接是否为合法404,合法返回True,不合法返回False,规则如下:
            1. 若没有重定向, 判定合法
            2. 若有重定向,且重定向后的url不含www.amazon的url, 判定不合法
            3. 若有重定向,且重定向后的url含www.amazon,且含有'/hz/'的url, 判定为合法
            4. 若有重定向,且重定向后的url含www.amazon,且和原url相同, 判定合法
            5. 若有重定向,且重定向后的url含www.amazon,且含/gp/errors/404.html, 判定合法
            6. 若返回的页面是空页面即len()小于1000,判定为不合法
            7. 其它未知重定向预警,且判定不合法
        """
        redirect_url_lst = request.meta.get
        if redirect_url_lst:
            if 'www.amazon' in request.url: 
                if '/hz/' in request.url:
                    return True
                elif request.url==redirect_url_lst[0]:
                    return True
                elif '/gp/errors/404.html' in request.url:
                    return True
                elif '/dp/' in request.url and len(response.body) <= 1000:
                    return False
                elif '/product-reviews/' in response.url and response.status == 404:
                    return ture
                else:
                    try:
                        pass
                        # ding(request, response, spider, line_place)
                    except:
                        logging.info('钉钉报警出错')
                    return False
            else:
                return False
        if '/dp/' in request.url and len(response.body) <= 1000:
            return False
        if not re.search('A|amazon', response.body):
            if request.url.endswith('cm_cr_dp_d_pdp'):
                return True
            else:
                return False
        if "?pg" in request.url:
            return False
        return True

    def process_response(self, request, response, spider):
        if response.status >= 400 and response.status < 500:
            if not spider.name.startswith('ebay_'):
                if self.cheack_redirect(request, response, spider, line_place='404'):
                    logger.info(u'状态码:{0}, 丢弃链接:{1}'.format(response.status, response.url))
                else:
                    redirect_url_lst = request.meta.get
                    if redirect_url_lst:
                        logging.info(u'状态码:{0}, 重定向异常链接:{1}'.format(response.status, response.url))
                        request._set_url(redirect_url_lst[0])
                        logging.info(u'将重定向链接修正为 %s' % redirect_url_lst[0])
                    else:
                        logging.info(u'状态码:{0}, 判定爬虫,进行重试:{1}'.format(response.status, response.url))
                    reply = self._retry(request, IpError(), spider)

                    if reply is not None:
                        return reply
                raise IgnoreRequest
            else:
                if not re.search('ebay', response.body):
                    reply = self._retry(request, IpError(), spider)
                    if reply is not None:
                        return reply
                    else:
                        raise IgnoreRequest
        if response.status >= 300 and response.status < 400 and response.url.startswith('https://www.ebay'):
            logger.info(u'发现ebay充定向链接: {0}'.format(response.url))
            raise IgnoreRequest
        return super(PtxRetryMiddleware, self).process_response(request, response, spider)

    def _retry(self, request, reason, spider):
        if 'proxy' in request.meta:
            logger.debug(request.meta['proxy'])

        retries = request.meta.get + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']
        if isinstance(reason, (defer.TimeoutError, TimeoutError, DNSLookupError,
                               ConnectionRefusedError, ConnectionDone, ConnectError, ConnectionLost,
                               TCPTimedOutError, ResponseFailed, IOError, TunnelError, IpError)):
            if request.meta['proxy'] in proxy_cache.cache:
                proxy_cache.cache.remove(request.meta['proxy'])
            else:
                if proxy_cache.cache:
                    request.meta['proxy'] = random.choice(proxy_cache.cache)
        logger.info(u'reason: {0}, cache update, retry_times: {1}'.format(
                            # ''.join(re.findall('\.(.*?Error)', str(type(reason)), re.I)),
                            reason,
                            request.meta.get))

        stats = spider.crawler.stats
        if retries <= retry_times:
            if retries == retry_times:
                retries = 0
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)

            # 2018-09-04 添加去除https://mobilefilter
            if not request.url.startswith('https://www.amazon') and \
               not request.url.startswith('https://www.ebay') and \
               not request.url.startswith('https://feedback.ebay') and \
               not request.url.startswith('http://feedback.ebay') and \
               not request.url.startswith('https://offer.ebay') and \
               not request.url.startswith('https://cgi.ebay'):
                redirect_url = retryreq.meta.get[0]
                retryreq._set_url(redirect_url)
                logging.info(u'发现异常链接:%s,' % request.url)
                logging.info(u'将异常链接修正为 %s' % redirect_url)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.debug(
                "Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                {'request': request, 'retries': retries, 'reason': reason},
                extra={'spider': spider})
