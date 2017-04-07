# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from .settings import *


class LagouPipeline(object):

    def __init__(self):
        self.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PW,
            charset=DB_CHARSET,
            db=DB_NAME)
        self.table = DB_TABLE

    def insert_sql(self, params):
        sql = 'INSERT INTO {table} ({keys}) VALUE ({values})'
        keys = ''
        values = ''
        for k, v in params.items():
            keys += '{k},'.format(k=str(k))
            values += "'{v}',".format(v=str(v))
        return sql.format(table=self.table, keys=keys[:-1], values=values[:-1])

    def process_item(self, item, spider):
        cursor = self.conn.cursor()
        try:
            cursor.execute(self.insert_sql(item))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(e)
        return item

    def close_spider(self, spider):
        self.conn.close()