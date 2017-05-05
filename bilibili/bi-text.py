# -*- coding: utf-8 -*-
"""
# Created on  2017-04-11 18:31:20

# Author  : homerX
"""
import hashlib


_APP_KEY = '84956560bc028eb7'
_BILIBILI_KEY = '94aba54af9065f71de72f5508f1cd42e'
payload = 'appkey={appkey}&cid={cid}&otype=json&quality=2&type=flv'


def get_url(cid):
    p = payload.format(appkey=_APP_KEY, cid=cid)
    sign = hashlib.md5((p + _BILIBILI_KEY).encode('utf-8')).hexdigest()
    url = 'http://interface.bilibili.com/playurl?%s&sign=%s' % (p, sign)
    return url

cid = 15465663

print(get_url(cid))