# -*- coding: utf-8 -*-
"""
# Created on  2017-05-02 15:54:56

# Author  : homerX
"""
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class CookieMiddleware(object):

    def __init__(self):
        self._cookie = {}
        self.set_cookie("https://www.liepin.com")

    def set_cookie(self, url):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
        )
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.get(url)
        self._cookie = driver.get_cookies()
        driver.close()

    def process_request(self, request, spider):
        request.cookies = self._cookie
        return