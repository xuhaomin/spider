# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YoukuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    vid = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    labels = scrapy.Field()
    update_time = scrapy.Field()
    rank = scrapy.Field()
    series = scrapy.Field()
    category = scrapy.Field()
