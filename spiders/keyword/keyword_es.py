from spiders.keyword.base import KeywordSpiderBase


class KeywordEsSpider(KeywordSpiderBase):
    name = 'keyword_es'
    base_url = 'https://www.amazon.es'
