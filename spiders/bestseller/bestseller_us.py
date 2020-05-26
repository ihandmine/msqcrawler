from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerUsSpider(BestsellerSpiderBase):
    name = 'bestseller_us'
    base_url = 'https://www.amazon.com'
