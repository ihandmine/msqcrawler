from spiders.review.base import ReviewSpiderBase

import re


class ReviewDeSpider(ReviewSpiderBase):
    name = 'review_de'
    base_url = 'https://www.amazon.de'

    def get_review_rating(self, review):
        return ''.join(review.xpath(".//span[@class='a-icon-alt']/text()").extract()).split()[0].replace(',', '.')

    def get_review_votes(self, review):
        return ''.join(re.findall(r'\d+', ''.join(review.xpath("div[7]/div/span[3]/span/span[1]/span/text()").extract()).replace('Eine', '1')))
