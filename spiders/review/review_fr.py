from spiders.review.base import ReviewSpiderBase

import re


class ReviewFrSpider(ReviewSpiderBase):
    name = 'review_fr'
    base_url = 'https://www.amazon.fr'

    def get_review_votes(self, review):
        return ''.join(re.findall(r'\d+', ''.join(review.xpath("div[7]/div/span[3]/span/span[1]/span/text()").extract()).replace('Une', '1')))
