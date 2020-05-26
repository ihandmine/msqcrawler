import re

from lxml import etree

from utils.misc import get_settings


class Xpath(object):
    # _INSTANCE = None

    # def __new__(cls, *args, **kwargs):
    #     if not cls._INSTANCE:
    #         cls._INSTANCE = super().__new__(cls)
    #     return cls._INSTANCE

    def __init__(self, rule, x_res):
        self.rule = rule
        self.x_res = x_res

    def __len__(self):
        return len(self.xpath)

    def __iter__(self):
        if not len(self.xpath) > 1:
            raise StopIteration("[define] Iter object length is 1")
        return iter(self.xpath)
    #
    # def __next__(self):
    #     for item in self.xpath:
    #         yield item

    @property
    def xpath(self):
        if not hasattr(self, 'x_res'):
            raise ValueError('[define] Xpath not to be instanced')
        _result = self.x_res.xpath(self.rule)
        # if not _result:
        #     print('[define] Xpath not found content, rule: %s' % self.rule)
        return _result

    def extract(self):
        return self.xpath

    def extract_first(self):
        return self.xpath[0]


class Response(object):

    _INSTANCE = None

    def __new__(cls, *args, **kwargs):
        cls._INSTANCE = super().__new__(cls)
        cls.async_http = get_settings(key="ASYNC_HTTP")
        return cls._INSTANCE

    def __init__(self, response, meta):
        self.response = response
        self.meta_source = meta
        self._text = ''
        self.set_text()
        self.x_res = etree.HTML(self._text)

    def set_text(self):
        if isinstance(self.response, bytes):
            self._text = self.response.decode('utf-8')
        elif self.async_http:
            self._text = self.response.body.decode('utf-8')
        else:
            self._text = self.response.text

    def regex(self, pattern, text=None, flags=0):
        if text:
            _result = re.findall(pattern, text, flags)
        else:
            _result = re.findall(pattern, self._text)
        return _result

    def xpath(self, rule):
        return Xpath(rule, self.x_res)

    @property
    def meta(self):
        return dict(self.meta_source)

    @property
    def text(self):
        return self._text

    @property
    def body(self):
        return self.response.content

    def json(self):
        return self.response.json()

    @property
    def url(self):
        return self.response.url

    @property
    def encoding(self):
        return self.response.encoding

    @property
    def headers(self):
        return self.response.headers
