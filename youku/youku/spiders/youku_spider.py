# -*- coding: utf-8 -*-
import scrapy
from youku.items import YoukuItem
from scrapy import log, Selector

import re
import json
import datetime


class YoukuSpiderSpider(scrapy.Spider):
    name = "youkuSpider"
    allowed_domains = []
    start_urls = []

    def __init__(self):
        self.rank_url = "http://index.api.youku.com/getData?num={v_type}&orderPro=vv&startindex=1&endindex=20&channelId={channel}"
        self.rank_table = [{'type': '700009', 'channel': '97', 'name': '剧集'},
                           {'type': '700009', 'channel': '85', 'name': '综艺'},
                           {'type': '700009', 'channel': '100', 'name': '动漫'},
                           {'type': '700008', 'channel': '95', 'name': '音乐'},
                           {'type': '700008', 'channel': '99', 'name': '游戏'},
                           {'type': '700008', 'channel': '91', 'name': '资讯'},
                           {'type': '700008', 'channel': '104', 'name': '汽车'},
                           {'type': '700009', 'channel': '87', 'name': '教育'},
                           {'type': '700009', 'channel': '84', 'name': '纪实'},
                           {'type': '700008', 'channel': '86', 'name': '娱乐'},
                           {'type': '700008', 'channel': '98', 'name': '体育'},
                           {'type': '700008', 'channel': '105', 'name': '科技'},
                           {'type': '700008', 'channel': '94', 'name': '搞笑'},
                           {'type': '700008', 'channel': '103', 'name': '生活'},
                           {'type': '700008', 'channel': '176', 'name': '自拍'}]
        self.font_table = {'剧集': '剧集', '放剧场': '剧集', '综艺': '综艺', '少儿': '动漫', '动漫': '动漫',
                           '自频道精选': '综艺', '娱乐': '娱乐', '来疯直播': '自拍', '资讯': '资讯',
                           '搞笑': '搞笑', '音乐': '音乐', '文化 • 纪实': '纪实',
                           '财经 • 科技': '科技', '生活 • 时尚': '生活', '旅游 • 亲子': '生活',
                           '教育 • 公益': '教育', '汽车': '汽车', '游戏': '游戏', '体育': '体育', '邀你关注': '剧集'}
        self.id_pattern = re.compile(
            r'(?:id_|item)*([A-Za-z0-9]{13,15})(?:==)*')
        self.page = "http://v.youku.com/v_show/id_{vid}==.htm"
        self.movie_page = "http://list.youku.com/category/show/c_96_s_1_d_1_p_{page}.html"

    def start_requests(self):
        req_list = [scrapy.Request(
            url=self.rank_url.format(
                v_type=catagory['type'], channel=catagory['channel']),
            meta={'category': catagory['name']},
            callback=self.parse_rank,
        ) for catagory in self.rank_table]
        req_list = []
        req_list.append(scrapy.Request(url='http://www.youku.com/',
                                       callback=self.parse_fontpage))
        '''
        req_list = [scrapy.Request(
            url=self.movie_page.format(page=i + 1),
            meta={'rank': i},
            callback=self.parse_movie,
        ) for i in range(30)]
        '''
        return req_list

    def parse_rank(self, response):
        data = json.loads(response.body.decode())
        for video_info in data['result']['data']:
            video = YoukuItem()
            video['title'] = video_info['title']
            video['update_time'] = datetime.datetime.now(
            ).strftime("%Y-%m-%d %H:%M:%S")
            vid = re.findall(self.id_pattern, video_info['homepageurl'])
            if not vid:
                continue
            video['vid'] = vid[0]
            video['img'] = video_info['avatar']
            video['rank'] = video_info['order']
            if video_info['kind']:
                if type(video_info['kind']) is str:
                    video['label'] = video_info['kind']
                elif type(video_info['kind']) is list:
                    video['label'] = ','.join(video_info['kind'])
            video['category'] = response.meta['category']
            yield video

    def parse_fontpage(self, response):
        for zone in response.xpath("//div[contains(@name,'m_pos')]/div[contains(@class,'mod-new')]"):
            try:
                label_ = zone.xpath("div/h2/img/@title").extract()[0]
            except:
                continue
            if label_ == '放剧场':
                continue
            # 放剧场片名太怪,会引起冲突
            label = self.font_table[label_]
            zone_set = []
            zone_set += zone.xpath("div//div[@class='p-thumb']")
            for hide_eles in zone.xpath("div//textarea/text()").extract():
                zone_set += Selector(text=hide_eles).xpath(
                    "//div[@class='p-thumb']")
            for ele in zone_set:
                try:
                    vid = re.findall(self.id_pattern, ele.xpath(
                        "./a/@href").extract()[0])[0]
                except:
                    continue
                img_c = ele.xpath(
                    "./img[contains(@src,'ykimg')]/@src").extract()
                img_c += ele.xpath("./img[contains(@alt,'ykimg')]/@alt").extract()
                img = img_c[0]
                title = ele.xpath('./a/@title').extract()[0]
                if label == '剧集':
                    yield scrapy.Request(url=self.page.format(vid=vid),
                                         meta={'img': img, 'series': title},
                                         callback=self.parse_tv)
                elif label == '综艺':
                    if label_ == '综艺':
                        series = ele.xpath(
                            "./following-sibling::ul[@class='info-list']/li/span/text()").extract()[0]
                    elif label_ == '自频道精选':
                        series = ele.xpath(
                            "./preceding-sibling::div[@class='p-user']/@title").extract()[0]
                    yield scrapy.Request(url=self.page.format(vid=vid),
                                         meta={'series': series},
                                         callback=self.parse_show)
                else:
                    video = YoukuItem()
                    video['vid'] = vid
                    video['img'] = img
                    video['title'] = ele.xpath('./a/@title').extract()[0]
                    video['update_time'] = datetime.datetime.now(
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    video['category'] = label
                    video['series'] = ''
                    yield video

    def parse_tv(self, response):
        for item in response.xpath("//div[@class='tvlists']//div[contains(@class,'items')]/div[contains(@name,'tvlist')]"):
            video = YoukuItem()
            try:
                video['vid'] = re.findall(
                    self.id_pattern, item.xpath('./@id').extract()[0])[0]
            except:
                continue
            title = response.meta['series'] + \
                item.xpath('./@title').extract()[0]
            video['title'] = title
            video['update_time'] = datetime.datetime.now(
            ).strftime("%Y-%m-%d %H:%M:%S")
            video['category'] = '剧集'
            video['img'] = response.meta['img']
            video['series'] = response.meta['series']
            yield video

    def parse_show(self, response):
        for item in response.xpath("//div[@class='showlists']//div[contains(@class,'items')]/div[contains(@id,'child')]"):
            video = YoukuItem()
            try:
                video['vid'] = re.findall(
                    self.id_pattern, item.xpath(".//div[contains(@id,'item_')]/@id").extract()[0])[0]
            except:
                continue
            title = item.xpath(
                ".//div[contains(@id,'item_')]/@title").extract()[0]
            video['title'] = title
            video['update_time'] = datetime.datetime.now(
            ).strftime("%Y-%m-%d %H:%M:%S")
            video['category'] = '综艺'
            video['img'] = item.xpath(
                ".//div[contains(@class,'cover')]/img/@src").extract()[0]
            video['series'] = response.meta['series']
            yield video

    def parse_movie(self, response):
        i = 0
        for item in response.xpath("//div[contains(@class,'p-thumb')]"):
            img = item.xpath(".//img/@src").extract()
            if not img:
                continue
            video = YoukuItem()
            video['img'] = img[0]
            video['category'] = '电影'
            video['title'] = item.xpath(".//a/@title").extract()[0]
            try:
                video['vid'] = re.findall(
                    self.id_pattern, item.xpath(".//a/@href").extract()[0])[0]
            except:
                continue
            video['update_time'] = datetime.datetime.now(
            ).strftime("%Y-%m-%d")
            video['rank'] = response.meta['rank'] * 30 + i
            i += 1
            yield video
