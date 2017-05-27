# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LiepinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company = scrapy.Field()
    position = scrapy.Field()
    city = scrapy.Field()
    salary = scrapy.Field()
    benefit = scrapy.Field()
    requirement = scrapy.Field()
    rank = scrapy.Field()
    pid = scrapy.Field()
    companylink = scrapy.Field()
    catagory = scrapy.Field()


class Cata(scrapy.Item):
    pid = scrapy.Field()
    python = scrapy.Field()
    spider = scrapy.Field()
    data = scrapy.Field()
