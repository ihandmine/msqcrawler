from item import Item

from spider import Spider, FollowRequest


class QiushiSpider(Spider):
    name = 'qiushi'
    base_url = 'https://www.qiushibaike.com'

    def parse(self):
        for div in self.response.xpath("//div[contains(@id, 'qiushi_tag')]"):
            item = Item()
            item['username'] = ''.join(div.xpath(".//h2/text()")).strip()
            item['content'] = ''.join(div.xpath(".//div[@class='content']/span/text()")).strip()
            item['laugh_count'] = ''.join(div.xpath('.//i[@class="number"]/text()')[0]).strip()
            item['review_count'] = ''.join(div.xpath('.//i[@class="number"]/text()')[1]).strip()
            item['sex'] = 0 if 'woman' in ''.join(div.xpath(".//div[contains(@class, 'articleGender')]/@class")) else 1
            item['age'] = ''.join(div.xpath(".//div[contains(@class, 'articleGender')]/text()")).strip()

            yield item

        next_url = self.base_url + self.response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').extract_first()
        page_num = int(self.response.regex(r'/(\d+)/', next_url)[0])
        if next_url and page_num < 10:
            yield FollowRequest((next_url, self.response.meta, self.name))







