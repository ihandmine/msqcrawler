from spiders.listing.base import ListingSpiderBase


class ListingCaSpider(ListingSpiderBase):
    name = 'listing_ca'
    base_url = 'https://www.amazon.ca'
