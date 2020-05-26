from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerCaSpider(BestsellerSpiderBase):
    name = 'bestseller_ca'
    base_url = 'https://www.amazon.ca'
