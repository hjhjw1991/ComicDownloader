#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Exception.py
Created on 2020/3/26
2018-2020 all copyright reserved by huangjun
"""

class HJException(Exception):
    def __init__(self, *args):
        super().__init__(args)

