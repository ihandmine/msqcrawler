import json
import re
import time
from abc import ABC

from item import Item
from spider import Spider, FollowRequest


class KeywordSpiderBase(Spider, ABC):
    name = ''
    base_url = ''

    def parse(self):
        page_ranking = 0
        for i, result_li in enumerate(self.response.xpath(".//li[contains(@id, 'result_')]") or self.response.xpath("//*[@data-index]")):
            item = Item()
            item['url'] = self.response.url
            item['page'] = self.response.meta['page']
            item['search_key'] = self.response.meta['keyword']

            # 20181106修改自然排名获取逻辑
            if result_li.xpath('.//span[contains(@class, "info-icon")]'):
                item['page_ranking'] = i + 1
            else:
                page_ranking += 1
                item['page_ranking'] = page_ranking
            item['pic_url'] = ''.join(result_li.xpath(".//img/@src")[:1]) \
                              or ''.join(result_li.xpath("div//a/img/@src")[:1])
            item['price'] = ''
            item['product_title'] = ''.join(result_li.xpath("div//a/@title"))[:1000]
            item['product_brand'] = ''.join(result_li.xpath("div//a[@title]/parent::div/following::div[1]/span[2]/text()"))[:100]
            item['asin'] = ''.join(result_li.xpath("@data-asin"))
            item['is_ad'] = 1 if result_li.xpath('.//span[contains(@class, "info-icon")]') else 0
            item['list_id'] = ''.join(result_li.xpath("./@data-index")) \
                              or ''.join(''.join(result_li.xpath("@id")).split('_')[-1:])
            item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

            # 去除表情
            item.multi_filter_emoji(item, 'product_brand', 'product_title')
            yield item

            # 衍生详情类(listing)任务
            info_url = self.base_url + '/dp/' + item['asin']
            meta = json.dumps({'asin': item['asin']})
            yield FollowRequest((info_url, meta, self.name))

            # 衍生产品评论(review)任务
            review_url = self.base_url + "/product-reviews/" + item['asin'] + "?sortBy=recent&pageNumber=1&reviewerType=all_reviews"
            meta = json.dumps({})
            yield FollowRequest((review_url, meta, self.name))

        # 20181124将一次性翻页改为一页一页翻
        path_url = ''.join(self.response.xpath(".//*[@id='pagnNextLink']/@href").extract()).strip() \
                   or ''.join(self.response.xpath(".//*[@class='a-last']//a/@href").extract()).strip()

        page = int(self.response.meta.get)
        max_page = int(self.response.meta.get)

        if path_url and page < max_page:
            meta = self.response.meta.copy()
            meta.update({'page': meta.get + 1})
            next_url = self.base_url + path_url
            yield FollowRequest((next_url, meta, self.name))
