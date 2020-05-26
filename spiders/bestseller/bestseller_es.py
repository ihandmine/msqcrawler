from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerEsSpider(BestsellerSpiderBase):
    name = 'bestseller_es'
    base_url = 'https://www.amazon.es'
