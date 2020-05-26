import string
import random
# import logging
import urllib.parse

from useragent.firefoxua import FirefoxUA


# logger = logging.getLogger('useragent')


class RandomUserAgentMiddleware(object):
    """
    设置请求的user_agent
    """
    def __init__(self):
        self.user_agents = self.user_agent.ua

    @property
    def user_agent(self):
        return FirefoxUA('windows')

    def process_request(self, request):
        request.headers = {}
        parse_url = urllib.parse.urlsplit(request.url)
        request.headers.update({
            'User-Agent': self.user_agents,
        })

        header_params = [
            {'accept': '*/*'},
            {'accept-encoding': 'gzip, deflate'},
            {'accept-language': 'en'},
            {'cache-control': 'max-age=0'},
            {'Connection': 'keep-alive'},
            {'Upgrade-Insecure-Requests': '1'},
            {'TE': 'Trailers'},
            {"Content-Type": "application/x-www-form-urlencoded"},
            {'DNT': '1'},
            {'Host': parse_url.netloc},
            {'referer': request.url},

            {'accpect-type': 'utf-8'},
            {'Upgrade-type': 'none'},
            {'cache-type': 'any'},
            {'Origin-content': 'false'},
            {'content-from': 'google'},
            {'referer-rec': 'ture'}
        ]

        def rand_string():
            return ''.join(
                    [random.choice(string.ascii_letters) for _ in range(5)]
                )
        headers_must = [
            {rand_string(): rand_string()},
            {'Connection': 'close'}
        ]
        param_num = random.randint(0, len(header_params))
        new_header_params = random.sample(header_params, param_num)
        for param in new_header_params + headers_must:
            request.headers.update(param)

        # print('useragent_middleware: ', request.headers)
        # logger.debug(u'[当前UserAgent]: ' + user_agent)
