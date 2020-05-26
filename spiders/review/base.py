import re
import time
from abc import ABC

from datetime import datetime, timedelta

from spider import Spider, FollowRequest
from item import Item
from spiders.utils import str_to_date


class ReviewSpiderBase(Spider, ABC):
    name = ''
    base_url = ''

    def parse(self):
        date_in_page = datetime.now()
        for review in self.response.xpath(".//div[@id='cm_cr-review_list']/div[@data-hook='review']/div"):
            item = Item()
            item['pageurl'] = self.response.url
            item['asin'] = self.response.meta['asin']
            item['pagetitle'] = ''.join(self.response.xpath(".//title/text()")).strip()[:500]
            item['review_rating'] = self.get_review_rating(review)
            item['review_title'] = ''.join(review.xpath(".//a[@data-hook='review-title']/text()"))[:255]
            item['review_title_url'] = self.base_url + ''.join(review.xpath(".//a[@data-hook='review-title']/@href"))
            item['author'] = self.get_author(review)
            item['author_linkurl'] = self.get_author_link(review)
            item['author_profileid'] = ''.join(re.findall('profile/(.+?)/', item['author_linkurl'])) or \
                                       ''.join(re.findall('profile/(.+)', item['author_linkurl']))
            item['classify_asin'] = re.search(
                'product-reviews/(.+?)/',
                ''.join(review.xpath(".//a[@data-hook='format-strip']/@href"))).group(1) \
                if re.search(
                'product-reviews/(.+?)/',
                ''.join(review.xpath(".//a[@data-hook='format-strip']/@href"))
            ) else item['asin']
            item['countrycode'] = self.name.split('_')[-1].upper()
            item['review_date'] = self.get_review_date(review)
            item['local_date'] = str_to_date(item['review_date'], item['countrycode'])
            item['w_pro_color'] = ' '.join(review.xpath(".//a[@data-hook='format-strip']/text()")).strip()[:100]
            item['verified_purchase'] = 1 if ''.join(
                review.xpath(".//span[@data-hook='avp-badge']/text()")) else 0
            item['review_text'] = '\n'.join(review.xpath(".//span[@data-hook='review-body']//text()"))
            item['w_comments'] = ''.join(
                review.xpath(".//span[@class='review-comment-total aok-hidden']/text()"))

            # 20181027  ???
            item['review_votes'] = self.get_review_votes(review)

            item['nowstar'] = self.get_nowstar()
            item['review_id'] = ''.join(review.xpath("parent::div/@id"))
            item['w_now'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            date_in_page = item['local_date']

            # 过滤表情
            item.multi_filter_emoji(item, 'pagetitle', 'review_title', 'author', 'review_text', 'w_pro_color')

            yield item

        try:
            path_url = self.response.xpath(".//*[@id='cm_cr-pagination_bar']/ul/li[@class='a-last']/a/@href")[0]
        except:
            path_url = None

        date = self.response.meta.get

        if path_url and (date == 0 or date_in_page > (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1))):
            meta = self.response.meta
            meta.update({'page': meta.get + 1})
            next_url = self.base_url + path_url
            # print next_url
            yield FollowRequest((next_url, meta, self.name))

    def get_review_votes(self, review):
        return ''.join(re.findall(r'\d+', ''.join(
                review.xpath("div[7]/div/span[3]/span/span[1]/span/text()")).replace('One', '1')))

    def get_review_rating(self, review):
        return ''.join(review.xpath(".//span[@class='a-icon-alt']/text()")).split()[0]

    def get_author(self, review):
        return ''.join(review.xpath(".//span[@class='a-profile-name']/text()")).strip()[:50]

    def get_author_link(self, review):
        return self.base_url + ''.join(review.xpath(".//a[@class='a-profile']/@href"))

    def get_review_date(self, review):
        return ' '.join(
                ''.join(review.xpath(".//span[@data-hook='review-date']/text()")).split(' ')[-3:])

    def get_nowstar(self):
        return ''.join(
                self.response.xpath(".//*[@id='cm_cr-product_info']//span[@class='a-icon-alt']/text()")
            ).split()[0]
