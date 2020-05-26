import re


class Item(dict):

    def filter_emoji(self, desstr, restr=''):
        """过滤emoj表情"""
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    def multi_filter_emoji(self, obj, *args):
        """批量对obj的成员变量过滤emoj表情"""
        for arg in args:
            obj[arg] = self.filter_emoji(obj[arg])



