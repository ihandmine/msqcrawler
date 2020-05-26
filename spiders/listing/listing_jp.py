import re

from spiders.listing.base import ListingSpiderBase


class ListingJpSpider(ListingSpiderBase):
    name = 'listing_jp'
    base_url = 'https://www.amazon.co.jp'

    def get_star_percent(self, item):
        html = self.response.text
        item['five_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[1]/td[3]//a//text()").extract()[:-1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="レビューの(.{0,20})に星5つが付いています。" href="', html, re.S)[:1]).strip().replace('\xef\xbc\x85', '%') \
            or ''.join(re.findall(r'<a class="a-link-normal" title="5 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 5 stars"', html, re.S)[:1]).strip()

        item['four_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[2]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="レビューの(.{0,20})に星4つが付いています。" href="', html, re.S)[:1]).strip().replace('\xef\xbc\x85', '%') \
            or ''.join(re.findall(r'<a class="a-link-normal" title="4 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 4 stars"', html, re.S)[:1]).strip()

        item['three_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[3]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="レビューの(.{0,20})に星3つが付いています。" href="', html, re.S)[:1]).strip().replace('\xef\xbc\x85', '%') \
            or ''.join(re.findall(r'<a class="a-link-normal" title="3 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 3 stars"', html, re.S)[:1]).strip()

        item['two_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[4]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="レビューの(.{0,20})に星2つが付いています。" href="', html, re.S)[:1]).strip().replace('\xef\xbc\x85', '%') \
            or ''.join(re.findall(r'<a class="a-link-normal" title="2 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 2 stars"', html, re.S)[:1]).strip()

        item['one_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[5]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="レビューの(.{0,20})に星1つが付いています。" href="', html, re.S)[:1]).strip().replace('\xef\xbc\x85', '%') \
            or ''.join(re.findall(r'<a class="a-link-normal" title="1 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 1 stars"', html, re.S)[:1]).strip()
        return item

    def get_bsr(self, item):
        html = self.response.text
        bsrs = ''.join(re.findall(r'売れ筋ランキング(...*?)(?:</td>|</tr>)', html, re.S))
        bsrs_text = re.sub(re.compile(r'\(.*?\)|<style.*?</style>|<script.*?</script>|<.*?>', re.S), '', bsrs).replace('&nbsp;',' ').replace('&gt;','>')
        # '\xe4\xbd\x8d'是'位'的GBK编码,'\xe2\x94\x80'是'─'的GBK编码
        try:
            bsrs_text = bsrs_text.replace('\xe4\xbd\x8d', u'位').replace('\xe2\x94\x80', u'─')
        except:
            bsrs_text = bsrs_text.replace('\xe4\xbd\x8d', u'位').replace('\xe2\x94\x80', u'─')

        # bsr1
        bsr_one = re.findall(u"(.*?) - (\d[\d,]*)位", bsrs_text, re.S)
        if bsr_one:
            item['bsr1'] = bsr_one[0][-1].replace(',', '')
            item['bsr1path'] = bsr_one[0][0].replace(':', '').strip()[:200]

        # bsr2, bsr3, bsr4, bsr5
        for i, bsr in enumerate(re.findall(u"(\d[\d,]*)位\s+─\s*(.*?)\s\s+", bsrs_text, re.S)):
            if i<=3:
                item['bsr' + str(i+2)] = bsr[0].replace(',', '').strip()
                try:
                    item['bsr' + str(i+2) + 'path'] = bsr[1].strip()[:200]
                except:
                    # python2处理UnicodeDecodeError错误
                    item['bsr' + str(i+1) + 'path'] = bsr[1].strip()[:200]
            else:
                # 防止正则出错, 产生过多字段
                pass

        # 校验bsr,确保item有该字段
        for i in range(5):
            if not item.get:
                item['bsr' + str(i+1)] = 0
            if not item.get:
                item['bsr' + str(i+1) + 'path'] = ''

        return item

    def get_product_dimensions(self):
        product_dimensions = ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(text(), '%s')]/following-sibling::td/text()" % u'寸法').extract()).strip() \
                            or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(text(), '%s')]/parent::li/text()" % u'寸法').extract()).strip()
        return product_dimensions

    def get_offer_listing(self):
        return ''.join(self.response.xpath(".//*[@id='olp_feature_div']/div/span[1]/a/text()").extract()).strip().split(u'\uff1a')[
                -1] if self.response.xpath(".//*[@id='olp_feature_div']/div/span[1]/a/text()").extract() else ''

    def get_item_weight (self):
        item_weight = ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(text(), '%s')]/following-sibling::td/text()" % u'商品重量').extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(text(), '%s')]/parent::li/text()" % u'商品重量').extract()).strip()
        return item_weight

    def get_shipping_weight(self):
        shipping_weight = ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(text(), '%s')]/following-sibling::td/text()" % u'発送重量').extract()).strip() \
                        or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(text(), '%s')]/parent::li/text()" % u'発送重量').extract()).strip()
        return shipping_weight

    def get_item_model_number(self):
        item_model_number = ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(text(), '%s')]/following-sibling::td/text()" % u'型番').extract()).strip() \
                            or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(text(), '%s')]/parent::li/text()" % u'型番').extract()).strip()
        return item_model_number[:50]

    def get_issue_date(self):
        issue_date = ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(text(), '%s')]/following-sibling::td/text()" % u'開始日').extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(text(), '%s')]/parent::li/text()" % u'開始日').extract()).strip()
        return issue_date


