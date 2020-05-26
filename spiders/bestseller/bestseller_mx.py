from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerMxSpider(BestsellerSpiderBase):
    name = 'bestseller_mx'
    base_url = 'https://www.amazon.com.mx'
