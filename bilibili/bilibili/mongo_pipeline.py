# -*- coding: utf-8 -*-
"""
# Created on  2017-04-11 14:44:56

# Author  : homerX
"""
import pymongo

from .setting import *


class Bilibili_Mongo(object):

    def __init__(self):
        self.uri = DB_URI
        self.db_name = DB_NAME
        self.col_name = DB_TABLE
        self.cli = pymongo.MongoClient(self.uri)
        self.db = self.cli[self.db_name]
        self.col = self.db[self.col_name]

    def process_item(self, item, spider):
        pass

    def close_spider(self, spider):
        pass
