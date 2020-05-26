from spiders.question.base import QuestionSpiderBase


class QuestionEsSpider(QuestionSpiderBase):
    name = 'question_es'
    base_url = 'https://www.amazon.es'
