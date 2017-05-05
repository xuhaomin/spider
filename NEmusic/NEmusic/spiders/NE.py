# -*- coding: utf-8 -*-
import scrapy
from NEmusic.items import Playlist, Song, Artist, Album


import json


class NeSpider(scrapy.Spider):
    name = "NE"
    allowed_domains = ["music.163.com"]
    start_urls = ['']

    def __init__(self):
        self.play_list = 'http://music.163.com/api/playlist/list?cat={cat}&order={order}&offset={offset}&limit={limit}'
        self.playlist_detail = 'http://music.163.com/api/playlist/detail?id={lid}'
        self.limit = 50

    def start_requests(self):
        url = self.play_list.format(
            cat='全部', order='hot', limit=self.limit, offset=0)
        return [scrapy.Request(
            url=url,
            callback=self.order_to_list,
        )]

    def order_to_list(self, response):
        data = json.loads(response.text)
        self.get_list(response)
        total = data['total']
        offset = self.limit
        while offset < total:
            yield scrapy.Request(
                url=self.play_list.format(cat='全部', order='hot',
                                          limit=self.limit, offset=offset),
                callback=self.get_list,
            )
            offset += self.limit
        yield scrapy.Request(
            url=self.play_list.format(cat='全部', order='hot',
                                          limit=self.limit, offset=total),
            callback=self.get_list,
        )

    def get_list(self, response):
        data = json.loads(response.text)
        lid_list = [l["id"] for l in data["playlists"]]
        for lid in lid_list:
            yield scrapy.Request(
                url=self.playlist_detail.format(lid=lid),
                callback=self.parse_playlist
            )

    def parse_playlist(self, response):
        data = json.loads(response.text)
        playlist = Playlist()

        playlist["lid"] = int(data["result"]["id"])
        playlist["name"] = data["result"]["name"]
        playlist["creator"] = data["result"]["creator"]["nickname"]
        playlist["play_count"] = int(data["result"]["playCount"])
        playlist["img"] = data["result"]["coverImgUrl"]
        yield playlist

        for songdata in data["result"]["tracks"]:
            song = Song()
            song["sid"] = int(songdata["id"])
            song["name"] = songdata["name"]
            song["popularity"] = int(songdata["popularity"])
            song["url"] = songdata["mp3Url"]
            if songdata["artists"]:
                for artistdata in songdata["artists"]:
                    artist = Artist()
                    artist["artist_id"] = int(artistdata["id"])
                    artist["name"] = artistdata["name"]
                    artist["img"] = artistdata["picUrl"]
                    yield artist
                song["artist_id"] = int(songdata["artists"][0]["id"])
            else:
                song["artist_id"] = 0
            if songdata["album"]:
                album = Album()
                album["album_id"] = int(songdata["album"]["id"])
                album["name"] = songdata["album"]["name"]
                album["img"] = songdata["album"]["picUrl"]
                yield album
                song["album_id"] = album["album_id"]
            else:
                song["album_id"] = 0
            yield song
