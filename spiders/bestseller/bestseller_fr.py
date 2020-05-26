from spiders.bestseller.base import BestsellerSpiderBase


class BestsellerFrSpider(BestsellerSpiderBase):
    name = 'bestseller_fr'
    base_url = 'https://www.amazon.fr'
