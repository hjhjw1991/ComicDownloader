#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
TestChromeDriver.py
Created on 2020/3/28
2018-2020 all copyright reserved by huangjun
"""
from tests.BaseTest import BaseTestCase
import unittest


class TestNetworkDeps(BaseTestCase):
    # def testDriver(self):
    #     from selenium import webdriver
    #     option = webdriver.ChromeOptions()
    #     option.add_argument('--headless')
    #     self._driver = webdriver.Chrome(options=option)
    #     self.assertIsNotNone(self._driver)

    def testRequests(self):
        import requests
        url = "https://www.bilibili.com"
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        response = requests.get(url, headers=header)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
