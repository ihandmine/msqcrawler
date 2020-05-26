from spiders.review.base import ReviewSpiderBase


class ReviewUkSpider(ReviewSpiderBase):
    name = 'review_uk'
    base_url = 'https://www.amazon.co.uk'
