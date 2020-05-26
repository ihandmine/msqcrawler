import json
import re
import time

from spiders.bestseller.base import BestsellerSpiderBase

from item import Item
from spider import FollowRequest


class BestsellerJpSpider(BestsellerSpiderBase):
    name = 'bestseller_jp'
    base_url = 'https://www.amazon.co.jp'

    def parse(self):
        self.response.meta['page'] = 1 if not self.response.meta.get else self.response.meta['page']
        flag = True
        for bestsellers in self.response.xpath('//*[@id="zg_left_col1"]//div[@class="zg_itemRow"]'):
            flag = False
            item = Item()
            item['cate_id'] = ''
            item['cate_name'] = ''
            item['cate_url'] = self.response.url
            try:
                item['asin'] = str(json.loads(bestsellers.xpath("./div/@data-p13n-asin-metadata")[0])['asin'])
            except:
                continue
            item['ranking'] = ''.join(
                bestsellers.xpath("div//span[@class='zg_rankNumber']/text()")).strip().replace('.', '') or 0
            item['pic_url'] = ''.join(bestsellers.xpath('.//img[@class="a-thumbnail-left"]/@src'))
            item['title'] = ''.join(bestsellers.xpath('.//img[@class="a-thumbnail-left"]/@alt'))
            item['stars'] = ''.join(bestsellers.xpath(".//i/span/text()")).split()[-1] if \
                            ''.join(bestsellers.xpath(".//i/span/text()")) else 0
            item['review_counts'] = ''.join(
                bestsellers.xpath('.//a[@class="a-size-small a-link-normal"]/text()')).replace(',', '') or 0
            item['price'] = ''.join(bestsellers.xpath('.//span[@class="p13n-sc-price"]/text()'))
            item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            item.multi_filter_emoji(item, 'title')
            yield item
        if flag and self.response.meta['page'] == 1:
            for bestsellers in self.response.xpath(".//li[@class='zg-item-immersion']"):
                item = Item()
                item['cate_id'] = ''
                item['cate_name'] = ''
                item['cate_url'] = self.response.url
                item['asin'] = ''.join(re.findall('/dp/(.*?)/ref=zg_bs', ''.join(
                    bestsellers.xpath(".//span[@class='aok-inline-block zg-item']/a/@href")))[:1])
                item['ranking'] = bestsellers.xpath(
                    ".//span[@class='zg-badge-text']/text()")[0].strip().replace('#', '') or 0
                item['pic_url'] = ''.join(bestsellers.xpath(".//img/@src"))
                item['title'] = ''.join(bestsellers.xpath(".//img/@alt"))[:250]
                item['stars'] = ''.join(bestsellers.xpath(".//a[1]/@title")).split()[-1] \
                    if bestsellers.xpath(".//a[1]/@title") else 0
                item['review_counts'] = bestsellers.xpath(
                    ".//a[2]/text()")[0].replace(',', '') if bestsellers.xpath(".//a[2]/text()")[0] else 0
                item['price'] = ''.join(
                    bestsellers.xpath(".//span[@class='a-size-base a-color-price']//text()"))
                item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                if item['stars'] == '':
                    item['stars'] = \
                        ''.join(bestsellers.xpath(".//i/span/text()")).split()[-1] \
                        if bestsellers.xpath(".//i/span/text()") else 0
                    item['review_counts'] = ''.join(
                        bestsellers.xpath(".//span/div/span/div[2]/a[2]/text()")) or 0
                item.multi_filter_emoji(item, 'title')
                yield item
            next_url = self.response.xpath('.//li[@class="a-last"]/a/@href')[0]
            if next_url:
                yield FollowRequest((next_url, self.response.meta, self.name))
        if flag and self.response.meta['page'] == 2:
            next_url = self.response.url.split('?pg')[0] + "?pg=" + str(self.response.meta['page'])
            yield FollowRequest((next_url, self.response.meta, self.name))
        if not flag:
            self.response.meta['page'] += 1
            next_url = self.response.url.split('?pg')[0] + "?pg=" + str(self.response.meta['page'])
            if '#' in self.response.url:
                next_url = self.response.url.split('#')[0] + '?pg=' + str(self.response.meta['page'])
            if self.response.meta['page'] < 6:
                yield FollowRequest((next_url, self.response.meta, self.name))
