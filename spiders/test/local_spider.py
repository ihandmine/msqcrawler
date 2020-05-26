
from spider import Spider


class LocalSpider(Spider):
    name = 'local_spider'
    
    def parse(self):
        yield [{'topic': self.response.meta['topic']}, self.response.json()]
