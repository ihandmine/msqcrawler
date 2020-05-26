from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerAuSpider(BestsellerSpiderBase):
    name = 'bestseller_au'
    base_url = 'https://www.amazon.com.au'
