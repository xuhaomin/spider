#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-19 17:55:06
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import requests
from lxml import etree
from selenium import webdriver
import time

s = requests.Session()
url = 'https://www.moseeker.com/job/search?keyword={key}&city={city}&candidate_source=%E5%85%A8%E9%83%A8&employment_type=%E5%85%A8%E9%83%A8&count=1&size=25'
key = ''
city = ''


def get_cookie():
    driver = webdriver.PhantomJS()
    driver.get(
        "https://www.moseeker.com/job/search?keyword=&city=&candidate_source=%E5%85%A8%E9%83%A8&employment_type=%E5%85%A8%E9%83%A8")

    time.sleep(1)
    cookies = {}
    for ele in driver.get_cookies():
        cookies[ele['name']] = ele['value']
    driver.quit()
    return cookies

cookies = get_cookie()
headers = {
    'Accept': 'application/json; charset=UTF-8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
    'X-Csrftoken': cookies["_xsrf"],
    'Connection': 'keep-alive',
    'Host': 'www.moseeker.com',
    'Referer': 'http://www.moseeker.com',
    'X-Requested-With': 'XMLHttpRequest',
}
resp = s.get(url='http://www.moseeker.com/job/search?keyword=python&city=北京&candidate_source=%E5%85%A8%E9%83%A8&employment_type=%E5%85%A8%E9%83%A8&count=1&size=100&_=1495188780864', headers=headers, cookies=cookies)

print(resp.text)


time.sleep(5)

resp = s.get(url='http://www.moseeker.com/job/search?keyword=&city=上海&candidate_source=%E5%85%A8%E9%83%A8&employment_type=%E5%85%A8%E9%83%A8&count=2&size=500&_=1495188780864', headers=headers, cookies=cookies)

print(resp.text)
