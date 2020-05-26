import re
import time
from abc import ABC

from spider import Spider, FollowRequest
from item import Item


class QuestionSpiderBase(Spider, ABC):
    name = ''
    base_url = ''

    def parse(self):
        for elem in self.response.xpath('//div[@class="a-section askInlineWidget"]/div/div'):
            item = Item()
            item['asin'] = self.response.meta['asin']
            item['question_id'] = ''.join(elem.xpath('div//div[contains(@id, "question-")]/@id')).strip().split('-')[-1]
            item['votes'] = int(''.join(elem.xpath('div//ul[@class="vote voteAjax"]/li/@data-count')).strip())
            item['question'] = ''.join(elem.xpath('div//div[contains(@id, "question-")]/div/div[2]//span/text()')).strip()
            item['url'] = ''.join(elem.xpath('div//div[contains(@id, "question-")]/div/div[2]/a/@href')).strip()

            has_count = elem.xpath('div//span[@class="a-text-bold"]/text()')
            if has_count < 2:
                item['answer_count'] = 0
            else:
                item['answer_count'] = int(''.join(re.findall(r'\d+', ''.join(elem.xpath('div//div[contains(@id, "askSeeAllAnswersLink")]/a//text()')))).strip()) \
                    if elem.xpath('div//div[contains(@id, "askSeeAllAnswersLink")]/a') else 1
            item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            yield item
            
        next_url = ''.join(self.response.xpath('//*[@id="askPaginationBar"]/ul/li[@class="a-last"]/a/@href'))
        if next_url and len(next_url) > 20:
            yield FollowRequest((next_url, self.response, self.name))
