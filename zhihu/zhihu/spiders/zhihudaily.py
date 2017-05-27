# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from zhihu.items import Hot, Daily, Post

import json
import re
import datetime


class ZhihuDailySpider(scrapy.Spider):
    name = "zhihudaily"
    allowed_domains = []
    start_urls = ["http://daily.zhihu.com/"]

    def __init__(self):
        self.id_pattern = re.compile(r"/story/(\d+)")
        self.update_time = datetime.datetime.now(
            ).strftime("%Y-%m-%d")

    def parse(self, response):
        for ele in response.xpath("//div[@class='box']"):
            item = Daily()
            url = ele.xpath(".//a/@href").extract()[0]
            item['id'] = re.findall(self.id_pattern, url)[0]
            item['img'] = ele.xpath(".//img/@src").extract()[0]
            item['title'] = ele.xpath(".//span/text()").extract()[0]
            item['update_time'] = self.update_time
            yield item


class ZhihuHotSpider(scrapy.Spider):
    name = 'zhihuhot'
    allowed_domains = []
    start_urls = []

    def __init__(self):
        self.update_time = datetime.datetime.now(
            ).strftime("%Y-%m-%d")
        self.url = 'https://www.zhihu.com/node/ExploreAnswerListV2?params='
        self.reco_url = 'https://www.zhihu.com/node/ExploreRecommendListV2'
        self.id_pattern = re.compile(r'/question/(?P<qid>\d+)/answer/(?P<aid>\d+)')
        self.post_pattern = re.compile(r'https://zhuanlan.zhihu.com/p/(?P<id>\d+)')

    def start_requests(self):
        requests = []
        for i in range(20):
            for j in ['day', 'month']:
                params = json.dumps({'offset': i * 5, 'type': j})
                request = scrapy.Request(
                    url=self.url + params,
                    meta={'type': j},
                    callback=self.parse
                )
                requests.append(request)
        data = {'method': 'next', 'params': '{"offset": 0, "limit": 100}'}
        requests.append(scrapy.FormRequest(
            url=self.reco_url,
            formdata=data,
            meta={'type': 'reco'},
            callback=self.parse
        ))
        return requests

    def parse(self, response):
        posts = []
        if response.meta['type'] != 'reco':
            eles = response.xpath("//div[contains(@class,'feed-item')]")
        else:  #reco return mix articles and answers
            eles = []
            data = json.loads(response.body.decode())
            for content in data['msg']:
                ele = Selector(text=content)
                if ele.xpath("//div[@class='zm-item']/@data-type").extract()[0] == 'Post':
                    posts.append(ele)
                    continue
                eles.append(ele)
        for ele in eles:
            url = ele.xpath(".//a[@class='question_link']/@href").extract()
            title = ele.xpath(".//a[@class='question_link']/text()").extract()
            update_time = self.update_time
            abstract = ele.xpath(
                ".//div[@class='zh-summary summary clearfix']").xpath('string(.)').extract()
            full_content = ele.xpath(".//textarea/text()").extract()
            author = ele.xpath(".//span[contains(@class,'author')]").xpath('string(.)').extract()
            item = Hot()
            try:
                item[response.meta['type']] = 1
                item['aid'], item['qid'] = re.match(self.id_pattern, url[0]).group('aid', 'qid')
                item['title'] = title[0]
                item['update_time'] = update_time
                item['full_content'] = full_content[0]
                item['author'] = author[0].lstrip()
                item['abstract'] = abstract[0][:80]
            except Exception as e:
                print(e)
                response.meta['ele'] = ele
                from scrapy.shell import inspect_response
                inspect_response(response, self)
            yield item
        for post in posts:
            url = post.xpath(".//a[@class='post-link']/@href").extract()
            title = post.xpath(".//a[@class='post-link']/text()").extract()
            update_time = self.update_time
            abstract = post.xpath(
                ".//div[@class='zh-summary summary clearfix']").xpath('string(.)').extract()
            full_content = post.xpath(".//textarea/text()").extract()
            author = post.xpath(".//div[@class='post-content']/@data-author-name").extract()
            item = Post()
            try:
                item['id'] = re.match(self.post_pattern, url[0]).group('id')
                item['title'] = title[0]
                item['update_time'] = update_time
                item['full_content'] = full_content[0]
                item['author'] = author[0].lstrip()
                item['abstract'] = abstract[0][:80]
            except Exception as e:
                print(e)
                response.meta['ele'] = post
                from scrapy.shell import inspect_response
                inspect_response(response, self)
            yield item