#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
BaseTest.py
Created on 2020/3/28
2018-2020 all copyright reserved by huangjun
"""

from unittest import mock, TestCase


class BaseTestCase(TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._patcher = []

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        for patcher in self._patcher:
            patcher.stop()

    def _patch_method(self, method: str, result):
        """
        patch 某个方法, 使其返回 result
        :param method: 需要被mock.patch的方法
        :param result: 需要被patch方法返回的值
        :return: None
        """
        patcher = mock.patch(method)
        self._patcher.append(patcher)
        mock_obj = patcher.start()
        mock_obj.return_value = result
