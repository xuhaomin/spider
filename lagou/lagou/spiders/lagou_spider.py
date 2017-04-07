# -*- coding: utf-8 -*-

import json

import scrapy
from lagou.items import LagouItem
from scrapy import log
from scrapy_redis.spiders import RedisCrawlSpider


class LagouspiderSpider(RedisCrawlSpider):
    name = "lagouSpider"
    redis_key = 'lagou:spider:urls'
    #   allowed_domains = ["lagou.com"]
    #   start_urls = ["lagou.com"]

    def __init__(self):
        self.ajax_url = "http://www.lagou.com/jobs/positionAjax.json?kd={key}&pn={page}"
        self.position_url = 'https://www.lagou.com/jobs/{pID}.html'
        self.key_words = ['python', '爬虫', '数据采集']

    def start_requests(self):
        log.msg('now we start get_position_total_count', level=log.INFO)
        return [scrapy.Request(
                url=self.ajax_url.format(key=key, page=388),
                meta={'key': key},
                callback=self.get_position_info
                ) for key in self.key_words]

    def get_position_info(self, response):
        data = json.loads(response.body.decode())
        position_count = data['content']['positionResult']['totalCount']
        for i in range(1, min(334, (position_count - 1) // 15 + 2)):
            url = self.ajax_url.format(key=response.meta['key'], page=i)
            yield scrapy.Request(
                url=url,
                meta={'key': response.meta['key']},
                callback=self.parse_position_info
            )

    def parse_position_info(self, response):
        content = json.loads(response.body.decode())
        data = content['content']['positionResult']['result']
        for position in data:
            lab = position['firstType'] + ';' + position['secondType']
            position_info = {
                'position': position['positionName'],
                'benefit': position['positionAdvantage'],
                'positionID': position['positionId'],
                'company': position['companyFullName'],
                'salary': position['salary'],
                'city': position['city'],
                'labels': lab,
                'stage': position['financeStage']}
            url = self.position_url.format(pID=position_info['positionID'])
            yield scrapy.Request(
                url=url,
                meta={'key': response.meta['key'],
                      'position_info': position_info},
                callback=self.parse_position_page
            )

    def parse_position_page(self, response):
        item = LagouItem()
        item['requirement'] = '\n'.join(
            response.xpath('//dd[@class="job_bt"]/div//p//text()').extract()).replace('\xa0', '')
        item['company'] = response.meta['position_info']['company']
        item['position'] = response.meta['position_info']['position']
        item['city'] = response.meta['position_info']['city']
        item['salary'] = response.meta['position_info']['salary']
        item['benefit'] = response.meta['position_info']['benefit']
        item['labels'] = response.meta['position_info']['labels']
        item['stage'] = response.meta['position_info']['stage']
        yield item
