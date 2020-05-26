import re
import time
from abc import ABC

from spider import Spider, FollowRequest

from item import Item


class BestsellerSpiderBase(Spider, ABC):
    name = ''
    base_url = ''

    def parse(self):
        for bestsellers in self.response.xpath(".//li[@class='zg-item-immersion']"):
            item = Item()
            item['cate_id'] = ''
            item['cate_name'] = ''
            item['result_tb'] = self.response.meta['result_tb']
            item['task_id'] = ''.join(self.response.meta.get.split(':')[-1:])
            item['cate_url'] = self.response.url
            item['asin'] = ''.join(re.findall('/dp/(.*?)/ref=zg_bs', ''.join(bestsellers.xpath(".//span[@class='aok-inline-block zg-item']/a/@href")))[:1])
            item['ranking'] = bestsellers.xpath(".//span[@class='zg-badge-text']/text()")[0].strip().replace('#', '') or 0
            item['pic_url'] = ''.join(bestsellers.xpath(".//img/@src"))
            item['title'] = ''.join(bestsellers.xpath(".//img/@alt"))[:250]
            item['stars'] = ''.join(bestsellers.xpath(".//a[1]/@title")).split()[0].replace(',', '.') \
                if bestsellers.xpath(".//a[1]/@title") else 0
            item['review_counts'] = bestsellers.xpath(".//a[2]/text()")[0].replace(',', '') if bestsellers.xpath(".//a[2]/text()") else 0
            item['price'] = ''.join(
                bestsellers.xpath(".//span[@class='a-size-base a-color-price']//text()"))
            item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if item['stars'] == '':
                item['stars'] = \
                    ''.join(bestsellers.xpath(".//i/span/text()")).split()[0] \
                    if bestsellers.xpath(".//i/span/text()") else 0
                item['review_counts'] = ''.join(
                    bestsellers.xpath(".//span/div/span/div[2]/a[2]/text()")) or 0
            item.multi_filter_emoji(item, 'title')
            yield item
        next_url = self.response.xpath('.//li[@class="a-last"]/a/@href')[0]
        if next_url:
            yield FollowRequest((next_url, self.response.meta, self.name))

