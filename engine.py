import asyncio

from utils.misc import load_object, get_settings
from multihttp.request import Request
from multihttp.async_request import AsyncRequest
from multihttp.aio_request import AioRequest
from utils import logging

logger = logging.get_logger('engine')


class Engine(object):

    def __init__(self):
        self.settings = get_settings(key='DOWNLOADER_MIDDLEWARES')
        self.async_settings = get_settings(key="ASYNC_HTTP")
        self.async_method = get_settings(key="ASYNC_METHOD")
        self.request = None
        self.__response = None

    def inject(self, period='start'):
        if not isinstance(self.settings, dict):
            raise TypeError('[settings], Except to get dict type, but get %s' % type(self.settings).__name__)
        if period == 'start':
            sort_settings = dict(sorted(self.settings.items(), key=lambda d: d[1]))
        else:
            sort_settings = dict(sorted(self.settings.items(), key=lambda d: d[1], reverse=True))
        for middleware, status in sort_settings.items():
            if not status:
                continue
            downloader = load_object(middleware)()
            if not self.process_enable(downloader, period):
                break

    def process_enable(self, downloader, period):
        if period == 'start':
            if hasattr(downloader, 'process_request'):
                return downloader.process_request(self.request)
        elif period == 'end':
            if hasattr(downloader, 'process_response'):
                return downloader.process_response(self.response)

    @property
    def response(self):
        return self.__response

    def set_response(self, response):
        self.__response = response

    def runtime(self, url, *args, callback=None):
        if self.async_settings:
            if not callback:
                raise AssertionError('[define] asyncio request not found callback function')
            if self.async_method == "tornado":
                return self.tornado_runtime(url, args, callback)
        else:
            self.request = Request.request()
            self.request.url = url
            crawl = Request
            self.inject(period='start')
            self.set_response(crawl(self.request).response)
            self.inject(period='end')

    def tornado_runtime(self, url, args, callback=None):
        spider_iter, meta, callfunc = args

        def handler_response(response):
            self.set_response(response)
            self.inject(period='end')
            parse = getattr(spider_iter(self.__response, meta), callfunc)
            logger.success(logging.format(spider_iter, meta))
            callback(parse, spider_iter)

        self.request = AsyncRequest.request(url)
        crawl = AsyncRequest
        self.inject(period='start')
        future = crawl(self.request).fetch(callback=handler_response)
        return future

    async def async_runtime(self, url, *args, callback=None):
        spider_iter, meta, callfunc, message = args

        async def run(request):
            return await request.response

        async def task(_callback, request):
            ta = asyncio.create_task(run(request))
            ta.add_done_callback(_callback)
            await ta

        def handler_response_callback(future):
            response_text = future.result()
            self.set_response(response_text)
            self.inject(period='end')
            parse = getattr(spider_iter(self.__response, meta), callfunc)
            callback(parse, spider_iter)

        self.request = AioRequest()
        self.request.url = url
        self.inject(period='start')
        await task(handler_response_callback, self.request)
        return message
