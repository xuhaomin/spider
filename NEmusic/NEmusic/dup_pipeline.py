# -*- coding: utf-8 -*-
"""
# Created on  2017-04-25 23:11:21

# Author  : homerX
"""
from NEmusic.items import Playlist, Song, Artist, Album
from scrapy.exceptions import DropItem

class DuplicatesPipeline(object):

    def __init__(self):
        self.list_id_seen = set()
        self.song_id_seen = set()
        self.artist_id_seen = set()
        self.album_id_seen = set()
        self.class_dict = [
            {"class": Playlist, "set": self.list_id_seen, "id": "lid"},
            {"class": Song, "set": self.song_id_seen, "id": "sid"},
            {"class": Artist, "set": self.artist_id_seen, "id": "artist_id"},
            {"class": Album, "set": self.album_id_seen, "id": "album_id"},
        ]

    def process_item(self, item, spider):
        for item_class in self.class_dict:
            if item.__class__ == item_class["class"]:
                if item[item_class["id"]] in item_class["set"]:
                    raise DropItem("Drop %s" % item)
                else:
                    item_class["set"].add(item[item_class["id"]])
                    return item
