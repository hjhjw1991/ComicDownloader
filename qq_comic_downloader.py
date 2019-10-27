#!/usr/bin/python
# -*- coding:utf-8 -*-

from CheckUtil import HtmlQuery
from bs4 import BeautifulSoup
import os


class QQComicDownloader(HtmlQuery):
    _driver = None
    api = ""
    save_path = ""

    def __init__(self):
        from selenium import webdriver
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        self._driver = webdriver.Chrome(options=option)

    def target(self, url):
        self.api = url

    def download(self):
        import requests
        import re
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        pageUrls = self.query()
        if pageUrls:
            self.createDir(self._driver.title)
            if not os.path.exists(self.save_path):
                print('create dir %s failed!' % self.save_path)
                return
            length = len(pageUrls)
            for i in range(length):
                url = pageUrls[i]
                print('(%d/%d) downloading %s' % (i+1, length, url))
                filename = re.findall(r'.*/(.+\.jpg)', url)
                if filename:
                    filename = str(i) + "_" + filename[0]
                    try:
                        pic = requests.get(url, headers=header)
                        if pic.status_code == 200:
                            with open(self.save_path + '/' + filename, 'wb') as fp:
                                fp.write(pic.content)
                                fp.close()
                    except Exception as e:
                        print(e)
        print('download finished!')

    def createDir(self, name):
        path = './' + name
        os.path.abspath(path)
        if not os.path.exists(name):
            os.mkdir(path)
        self.save_path = path

    def sendQueryRequest(self, **kwargs):
        # 网页内容是动态渲染的，所以我们需要模拟用户访问，让网页渲染出来
        self._driver.get(self.api)
        # 由于页面内容是懒加载，所以我们需要模拟滑动到页面底部来完成全部图片的加载
        QQComicDownloader.scrollToBottom(self._driver)
        html = self._driver.page_source.encode('utf-8')
        return html

    @staticmethod
    def scrollToBottom(driver):
        bs = BeautifulSoup(driver.page_source.encode('utf-8'), features="html.parser")
        # 获取漫画页数
        pageList = bs.find_all(name='ul', attrs={'class': 'comic-contain'})
        if not pageList:
            print('no comic found')
            return []
        pages = pageList[0].find_all(name='li')
        # 每个分页高度
        step = 1200
        # 分页数
        times = len(pages)
        # 滑动等待时间
        wait = 1000
        # 把特定元素滑动到底部
        driver.execute_script("""
        function sleep(ms) {
            return new Promise((resolve)=>setTimeout(resolve,ms));
        }
        async function moveToBottom() {
            for(var i=1;i<=%d;i++) {
                document.getElementById('mainView').scrollTop=%d * i;
                await sleep(%d)
            }
        }
        moveToBottom()
        """ % (times, step, wait))
        # 等待页面元素加载完, 单位是秒
        print('wait %d seconds for loading pages' % (wait/1000 * times))
        import time
        time.sleep(wait/1000 * times)
        print('loading finished (or timeout)')

    def resolve(self, response):
        # response是目标漫画卷的阅读页html
        # 所有漫画页都在"comic-contain"的列表中
        bs = BeautifulSoup(response, features="html.parser")
        pageList = bs.find_all(name='ul', attrs={'class': 'comic-contain'})
        if not pageList:
            print('no comic found')
            return []
        pages = pageList[0].find_all(name='li')
        imgUrl = []
        for page in pages:
            imgUrl.append(page.img['src'])
        return imgUrl


def startDownload(url):
    downloader = QQComicDownloader()
    downloader.target(url)
    downloader.download()


def usage():
    prompt = """usage:
    python %s -u https://ac.qq.com/ComicView/index/id/549573/cid/1
    python %s --url https://ac.qq.com/ComicView/index/id/549573/cid/1
    """ % (__file__, __file__)
    print(prompt)


def cli():
    from optparse import OptionParser
    optParser = OptionParser()
    optParser.add_option('-u', '--url', action = 'store', type='string', dest='url')
    option, args = optParser.parse_args()
    if not option.url:
        usage()
        return
    startDownload(option.url)


def testSelenium():
    from selenium import webdriver
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    driver = webdriver.Chrome(options=option)
    driver.get("https://ac.qq.com/ComicView/index/id/549573/cid/1")
    page = driver.page_source.encode('utf-8')
    print(page)


if __name__=='__main__':
    cli()
    # downloader = QQComicDownloader()
    # downloader.target("https://ac.qq.com/ComicView/index/id/549573/cid/1")
    # downloader.download()
    # l = downloader.query()
    # print(l)
    # testSelenium()
