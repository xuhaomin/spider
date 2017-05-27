# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Daily(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    update_time = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()


class Hot(scrapy.Item):
    aid = scrapy.Field()
    qid = scrapy.Field()
    title = scrapy.Field()
    update_time = scrapy.Field()
    abstract = scrapy.Field()
    full_content = scrapy.Field()
    author = scrapy.Field()
    day = scrapy.Field()
    month = scrapy.Field()
    reco = scrapy.Field()

class Post(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    update_time = scrapy.Field()
    abstract = scrapy.Field()
    full_content = scrapy.Field()
    author = scrapy.Field()

