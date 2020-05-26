from spiders.review.base import ReviewSpiderBase


class ReviewAuSpider(ReviewSpiderBase):
    name = 'review_au'
    base_url = 'https://www.amazon.com.au'
