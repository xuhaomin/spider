# -*- coding: utf-8 -*-

import pymysql
from zhihu.items import Hot, Daily, Post
from .settings import *


class ZhihuPipeline(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def __init__(self):
        self.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PW,
            charset=DB_CHARSET,
            db=DB_NAME)
        self.dup = "ON DUPLICATE KEY UPDATE update_time = {};"
        self.class_dict = [
            {"class": Hot, "table": 'zhihu_explore'},
            {"class": Daily, "table": 'zhihu_daily'},
            {"class": Post, "table": 'zhihu_article'},
        ]

    def insert_sql(self, item):
        for item_class in self.class_dict:
            if isinstance(item, item_class["class"]):
                table = item_class["table"]
                break
        sql = 'INSERT INTO {table} ({keys}) VALUE ({values})'
        keys = ''
        values = ''
        for k, v in item.items():
            keys += '{k},'.format(k=str(k))
            values += "'{v}',".format(v=v)
        dup = self.dup.format(item['update_time'])
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
