from spiders.listing.base import ListingSpiderBase


class ListingAuSpider(ListingSpiderBase):
    name = 'listing_au'
    base_url = 'https://www.amazon.com.au'
