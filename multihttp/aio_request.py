import aiohttp


class AioRequest(object):
    """请求对象"""
    _INSTANCE = None

    def __new__(cls, *args, **kwargs):
        cls._INSTANCE = super().__new__(cls)
        return cls._INSTANCE

    def __init__(self, **kwargs):
        self.url = None
        self.headers = None
        self.timeout = 20
        self.proxy = None
        self.allow_redirects = True
        self._response = None
        self.kwargs = kwargs

    @property
    async def response(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url,
                                   headers=self.headers,
                                   timeout=self.timeout,
                                   allow_redirects=self.allow_redirects,
                                   **self.kwargs) as response:
                try:
                    self._response = await response.text(encoding='utf-8')
                except:
                    raise Exception('request error')
                return self._response.encode('utf-8')

    @property
    async def fetch(self):
        async with aiohttp.request('GET',
                                   url=self.url,
                                   headers=self.headers,
                                   # timeout=self.timeout,
                                   allow_redirects=self.allow_redirects,
                                   **self.kwargs) as resp:
            assert resp.status == 200
            print(await resp.text())
            return await resp.text()

    @property
    def _headers(self):
        return self.headers

    @property
    def _url(self):
        return self.url

    @property
    def _proxies(self):
        return self.proxy

    @property
    def _time_out(self):
        return self.timeout

    @property
    def _allow_redirect(self):
        return self.allow_redirects
