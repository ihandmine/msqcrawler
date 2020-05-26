from multihttp.response import Response


class Spider(object):
    name = ''

    def __init__(self, resp, meta=None):
        self.meta = meta
        self._response = Response(resp, self.meta)

    @property
    def response(self):
        return self._response

    def parse(self):
        raise NotImplementedError


class FollowRequest(list):
    pass
