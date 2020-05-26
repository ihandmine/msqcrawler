

class RollbackProxyMiddleware(object):
    def set_splash_proxy(self, request):
        if 'proxy' in request.meta:
            return

        if 'splash' in request.meta and 'proxy' in request.meta['splash']['args']:
            request.meta['proxy'] = request.meta['splash']['args']['proxy']

    def process_response(self, request, response, spider):
        self.set_splash_proxy(request)

        return response

    def process_exception(self, request, exception, spider):
        self.set_splash_proxy(request)
