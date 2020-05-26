import requests


class Request(object):
    """请求对象"""
    _INSTANCE = None

    def __new__(cls, *args, **kwargs):
        cls._INSTANCE = super().__new__(cls)
        cls.session = requests.Session()
        return cls._INSTANCE

    def __init__(self, request, method='GET'):
        if not request.method:
            request.method = method
            request.timeout = 20
        self.prep = self.session.prepare_request(request)

    @property
    def response(self):
        return self.session.send(self.prep)

    @classmethod
    def request(cls):
        return requests.Request()
