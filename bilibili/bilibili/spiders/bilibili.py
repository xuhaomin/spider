
# -*- coding: utf-8 -*-
"""
# Created on  2017-04-04 20:43:57

# Author  : homerX
"""
# gather the hot video aid from rank page
# use aid to the hot video page, parse, then get the cid and mid
# form cid generate the download url
# use the mid (author ID) to see other video
import json
import re

import scrapy
from bilibili.items import Bilibili_avinfo, Bilibili_downloadinfo
from scrapy import log
from scrapy_redis.spiders import RedisCrawlSpider


class BilibiliSpider(RedisCrawlSpider):
    name = "bilibili"
    redis_key = 'bilibili:spider:urls'

    def __init__(self):
        self._days = [1, 3, 7, 30]
        self.get_rank = '''http://www.bilibili.com/index/rank/all-{day}-{tid}.json'''
        self.video_page = 'https://www.bilibili.com/video/av{aid}/'
        self.get_info_by_mid = '''http://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}}&page={page}&pagesize={pagesize}'''
        self._rankID = {'0': '全站', '1': '动画', '3': '音乐', '4': '游戏', '5': '娱乐',
                        '11': '连载剧集', '23': '电影', '33': '连载动画', '36': '科技',
                        '119': '鬼畜', '129': '舞蹈', '168': '国创相关'}
        self.cid_getter = re.compile(r'cid=(\d+)')

    def get_item(self, av_info):
        item = Bilibili_avinfo()
        keys = ['aid', 'play', 'video_review', 'coins', 'title', 'author', 'mid', 'duration']
        for key in keys:
            item[key] = av_info[key]
        other = []
        if 'others' in av_info:
            for av in av_info['others']:
                other.append(av['aid'])
        item['others'] = other
        return item

    def start_requests(self):
        log.msg('now we start', level=log.INFO)
        return [scrapy.Request(
                url=self.get_rank.format(day=day, tid=tid),
                callback=self.parse_rank)
                for tid in self._rankID for day in self._days]

    def parse_rank(self, response):
        data = json.loads(response.body.decode())
        for video_info in data['rank']['list']:
            item = self.get_item(video_info)
            yield item
#            mid = item['mid']
            aids = item['others'] + [item['aid']]
            for aid in aids:
                yield scrapy.Request(
                    url=self.video_page.format(aid=aid),
                    meta={'aid': aid},
                    callback=self.parse_videopage)
#            yield scrapy.Request(
#                url=self.get_info_by_mid.format(mid=mid, page=1, pagesize=100),
#                callback=self.parse_mid)

    def parse_videopage(self, response):
        result = re.findall(self.cid_getter, response.body.decode())
        if not result:
            from scrapy.shell import inspect_response
            inspect_response(response)
        else:
            item = Bilibili_downloadinfo()
            item['aid'] = response.meta['aid']
            item['cid'] = result[0]
            yield item

    def parse_mid(self, response):
        data = json.loads(response.body.decode())
        pass
