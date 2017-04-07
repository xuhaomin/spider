# -*- coding: utf-8 -*-
"""
# Created on  2017-04-07 15:54:56

# Author  : homerX
"""
import random
import time

import requests


class CookieMiddleware(object):

    def __init__(self):  
        self._used_count = 0
        self._invaild = 50
        self._headers = {
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        self._cookie = self.get_a_cookie()

    def get_cookie_from_this_url(self):
        cid = '{0}.{1}'.format(
            int(random.random() * (10**9)), int(time.time()))
        url = '''http://a.lagou.com/collect?v=1&_v=j31&a=1437539037
        &t=pageview&_s=1&dl=https%3A%2F%2Fwww.lagou.com%2F&ul=zh-cn
        &de=UTF-8&dt=%E6%8B%89%E5%8B%BE%E7%BD%91-%E6%9C%80%E4%B8%93%
        E4%B8%9A%E7%9A%84%E4%BA%92%E8%81%94%E7%BD%91%E6%8B%9B%E8%81%98
        %E5%B9%B3%E5%8F%B0_%E6%89%BE%E5%B7%A5%E4%BD%9C_%E6%8B%9B%E8%81%
        98_%E4%BA%BA%E6%89%8D%E7%BD%91_%E6%B1%82%E8%81%8C&sd=24-bit&sr=1680x1050
        &vp=639x690&je=0&fl=24.0%20r0&_u=MACAAAQBK~&jid=&
        cid={cid}&tid=UA-41268416-1&z=772245087'''.format(cid=cid)
        return url

    def get_a_cookie(self):
        url = self.get_cookie_from_this_url()
        resp = requests.get(url, headers=self._headers)
        return resp.cookies.get_dict()

    def process_request(self, request, spider):
        self._used_count += 1
        if self._used_count > self._invaild:
            self._cookie = self.get_a_cookie()
            self._used_count = 1
        request.cookies = self._cookie.copy()
        return
