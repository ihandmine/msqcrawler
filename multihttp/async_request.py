import functools

from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class AsyncRequest(object):

    def __new__(cls, *args, **kwargs):
        cls._INSTANCE = super().__new__(cls)
        cls.http_client = AsyncHTTPClient()
        return cls._INSTANCE

    def __init__(self, request, method='GET'):
        if not request.method:
            request.method = method
            request.timeout = 20
        self._response = None
        self.url = None
        self.request = request

    @property
    def response(self):
        return self._response

    def handle_response(self, response):
        self._response = response

    def fetch(self, callback=None):
        callback = functools.partial(callback)
        return self.http_client.fetch(self.request, callback=callback, raise_error=False)

    @classmethod
    def request(cls, url):
        return HTTPRequest(url)

