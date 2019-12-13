#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Colored Terminal Log
"""
import os

Author = "HuangJun hjhjw1991@gmail.com"
QUITE = False
DEBUG = True


class LOGLEVEL:
    (VERBOSE, WARNING, ERROR) = range(3)


TAG = None


def _LOG(level, msg=""):
    global TAG
    if not TAG:
        TAG = os.path.basename(__file__)
    FORMAT = "[%s]: %s"
    # Color definition in Linux-like terminal
    RED = "\033[1;31m%s\033[0m"
    GREEN = "\033[1;32m%s\033[0m"
    YELLOW = "\033[1;33m%s\033[0m"
    colored = "%s"
    if level >= LOGLEVEL.ERROR:
        colored = RED
    elif level >= LOGLEVEL.WARNING:
        colored = YELLOW
    elif level >= LOGLEVEL.VERBOSE:
        colored = GREEN

    # print with color
    print(colored % (FORMAT % (TAG, msg)))


def LOG(msg, color=None):
    if not color:
        color = 'g'

    level = None
    if color == 'g':
        level = LOGLEVEL.VERBOSE
    elif color == 'r':
        level = LOGLEVEL.ERROR
    _LOG(level, msg)


def LOGV(msg):
    if not QUITE:
        _LOG(LOGLEVEL.VERBOSE, msg)


def LOGW(msg):
    if not QUITE:
        _LOG(LOGLEVEL.WARNING, msg)


def LOGD(msg):
    if DEBUG:
        _LOG(LOGLEVEL.VERBOSE, msg)


def LOGE(msg):
    _LOG(LOGLEVEL.ERROR, msg)


def flattenDictOrList(d):
    values = []
    if isinstance(d, dict):
        for value in d.values():
            if isinstance(value, (dict, list)):
                values.extend(flattenDictOrList(value))
            elif isinstance(value, str):
                values.append(value)
    elif isinstance(d, list):
        for value in d:
            if isinstance(value, (dict, list)):
                values.extend(flattenDictOrList(value))
            elif isinstance(value, str):
                values.append(value)
    return values


if __name__ == "__main__":
    print("ColoredLog module is a simple script to color terminal output.")
