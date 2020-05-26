from spiders.review.base import ReviewSpiderBase


class ReviewUsSpider(ReviewSpiderBase):
    name = 'review_us'
    base_url = 'https://www.amazon.com'
