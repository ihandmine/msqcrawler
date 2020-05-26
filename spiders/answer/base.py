import re
import time
from abc import ABC

from spider import Spider, FollowRequest
from item import Item
from spiders.utils import str_to_date


class AnswerSpiderBase(Spider, ABC):
    name = ''
    base_url = ''

    def parse(self):
        ask_date = self.response.xpath('//*[@id="a-page"]//div[contains(@class, "a-span-last")]/p[2]/text()')[0].strip().replace('asked on ', '')
        ask_local_date = str_to_date(ask_date, self.name.split('_')[-1].upper())
        for answer in self.response.xpath(".//div[contains(@id,'answer-')]"):
            item = Item()
            item['question_id'] = self.response.meta['question_id']
            item['ask_date'] = ask_date
            item['ask_local_date'] = ask_local_date
            item['answer_id'] = ''.join(answer.xpath("@id")).split('-')[-1]
            item['answer_content'] = ''.join(answer.xpath("./span[1]/text()")).strip()
            item['answer_author'] = ''.join(answer.xpath('.//span[@class="a-profile-name"]/text()'))[:64]
            item['answer_profile_id'] = ''.join(re.findall('profile/(.*?)/', ''.join(
                answer.xpath('.//a[@data-a-size="small"]/@href')[:1])))

            item['post_date'] = \
                ''.join(answer.xpath("./div/span[@class='a-color-tertiary aok-align-center']/text()")).replace(u'· ', '').strip()
            item['local_date'] = str_to_date(item['post_date'], self.name.split('_')[-1].upper())
            item.multi_filter_emoji(item, 'answer_content', 'answer_author')

            votes = ''.join(answer.xpath("div/div/span/text()") if answer.xpath(
                "div/div/span/text()") else answer.xpath("div/span/text()")).strip().split('of')
            if len(votes) > 1:
                item['helpful_count'] = ''.join(re.findall(r'\d+', votes[0]))
                item['votes'] = ''.join(re.findall(r'\d+', votes[1]))
            else:
                item['helpful_count'] = 0
                item['votes'] = 0
            item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            yield item
            
        next_url = ''.join(self.response.xpath('.//*[@id="askPaginationBar"]//li[@class="a-last"]/a/@href'))
        if next_url and len(next_url) > 20:
            yield FollowRequest((next_url, self.response.meta, self.name))
