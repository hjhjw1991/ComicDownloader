# -*- coding:utf-8 -*-
import re
import json
import requests, base64
from urllib.parse import urlparse


def isUrl(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def getCurrentIp():
    import json
    ipaddr = json.loads(requests.get('http://httpbin.org/ip').text)['origin']
    return ipaddr


def isEmail(email):
    raise NotImplementedError()


class Query(object):
    # must be override
    def sendQueryRequest(self, **kwargs):
        raise NotImplementedError()

    # must be override
    def resolve(self, response):
        raise NotImplementedError()

    def query(self, **kwargs):
        response = self.sendQueryRequest(**kwargs)
        return self.resolve(response)


class IpQuery(Query):
    """
    query current ip's geo info 
    """
    api = "https://ip.ws.126.net/ipquery"

    def sendQueryRequest(self, **kwargs):
        response = requests.get(self.api)
        return response

    def resolve(self, response):
        import js2py
        if not response:
            return ""
        jsResponse = js2py.eval_js(response.text)
        addr = jsResponse["city"]
        return addr


class DeliveryQuery(Query):
    """
    query delivery progress
    need to apply for official api use
    """
    api = "https://m.kuaidi100.com"
    icon = "https://cdn.kuaidi100.com/images/logo_v4_sso.png"

    def sendQueryRequest(self, **kwargs):
        pass

    def resolve(self, response):
        return self.api


class HtmlQuery(Query):

    def __init__(self):
        self.api = ""

    def sendQueryRequest(self, **kwargs):
        return requests.get(self.api).text

    def resolve(self, htmlText):
        return htmlText


class ImageQuery(Query):

    def __init__(self):
        self.api = ""

    def sendQueryRequest(self, **kwargs):
        return requests.get(self.api)

    def resolve(self, response):
        from PIL import Image
        from io import BytesIO
        # 将这个图片从内存中打开，然后就可以用Image的方法进行操作了
        image = Image.open(BytesIO(response.content))
        # 得到这个图片的base64编码
        ls_f = base64.b64encode(BytesIO(response.content).read())
        # 打印出这个base64编码
        print(type(ls_f))
        #########################
        # 下面是将base64编码进行解码
        imgdata = base64.b64decode(ls_f)
        print(imgdata)
        return ls_f
