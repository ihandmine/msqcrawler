# encoding: utf-8
import random
import requests
import logging

from .proxy_cache import proxy_cache


logger = logging.getLogger('cookiecache')


class Cookie(object):
    '''
    cookie 获取的具体实现
    '''
    def __init__(self):
        self.urldict = {
            'au': 'https://www.amazon.com.au/',
            'us': 'https://www.amazon.com/',
            'ca': 'https://www.amazon.ca/',
            'de': 'https://www.amazon.de/',
            'es': 'https://www.amazon.es/',
            'fr': 'https://www.amazon.fr/',
            'in': 'https://www.amazon.in/',
            'it': 'https://www.amazon.it/',
            'jp': 'https://www.amazon.co.jp/',
            'mx': 'https://www.amazon.com.mx/',
            'uk': 'https://www.amazon.co.uk/',
        }
        self.countryCode = {
            'au': '2600',
            'us': '99571',
            'ca': 'A0E 2Z0',
            'de': '01099',
            'es': '04004',
            'fr': '75003',
            'in': '744304',
            'it': '03100',
            'jp': '197-0825',
            'mx': '01139',
            'uk': 'AB101AF',
        }
        self.codeCountry = dict(zip(
                            self.countryCode.values(),
                            self.countryCode.keys()
                ))
        self.cookiecache = []
        self.user_agent_random = 'Mozilla/5.0 (%(num1)s; %(win)s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%(num2)d.%(num3)d.%(num4)d.%(num5)d'
        self.base_url = 'gp/delivery/ajax/address-change.html'

    def get_cookie_cache(self, country):
        if len(self.cookiecache) < 1:
            cookie = self.getNewCookie(country)
            logger.info('get cookie : %s ' % cookie)
            self.cookiecache.append(cookie)

    def rand_headers(self):
        lst = [
            'Windows NT 6.1',
            'Windows NT 6.2',
            'Windows NT 6.3',
            'Windows NT 10.0',
        ]
        lst2 = [
            'Win64; x64',
            'WOW64',
        ]
        user_agent = self.user_agent_random % {
            "num1": random.choice(lst),
            "win": random.choice(lst2),
            "num2": random.randint(40, 70),
            "num3": random.randint(0, 9),
            "num4": random.randint(1000, 9999),
            "num5": random.randint(0, 9),
        }
        return user_agent

    def getNewCookie(self, country):
        '''
        香港: proxies = {'http': 'http://192.168.5.71:3128', 'https': 'https://192.168.5.71:3128'}
        美国: proxies = {'http': 'http://172.16.186.206:7777', 'https': 'https://172.16.186.206:7777'}
        美国: proxies = {'http': 'http://172.16.186.204:7777', 'https': 'https://172.16.186.204:7777'}

        :param country:
        :return: cookiedic
        '''
        data = {
            'locationType': 'LOCATION_INPUT',
            'zipCode': self.countryCode[country],
            'storeContext': 'gateway',
            'deviceType': 'web',
            'pageType': 'Search',
            'actionSource': 'glow',
        }
        redis_key = 'proxies_' + country
        while True:
            try:
                proxy_cache.get_proxy(redis_key)
                proxy = random.choice(proxy_cache.cache)
                proxies = {'http': proxy, 'https': proxy}
                headers = {'User-Agent': self.rand_headers()}
                resp = requests.post(self.urldict[country] + self.base_url, data=data, headers=headers, proxies=proxies, timeout=30)
            except Exception as e:
                proxy_cache.cache.remove(proxy)
                logger.info(u'获取session-id error: {}, 正在重新获取'.format(e))
                continue
            if dict(resp.cookies):
                break
            else:
                logger.info(u'没有获取到session-id, 正在重新获取')
        ubin = "{0}-{1}-{2}".format(random.randint(100, 160), random.randint(1000000, 9999999), random.randint(1000000, 9999999))
        # ubin = f'{random.randint(100, 160)}-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}' --- python3 语法
        # cookie = f"session-id={dict(resp.cookies).get('session-id')}; ubin-main={ubin}" -- headers类cookie写法
        cookiedic = {
            'session-id': dict(resp.cookies).get('session-id'),
            'ubin-main': ubin
        }
        return cookiedic


cookie_cache = Cookie()
