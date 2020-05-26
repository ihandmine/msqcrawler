from spiders.listing.base import ListingSpiderBase


class ListingNlSpider(ListingSpiderBase):
    name = 'listing_nl'
    base_url = 'https://www.amazon.nl'
