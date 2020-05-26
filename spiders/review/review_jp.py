from spiders.review.base import ReviewSpiderBase


class ReviewJpSpider(ReviewSpiderBase):
    name = 'review_jp'
    base_url = 'https://www.amazon.co.jp'

    def get_review_rating(self, review):
        return ''.join(review.xpath(".//span[@class='a-icon-alt']/text()").extract()).replace(u'5つ星のうち', '')

    def get_author(self, review):
        return ''.join(review.xpath(".//span[@class='a-profile-name']/text()").extract())[:50] or \
               ''.join(review.xpath(".//a[@data-hook='review-author']/text()").extract()).strip()[:50]

    def get_author_link(self, review):
        return self.base_url + ''.join(review.xpath(".//a[@class='a-profile']/@href").extract()) or \
               self.base_url + ''.join(review.xpath(".//a[@data-hook='review-author']/@href").extract())

    def get_review_date(self, review):
        return ' '.join(''.join(review.xpath(".//span[@data-hook='review-date']/text()").extract()).split(' ')[-3:]).replace(u'に日本でレビュー済み', '')

    def get_nowstar(self):
        return ''.join(self.response.xpath(
                ".//*[@id='cm_cr-product_info']//span[@class='a-icon-alt']/text()").extract()).replace(u'5つ星のうち', '')
