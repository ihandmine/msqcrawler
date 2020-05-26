from spiders.listing.base import ListingSpiderBase


class ListingUsSpider(ListingSpiderBase):
    name = 'listing_us'
    base_url = 'https://www.amazon.com'
