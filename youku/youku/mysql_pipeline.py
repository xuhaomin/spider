# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from .settings import *


class youkuPipeline(object):

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
        add = 'ON DUPLICATE KEY UPDATE rank={}'.format(int(params['rank'])) if 'rank' in params else ''
        for k, v in params.items():
            keys += '{k},'.format(k=str(k))
            values += "'{v}',".format(v=str(v))
        sql_line = sql.format(table=self.table, keys=keys[:-1], values=values[:-1]) + add
        return sql_line

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