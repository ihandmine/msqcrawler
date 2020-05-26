from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerUsSpider(BestsellerSpiderBase):
    name = 'bestseller_it'
    base_url = 'https://www.amazon.it'
