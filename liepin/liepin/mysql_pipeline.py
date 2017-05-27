# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from liepin.items import LiepinItem, Cata
from .settings import *


class LiepinPipeline(object):

    def __init__(self):
        self.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PW,
            charset=DB_CHARSET,
            db=DB_NAME)
        dup_cata = "ON DUPLICATE KEY UPDATE {key} = 1;"
        self.class_dict = [
            {"class": LiepinItem, "table": 'liepin_position', "dup": ''},
            {"class": Cata, "table": 'liepin_cata', "dup": dup_cata},
        ]

    def insert_sql(self, params):
        for item_class in self.class_dict:
            if isinstance(params, item_class["class"]):
                table = item_class["table"]
                dup = item_class["dup"]
                break
        sql = 'INSERT INTO {table} ({keys}) VALUE ({values})'
        keys = ''
        values = ''
        for k, v in params.items():
            keys += '{k},'.format(k=str(k))
            values += "'{v}',".format(v=v)
            if v == 1:
                key = k
        if dup:
            dup = dup.format(key=key)
        return sql.format(table=table, keys=keys[:-1], values=values[:-1]) + dup

    def process_item(self, item, spider):
        cursor = self.conn.cursor()
        sql = self.insert_sql(item)
        try:
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(e)
        return item

    def close_spider(self, spider):
        self.conn.close()
