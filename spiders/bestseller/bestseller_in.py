from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerInSpider(BestsellerSpiderBase):
    name = 'bestseller_in'
    base_url = 'https://www.amazon.in'
