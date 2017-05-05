# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Bilibili_avinfo(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    aid = scrapy.Field()
    play = scrapy.Field()
    video_review = scrapy.Field()
    coins = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    mid = scrapy.Field()
    duration = scrapy.Field()
    others = scrapy.Field()


class Bilibili_downloadinfo(scrapy.Item):
    aid = scrapy.Field()
    cid = scrapy.Field()
    download_link = scrapy.Field()
