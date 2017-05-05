# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from NEmusic.items import Playlist, Song, Artist, Album


from .settings import *


class NEPipeline(object):

    def __init__(self):
        self.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PW,
            charset=DB_CHARSET,
            db=DB_NAME)
        self.table_dict = [
            {"table": 'nemusic_playlist', "class": Playlist},
            {"table": 'nemusic_song', "class": Song},
            {"table": 'nemusic_artist', "class": Artist},
            {"table": 'nemusic_album', "class": Album},
        ]

    def sql_line(self, item, table):
        sql = 'INSERT INTO {table} ({keys}) VALUE ({values})'
        keys = ''
        values = ''
        for k, v in item.items():
            keys += '{k},'.format(k=str(k))
            values += "'{v}',".format(v=str(v))
        return sql.format(table=table, keys=keys[:-1], values=values[:-1])

    def process_item(self, item, spider):
        cursor = self.conn.cursor()
        sql = ''
        for item_class in self.table_dict:
            if item.__class__ == item_class["class"]:
                sql = self.sql_line(item, item_class['table'])
                break
        try:
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
        return item

    def close_spider(self, spider):
        self.conn.close()
