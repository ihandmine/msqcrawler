from spiders.review.base import ReviewSpiderBase


class ReviewCaSpider(ReviewSpiderBase):
    name = 'review_ca'
    base_url = 'https://www.amazon.ca'
