from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerDeSpider(BestsellerSpiderBase):
    name = 'bestseller_de'
    base_url = 'https://www.amazon.de'
