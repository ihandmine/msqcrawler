from spiders.review.base import ReviewSpiderBase

import re


class ReviewItSpider(ReviewSpiderBase):
    name = 'review_it'
    base_url = 'https://www.amazon.it'

    def get_review_votes(self, review):
        return ''.join(re.findall(r'\d+', ''.join(review.xpath("div[7]/div/span[3]/span/span[1]/span/text()").extract()).replace('Una', '1')))
