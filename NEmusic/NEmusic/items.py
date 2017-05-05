# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Playlist(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    lid = scrapy.Field()
    name = scrapy.Field()
    creator = scrapy.Field()
    play_count = scrapy.Field()
    img = scrapy.Field()


class Song(scrapy.Item):
    """docstring for song"""
    sid = scrapy.Field()
    name = scrapy.Field()
    artist_id = scrapy.Field()
    album_id = scrapy.Field()
    popularity = scrapy.Field()
    url = scrapy.Field()


class Artist(scrapy.Item):
    """docstring for artist"""
    artist_id = scrapy.Field()
    name = scrapy.Field()
    img = scrapy.Field()


class Album(scrapy.Item):
    album_id = scrapy.Field()
    name = scrapy.Field()
    img = scrapy.Field()
