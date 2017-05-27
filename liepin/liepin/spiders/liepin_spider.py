# -*- coding: utf-8 -*-

import json
import re
import scrapy
from liepin.items import LiepinItem, Cata
from scrapy import log
from scrapy_redis.spiders import RedisCrawlSpider


class liepinSpider(RedisCrawlSpider):
    name = "liepinSpider"
    redis_key = 'liepin:spider:urls'
    #   allowed_domains = ["lagou.com"]
    #   start_urls = ["lagou.com"]

    def __init__(self):
        self.search_url = 'https://www.liepin.com/zhaopin/?dqs={city}&headckid={ckid}&key={key}&curPage={page}'
        self.position_url = 'https://www.liepin.com/job/{pID}.shtml'
        self.city_dict = {
            '020': '上海',
            '050020': '广州',
            '070020': '杭州',
            '090040': '厦门',
        }
        self.key_dict = {
            'python': 'python',
            '爬虫': 'spider',
            '数据挖掘': 'data'
        }
        self.count_extract = re.compile(r'curPage=(\d+)')
        self.ckid_extract = re.compile(r'headckid=(\w+)')
        self.pid_extract = re.compile(r'/(\d+)\.shtml')

    def start_requests(self):
        return [scrapy.Request(
                url=self.search_url.format(
                    key=key, city=city, ckid='', page=0),
                meta={'key': key, 'city': city},
                callback=self.parse_search
                ) for key in self.key_dict for city in self.city_dict]

    def parse_search(self, response):
        page_link = response.xpath(
            '//div[@class="pagerbar"]//a[@class="last"]/@href').extract()
        page_count = min(
            20, int(re.findall(self.count_extract, page_link[0])[0]))
        ckid = re.findall(self.ckid_extract, page_link[0])[0]
        self.next_search_page(response)
        for i in range(1, page_count):
            url = self.search_url.format(
                city=response.meta['city'], ckid=ckid, key=response.meta['key'], page=i)
            yield scrapy.Request(
                url=url,
                meta={'key': response.meta['key'],
                      'city': response.meta['city'],
                      'rank': i},
                callback=self.next_search_page
            )

    def next_search_page(self, response):
        positions = response.xpath(
            "//div[contains(@class,'sojob-result')]//li")
        links = response.xpath(
            "//div[contains(@class,'sojob-result')]//li//h3/a/@href").extract()
        for p in positions:
            try:
                link = p.xpath(".//h3/a/@href").extract()[0]
                pid = re.findall(self.pid_extract, link)[0]
                salary = p.xpath(
                    ".//div[@class='job-info']//span[@class='text-warning']/text()").extract()[0]
                company = p.xpath(
                    ".//div[@class='job-info']//h3/@title").extract()[0]
            except:
                continue

            cata = Cata()
            cata[self.key_dict[response.meta['key']]] = 1
            cata['pid'] = pid
            yield cata

            yield scrapy.Request(
                url=link,
                meta={'key': response.meta['key'],
                      'city': response.meta['city'],
                      'pid': pid,
                      'rank': response.meta['rank'],
                      'company': company,
                      'salary': salary },
                callback=self.parse_position_page,
            )

    def parse_position_page(self, response):
        position = response.xpath(
            "//div[contains(@class,'title-info')]/h1/text()").extract()[0]
        requirement = '\n'.join(response.xpath(
            "//div[contains(@class,'main-message')][1]/div/text()").extract())
        benefit = ','.join(response.xpath(
            "//div[contains(@class,'tag-list')]/span/text()").extract())
        try:
            companylink = response.xpath(
                "//div[@class='company-infor']/h4/a[1]/@href").extract()[0]
        except:
            companylink = ''
        item = LiepinItem()
        item['requirement'] = requirement
        item['companylink'] = companylink
        item['company'] = response.meta['company']
        item['position'] = position
        item['city'] = self.city_dict[response.meta['city']]
        item['salary'] = response.meta['salary']
        item['benefit'] = benefit
        item['pid'] = response.meta['pid']
        item['catagory'] = response.meta['key']
        item['rank'] = response.meta['rank']
        yield item
