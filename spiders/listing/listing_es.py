from spiders.listing.base import ListingSpiderBase


class ListingEsSpider(ListingSpiderBase):
    name = 'listing_es'
    base_url = 'https://www.amazon.es'
