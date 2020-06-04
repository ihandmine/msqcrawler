import json
import re
import time

from abc import ABC

from item import Item
from spider import Spider


class ListingSpiderBase(Spider, ABC):
    name = ''
    base_url = ''
    logging_keys = ['asin', ]

    def parse(self):
        item = Item()
        item['country'] = self.name.split('_')[-1]
        item['asin'] = self.response.meta['asin']

        item['page_title'] = self.get_page_title()  # 页面标题
        item['product_title'] = self.get_product_title()    # 商品标题
        item['provide'] = self.get_provide()        # 品牌
        item['provide_id'] = self.get_provide_id()  # 品牌id
        item['product_path'] = self.get_product_path()  # 类目
        item['product_top100_node'] = self.get_product_node()

        # 获取商品图片链接:img1, img2, img3, img4, img5
        item = self.get_img(item)

        item['price'] = self.get_price()    # 价格
        item['list_price'] = self.get_list_price()  # 标签价
        item['sale_price'] = self.get_sale_price()  # 促销价格
        item['deal_price'] = self.get_deal_price()  # 活动价格
        item['price_savings'] = self.get_price_savings()   # 节省了多少钱

        # 获取卖点: bullet_point1, bullet_point2, bullet_point3, bullet_point4, bullet_point5
        item = self.get_bullet_point(item)

        item['customer_reviews_count'] = self.get_customer_reviews_count()  # 评论总数
        item['ask'] = self.get_ask()    # 咨询数
        item['best_seller'] = self.get_best_seller()    # 是否是best_seller
        item['best_seller_path'] = self.get_best_seller_path()  # best_seller所在类目
        item['stars'] = self.get_stars()    # 评论平率分

        # 获取评论星级占比: 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'
        item = self.get_star_percent(item)

        # item['description'] = self.get_description()    # 商品描述
        item['top_bad_reviews'] = self.get_top_bad_reviews()    # 排行最高的差评数
        # item['recent_bad_reviews'] = self.get_recent_bad_reviews()  # 最近的差评数
        item['offer_listing'] = self.get_offer_listing()    # 跟卖数量
        item['soldby'] = self.get_soldby()  # 销售平台
        item['soldbyurl'] = self.get_soldbyurl()    # 销售平台链接
        item['fba'] = self.get_fba()    # 物流

        # 获取bsr,商品所在类目排名: 'bsr1','bsr1path','bsr2','bsr2path','bsr3','bsr3path','bsr4','bsr4path','bsr5','bsr5path'
        item = self.get_bsr(item)

        # item['AddOn'] = self.get_AddOn()
        # item['RelatedUrl'] = self.get_RelatedUrl()  # 相近商品ajax链接
        # item['AlsoBoughtUrl'] = self.get_AlsoBoughtUrl()    # 跟卖ajax链接
        item['color'] = self.get_color()    # 颜色
        item['color_count'] = self.get_color_count()    # 颜色种类数

        item['product_dimensions'] = self.get_product_dimensions()  # 商品尺寸
        item['item_weight'] = self.get_item_weight()    # 商品重量
        item['shipping_weight'] = self.get_shipping_weight()    # 出货重量
        item['item_model_number'] = self.get_item_model_number()    # 商品编号
        item['issue_date'] = self.get_issue_date()  # 产品上架时间

        item['add_date_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 抓取时间(北京时间)
        # 过滤表情
        item.multi_filter_emoji(
            item,
            'bullet_point1',
            'bullet_point2',
            'bullet_point3',
            'bullet_point4',
            'bullet_point5',
            'page_title',
            'color',
            'product_title',
            'soldby',
            'provide'
        )

        yield item

    def get_page_title(self):
        return ''.join(self.response.xpath(".//title/text()").extract())

    def get_product_title(self):
        product_title = ''.join(self.response.xpath(".//*[@id='productTitle']/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='ebooksProductTitle']/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='title_feature_div']//h1/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//section[@class='av-detail-section']/h1/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='mas-title']/div/span/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='btAsinTitle']/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='a2s-product-info']//h1/text()").extract()).strip() \
                    or ''.join(self.response.xpath(".//*[@id='artist-name']/text()").extract()).strip()
        return product_title

    def get_provide(self):
        return ''.join(self.response.xpath(".//*[@id='bylineInfo' or @id='brand']/text()").extract()).strip()[:255]

    def get_provide_id(self):
        return ''.join(self.response.xpath(".//*[@id='bylineInfo' or @id='brand']/@href").extract()).strip()[:255]

    def get_product_path(self):
        return ''.join([i.strip() for i in self.response.xpath(".//*[@id='wayfinding-breadcrumbs_feature_div']/ul//text()").extract()])

    def get_product_node(self):
        return ''.join(re.findall(r'node=(\d+)', 
                                  ''.join(
            self.response.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[last()]//a/@href').extract())))

    def get_img(self, item):
        # 页面结构1
        if self.response.xpath(".//img[@id='landingImage']/@data-a-dynamic-image").extract():
            img_json = json.loads(self.response.xpath(".//img[@id='landingImage']/@data-a-dynamic-image").extract()[0])
            if img_json:
                item['img1'] = list(img_json.keys())[0]
        for i, img in enumerate(self.response.xpath(".//*[@id='altImages']/ul//img/@src").extract()):
            if i == 5:
                break
            else:
                if i >= 1:
                    item['img' + str(i + 1)] = img

        # 页面结构2
        if not item.get and self.response.xpath(".//img[@id='imgBlkFront']/@data-a-dynamic-image").extract():
            img_json = json.loads(self.response.xpath(".//img[@id='imgBlkFront']/@data-a-dynamic-image").extract()[0])
            if img_json:
                item['img1'] = list(img_json.keys())[0]

            for i, img in enumerate(self.response.xpath(".//*[@id='imgThumbs']//img/@src").extract()):
                if i == 5:
                    break
                else:
                    if i >= 1:
                        item['img' + str(i + 1)] = img

        for i in range(5):
            if not item.get:
                item['img' + str(i + 1)] = ''
        return item

    def get_price(self):
        html = self.response.text
        try:
            price = str(json.loads(''.join(self.response.xpath('//li[@data-p13n-asin-metadata][1]/@data-p13n-asin-metadata').extract())).get)
        except Exception as e:
            price = ''
        price = price \
            or ''.join(self.response.xpath('.//*[@id="priceblock_ourprice"]/text()').extract()).strip()  \
            or ''.join(self.response.xpath('//*[@id="comparison_price_row"]/td[1]/span/span[1]/text()').extract()).strip() \
            or ''.join(re.findall(u'id="priceblock_ourprice" class="a-size-medium a-color-price">(.*?)</span>', html, re.S)) \
            or ''.join(self.response.xpath('//*[@id="price"]//*[@class="a-size-medium a-color-price"]/text()').extract()[:1]).strip() \
            or ''.join(self.response.xpath('//*[@id="buyNew_noncbb"]/span/text()').extract()).strip() \
            or ''.join(self.response.xpath('//*[@id="cerberus-data-metrics"]/@data-asin-price').extract()).strip() \
            or ''.join(self.response.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()").extract()[:2]).strip() \
            or ''.join(''.join(self.response.xpath('//*[@id="olp-upd-new"]//a/text()').extract()).split('$')[-1:]).strip() \
            or ''.join(''.join(self.response.xpath('//*[@id="olp-upd-used"]/span/a/text()').extract()).split('$')[-1:]).strip() \
            or ''.join(self.response.xpath('//*[@id="olp-sl-new" or @id="olp-used"]/span/span//text()').extract()).strip() \
            or ''.join(self.response.xpath('//*[@id="buybox"]//*[contains(@class, "offer-price")]/text()').extract()).strip() \
            or ''.join(self.response.xpath('//*[@id="availability"]/span/text()').extract()) \
            or ''.join(self.response.xpath('//*[@id="outOfStock"]/div/span/text()').extract()) \
            or ''.join(self.response.xpath('//*[@id="comparison_price_row"]/td[1]/span/text()').extract()).replace('"', '').strip().replace('From ', '') \
            or ''.join(self.response.xpath('//*[@class="a-sirze-base a-color-price a-color-price"]/text()').extract()[:1]).strip() \
            or '.'.join(self.response.xpath('//*[@id="priceblock_ourprice"]//span/text()').extract()).replace('$.', '$').strip()
        if price and not re.findall(r'\d[\d]*', price) or len(price) >= 40:
            price = '-1'
        return price

    def get_list_price(self):
        list_price = ''.join(self.response.xpath("//*[@id='price']//tr[not(@id)]//td[2]/span[1]/text()").extract()).strip()
        if len(list_price) > 50:
            return ''
        return list_price

    def get_sale_price(self):
        sale_price = ''.join(self.response.xpath('//*[@id="priceblock_saleprice"]/text()').extract()).strip()
        if len(sale_price) > 50:
            return ''
        return sale_price

    def get_deal_price(self):
        deal_price = ''.join(self.response.xpath('//*[@id="priceblock_dealprice"]/text()').extract()).strip()
        if len(deal_price) > 50:
            return ''
        return deal_price

    def get_price_savings(self):
        price_savings = ''.join(self.response.xpath("//tr[@id='regularprice_savings']/td[2]//text()").extract()).strip()[:50] \
                        or ''.join(self.response.xpath("//tr[@id='dealprice_savings']/td[2]//text()").extract()).strip()[:50]
        if len(price_savings) > 50:
            return ''
        return price_savings

    def get_bullet_point(self, item):
        start_num = 1 if ''.join(
            self.response.xpath(".//*[@id='feature-bullets']//ul/li[1]/span/text()").extract()).strip() else 2
        item['bullet_point1'] = ''.join(
            self.response.xpath(".//*[@id='feature-bullets']//ul/li[%s]/span/text()" % str(start_num + 0)).extract()).strip()
        item['bullet_point2'] = ''.join(
            self.response.xpath(".//*[@id='feature-bullets']//ul/li[%s]/span/text()" % str(start_num + 1)).extract()).strip()
        item['bullet_point3'] = ''.join(
            self.response.xpath(".//*[@id='feature-bullets']//ul/li[%s]/span/text()" % str(start_num + 2)).extract()).strip()
        item['bullet_point4'] = ''.join(
            self.response.xpath(".//*[@id='feature-bullets']//ul/li[%s]/span/text()" % str(start_num + 3)).extract()).strip()
        item['bullet_point5'] = ''.join(
            self.response.xpath(".//*[@id='feature-bullets']//ul/li[%s]/span/text()" % str(start_num + 4)).extract()).strip()
        return item

    def get_customer_reviews_count(self):
        return ''.join(''.join(self.response.xpath(".//*[@id='acrCustomerReviewText']/text()").extract()[:1]).strip().split()[:-1]).replace(',', '')

    def get_ask(self):
        return ''.join(re.findall(r'\d+', ''.join(
            self.response.xpath(".//*[@id='askATFLink']/span/text()").extract()).strip().replace(',', '')))

    def get_best_seller(self):
        return '1' if self.response.xpath(".//*[@id='zeitgeistBadge_feature_div']/div/a") else '0'

    def get_best_seller_path(self):
        return ''.join([i.strip() for i in self.response.xpath(
            ".//*[@id='zeitgeistBadge_feature_div']/div/a/span/span/text()").extract()])

    def get_stars(self):
        # return ''.join(self.response.xpath(".//*[@id='acrPopover']/span[1]/a/i[1]/span/text()").extract()).split()[
        #     0] if self.response.xpath(".//*[@id='acrPopover']/span[1]/a/i[1]/span/text()") else 0
        return ''.join(re.findall(r'([0-4]\.\d|5\.0)', ''.join(self.response.xpath(".//*[@id='acrPopover']/span[1]/a/i[1]/span/text()").extract()).strip().replace(',', '.'))[:1]) or 0

    def get_star_percent(self, item):
        html = self.response.text
        item['five_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[1]/td[3]//a//text()").extract()[:-1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="5 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 5 stars"', html, re.S)[:1]).strip()

        item['four_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[2]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="4 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 4 stars"', html, re.S)[:1]).strip()

        item['three_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[3]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="3 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 3 stars"', html, re.S)[:1]).strip()

        item['two_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[4]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="2 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 2 stars"', html, re.S)[:1]).strip()

        item['one_star'] = ''.join(self.response.xpath(".//*[@id='histogramTable']//tr[5]/td[3]//a//text()").extract()[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="1 stars represent (.{0,10}) of rating" href="', html, re.S)[:1]).strip() \
            or ''.join(re.findall(r'<a class="a-link-normal" title="(.{0,10}) of reviews have 1 stars"', html, re.S)[:1]).strip()
        return item

    def get_description(self):
        return '\n'.join([i.strip() for i in self.response.xpath(
            ".//*[@id='aplus' or @id='productDescription']//*[not(@type='text/css' or @type='text/javascript')]/text()").extract()])

    def get_top_bad_reviews(self):
        try:
            return str(sum([1 for j in [float(i.split()[0]) for i in self.response.xpath(".//*[@data-hook='review']//*[@class='a-icon-alt']/text()").extract()] if j < 4]))
        except:
            return '0'

    def get_recent_bad_reviews(self):
        return str(sum([1 for j in [float(i.split()[0]) for i in self.response.xpath(
            ".//*[@id='revMRRL']/div//div/a[1]/i/span/text()").extract()] if j < 4]))

    def get_offer_listing(self):
        return ''.join(re.findall(r'\((\d+)\)', ''.join(
            self.response.xpath(".//*[@id='olp_feature_div']/div/span[1]/a/text()").extract()).strip()))

    def get_soldby(self):
        soldby = ''.join(self.response.xpath(".//*[@id='merchant-info']/a[1]/text()").extract()).strip()
        if soldby == '' and (u'Amazon' in ''.join(self.response.xpath(".//*[@id='merchant-info']/text()").extract())):
            soldby = u'Amazon'
        if len(soldby) > 100:
            return ''
        return soldby

    def get_soldbyurl(self):
        return ''.join(self.response.xpath(".//*[@id='merchant-info']/a[1]/@href").extract()).strip()

    def get_fba(self):
        return ''.join(
            self.response.xpath(".//*[@id='merchant-info']/a[@id='SSOFpopoverLink']/text()").extract()).strip()

    def get_bsr(self, item):
        html = self.response.text
        bsrs = ''.join(re.findall(r'Best Sellers Rank(...*?)(?:</td>|</tr>)', html, re.S))
        bsrs_text = re.sub(re.compile(r'\(.*?\)|<style.*?</style>|<script.*?</script>|<.*?>', re.S), '', bsrs).replace('&nbsp;',' ').replace('&gt;','>')

        for i, bsr in enumerate(re.findall(r"(\d[\d,]*)\s+in(.*?)\s\s+", bsrs_text, re.S)):
            if i <= 4:
                item['bsr' + str(i+1)] = bsr[0].replace(',', '').strip()
                item['bsr' + str(i+1) + 'path'] = bsr[1].replace(u'\xa0', '').strip()[:200]
            else:
                # 防止正则出错, 产生过多字段
                print('bsr正则出错, asin:{0}'.format(self.response.meta.get))

        # 校验bsr,确保item有该字段
        for i in range(5):
            if not item.get:
                item['bsr' + str(i+1)] = '0'
            if not item.get:
                item['bsr' + str(i+1) + 'path'] = ''

        return item

    def get_AddOn(self):
        return '1' if self.response.xpath(".//*[@id='addon']") else '0'

    def get_color(self):
        color = ''.join(self.response.xpath(".//*[@id='variation_color_name']/div/span/text()").extract()).strip()
        if len(color) > 100:
            return ""
        return color

    def get_color_count(self):
        return str(len(self.response.xpath(".//*[@id='variation_color_name']/ul/li")))

    def get_product_dimensions(self):
        html = self.response.text
        product_dimensions = ''.join(re.findall(r'(?:Product information|Product details).*?(?:Package |Product )Dimensions.*?(\d[\d\.]* x \d[\d\.]* x \d[\d\.]* inches)', html, re.S)[:1]).strip() \
            or ''.join(''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'dimensions')]/following-sibling::td/text()").extract()).split(';')[:1]).strip() \
            or ''.join(''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'dimensions')]/parent::li/text()").extract()).split(';')[:1]).strip()
        return product_dimensions

    def get_item_weight(self):
        html = self.response.text
        item_weight = ''.join(re.findall(r'(?:Product information|Product details).*?Item Weigh.*?(\d[\d\.]* (?:ounces|pounds))', html, re.S)[:1]).strip() \
            or ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'item weight')]/following-sibling::td/text()").extract()).strip() \
            or ''.join(''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'dimensions')]/parent::li/text()").extract()).split(';')[1:]).strip() \
            or ''.join(''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'item weight')]/parent::li/text()").extract()).split(';')[1:]).strip() \
            or ''.join(''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'dimensions')]/parent::li/text()").extract()).split(';')[1:]).strip()
        return item_weight

    def get_shipping_weight(self):
        html = self.response.text
        shipping_weight = ''.join(re.findall(r'(?:Product information|Product details).*?Shipping Weight.*?(\d[\d\.]* (?:ounces|pounds))', html, re.S)[:1]).strip() \
            or ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'shipping weight')]/following-sibling::td/text()").extract()[:1]).strip() \
            or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'shipping weight')]/parent::li/text()").extract()).strip() \
            or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'boxed-product weight')]/parent::li/text()").extract()).strip()
        return shipping_weight

    def get_item_model_number(self):
        html = self.response.text
        item_model_number = ''.join(re.findall(r'(?:Product information|Product details).*?Item model number.*?td class="a-size-base">(.*?)</td>', html, re.S)[:1]).strip() \
            or ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'item model')]/following-sibling::td/text()").extract()).strip() \
            or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'item model')]/parent::li/text()").extract()).strip()
        return item_model_number[:50]

    def get_issue_date(self):
        html = self.response.text
        issue_date = ''.join(re.findall(r'(?:Product information|Product details).*?Date First Available.*?td class="a-size-base">(.*?)</td>', html, re.S)[:1]).strip() \
            or ''.join(self.response.xpath(".//*[@id='prodDetails']//td[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'first available')]/following-sibling::td/text()").extract()).strip() \
            or ''.join(self.response.xpath(".//*[@id='prodDetails']//th[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'first listed on')]/following-sibling::td/text()").extract()).strip() \
            or ''.join(self.response.xpath(".//*[@id='detail_bullets_id']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'first available')]/parent::li/text()").extract()).strip() \
            or ''.join(self.response.xpath(".//*[@id='detail-bullets']//li/b[contains(translate(text(), 'QWERTYUIOPASDFGHJKLZXCVBNM', 'qwertyuiopasdfghjklzxcvbnm'), 'first listed on')]/parent::li/text()").extract()).strip()
        return issue_date

    def get_RelatedUrl(self):
        if self.response.xpath(".//*[@id='sp_detail']/@data-a-carousel-options"):
            data = json.loads(self.response.xpath(".//*[@id='sp_detail']/@data-a-carousel-options").extract()[0])
            return self.base_url + data['ajax']['url'] + '?ASIN=' + data['ajax']['params']['ASIN']\
                   + '&ie=UTF8'\
                   + '&searchTerms='\
                   + '&searchIndex='\
                   + '&referringSearchEngine=Amazon'\
                   + '&wName=' + data['ajax']['params']['wName']\
                   + '&pRID=' + data['ajax']['params']['pRID']\
                   + '&start=' + '0'\
                   + '&cc=' + '0'\
                   + '&count=' + '0'\
                   + '&offset=' + '0'\
                   + '&tot=' + str(data['set_size'])\
                   + '&num=35'
        return ''

    def get_AlsoBoughtUrl(self):
        if self.response.xpath(".//*[@id='purchase-sims-feature']/div").extract():
            data = json.loads(
                self.response.xpath(".//*[@id='purchase-sims-feature']/div/@data-a-carousel-options").extract()[0])
            get_count = data['set_size'] if data['set_size'] <= 35 else 35
            return self.base_url + data['ajax']['url'] + '?featureId=' + data['ajax']['params']['featureId']\
                   + '&reftagPrefix=' + data['ajax']['params']['reftagPrefix']\
                   + '&widgetTemplateClass=' + data['ajax']['params']['widgetTemplateClass'].replace(':', '%3A')\
                   + '&imageHeight=' + str(data['ajax']['params']['imageHeight'])\
                   + '&faceoutTemplateClass=' + data['ajax']['params']['faceoutTemplateClass'].replace(':', '%3A')\
                   + '&auiDeviceType=' + data['ajax']['params']['auiDeviceType']\
                   + '&imageWidth=' + str(data['ajax']['params']['imageWidth'])\
                   + '&schemaVersion=' + str(data['ajax']['params']['schemaVersion'])\
                   + '&productDetailsTemplateClass=' + data['ajax']['params']['productDetailsTemplateClass'].replace(':', '%3A')\
                   + '&forceFreshWin=' + str(data['ajax']['params']['forceFreshWin'])\
                   + '&productDataFlavor=' + data['ajax']['params']['productDataFlavor']\
                   + '&relatedRequestID=' + data['ajax']['params']['relatedRequestID']\
                   + '&maxLineCount=' + str(data['ajax']['params']['maxLineCount'])\
                   + '&count=' + str(get_count)\
                   + '&offset=' + '0'\
                   + '&asins=' + '%2C'.join(data['ajax']['id_list'][:get_count])
        return ''


