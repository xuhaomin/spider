# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from NEmusic.items import Song
from NEMbox.api import NetEase,encrypted_request

import hashlib


class fakePipeline(object):
    def __init__(self):
        self.mysession = NetEase()
        user = "xhm900119@163.com"
        pw = "19900119"
        pw_ = hashlib.md5(pw.encode('utf-8')).hexdigest()
        self.mysession.login(user, pw_)

    def fake(self, sid):
        url = 'http://music.163.com/weapi/feedback/weblog?csrf_token='
        text = {
            'data': {
                'logs': {
                    'action': "play",
                    'json': {"type": "song",
                             "wifi": 0,
                             "download": 0,
                             "id": sid,
                             "time": 600,
                             "end": "ui",
                             "source": "list",
                             "sourceId": "576900073"}
                }
            }
        }
        data = encrypted_request(text)
        self.mysession.session.post(url=url, data=data)

    def process_item(self, item, spider):
        if item.__class__ == Song:
            self.fake(item["sid"])
        return item
