from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerUkSpider(BestsellerSpiderBase):
    name = 'bestseller_uk'
    base_url = 'https://www.amazon.co.uk'
