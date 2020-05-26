from spiders.listing.base import ListingSpiderBase


class ListingUkSpider(ListingSpiderBase):
    name = 'listing_uk'
    base_url = 'https://www.amazon.co.uk'
