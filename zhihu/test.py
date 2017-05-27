#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from lxml import etree

url_hot = 'https://www.zhihu.com/node/ExploreAnswerListV2?params='
url_reco = 'https://www.zhihu.com/node/ExploreRecommendListV2'
headers = {
    'USER-AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'}


def gen_hot_url(offset, kind):
    params = {'offset': offset, 'type': kind}
    return url_hot + json.dumps(params)


def gen_reco_data(offset, limit=20):
    params = {"offset": offset, "limit": limit}
    data = {'method': 'next', 'params': json.dumps(params)}
    return data


def get_hot_content(offset, kind):
    s = requests.get(url=gen_hot_url(offset, kind), headers=headers)
    return s


def get_reco_content(offset, limit=20):
    resp = requests.post(url=url_reco, data=gen_reco_data(offset, limit), headers=headers)
    content = json.loads(resp.text)
    return content
