# -*- coding: utf-8 -*-
import random
import time
import json

import scrapy
from lagou.items import LagouItem
from scrapy import log


class LagouspiderSpider(scrapy.Spider):
    name = "lagouSpider"
    allowed_domains = ["lagou.com"]
    start_urls = ["lagou.com"]

    def __init__(self):
        self.cookie_counter = 0
        self.cookie_index = 0
        self._cookie_invaild_time = 50
        self.ajax_url = "http://www.lagou.com/jobs/positionAjax.json?kd={key}&pn={page}"
        self.position_url = 'https://www.lagou.com/jobs/{pID}.html'
        self.key_words = ['python', '爬虫', '数据采集']

    def get_cookie_from_this_url(self):
        cid = '{0}.{1}'.format(
            int(random.random() * (10**9)), int(time.time()))
        url = '''http://a.lagou.com/collect?v=1&_v=j31&a=1437539037
        &t=pageview&_s=1&dl=https%3A%2F%2Fwww.lagou.com%2F&ul=zh-cn
        &de=UTF-8&dt=%E6%8B%89%E5%8B%BE%E7%BD%91-%E6%9C%80%E4%B8%93%
        E4%B8%9A%E7%9A%84%E4%BA%92%E8%81%94%E7%BD%91%E6%8B%9B%E8%81%98
        %E5%B9%B3%E5%8F%B0_%E6%89%BE%E5%B7%A5%E4%BD%9C_%E6%8B%9B%E8%81%
        98_%E4%BA%BA%E6%89%8D%E7%BD%91_%E6%B1%82%E8%81%8C&sd=24-bit&sr=1680x1050
        &vp=639x690&je=0&fl=24.0%20r0&_u=MACAAAQBK~&jid=&
        cid={cid}&tid=UA-41268416-1&z=772245087'''.format(cid=cid)
        return url

    def checker(self):
        self.cookie_counter += 1
        if self.cookie_counter > self._cookie_invaild_time:
            self.cookie_index += 1
            self.cookie_counter = 0
            return False
        else:
            return True

    def change_cookie(self, response):
        meta = response.meta
        meta.update({'cookiejar': self.cookie_index})
        return scrapy.Request(
            response.meta['next_url'],
            meta=meta,
            callback=response.meta['callback']
        )

    def check_and_open(self, url, meta, callback):
        if self.checker():
            return scrapy.Request(url, meta=meta, callback=callback)
        else:
            meta.update({'next_url': url, 'callback': callback})
            return scrapy.Request(
                self.get_cookie_from_this_url(),
                meta=meta,
                callback=self.change_cookie,
                dont_filter=True
            )

    def start_requests(self):
        scrapy.log.msg('now we start', level=scrapy.log.INFO)
        return [scrapy.Request(
            self.get_cookie_from_this_url(),
            meta={'cookiejar': self.cookie_index},
            callback=self.get_position_total_count,
            dont_filter=True
        )]

    def get_position_total_count(self, response):
        log.msg('now we start get_position_total_count', level=log.INFO)
        for key in self.key_words:
            url = self.ajax_url.format(key=key, page=388)
            yield self.check_and_open(
                url=url,
                meta={'cookiejar': response.meta['cookiejar'], 'key': key},
                callback=self.get_position_info
            )

    def get_position_info(self, response):
        data = json.loads(response.body.decode())
        position_count = data['content']['positionResult']['totalCount']
        for i in range(1, min(334, (position_count - 1) // 15 + 2)):
            url = self.ajax_url.format(key=response.meta['key'], page=i)
            yield self.check_and_open(
                url=url,
                meta={'cookiejar': response.meta['cookiejar'],
                      'key': response.meta['key']},
                callback=self.parse_position_info
            )

    def parse_position_info(self, response):
        content = json.loads(response.body.decode())
        data = content['content']['positionResult']['result']
        for position in data:
            position_info = {
                'position': position['positionName'],
                'benefit': position['positionAdvantage'],
                'positionID': position['positionId'],
                'company': position['companyFullName'],
                'salary': position['salary'],
                'city': position['city'],
                'labels': position['positionLables'],
                'stage': position['financeStage']}
            url = self.position_url.format(pID=position_info['positionID'])
            yield self.check_and_open(
                url=url,
                meta={'cookiejar': response.meta['cookiejar'],
                      'key': response.meta['key'],
                      'position_info': position_info},
                callback=self.parse_position_page
            )

    def parse_position_page(self, response):
        item = LagouItem()
        item['requirement'] = '\n'.join(
            response.xpath('//dd[@class="job_bt"]/div//p//text()').extract())
        item['company'] = response.meta['position_info']['company']
        item['position'] = response.meta['position_info']['position']
        item['city'] = response.meta['position_info']['city']
        item['salary'] = response.meta['position_info']['salary']
        item['benefit'] = response.meta['position_info']['benefit']
        item['labels'] = ';'.join(response.meta['position_info']['labels'])
        item['stage'] = response.meta['position_info']['stage']
        yield item
