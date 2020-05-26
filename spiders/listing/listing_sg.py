from spiders.listing.base import ListingSpiderBase


class ListingSgSpider(ListingSpiderBase):
    name = 'listing_sg'
    base_url = 'https://www.amazon.sg'
