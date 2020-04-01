#!/usr/bin/python
# -*- coding:utf-8 -*-

from hjutils.CheckUtil import HtmlQuery
from bs4 import BeautifulSoup
import os
import re


class QQComicDownloader(HtmlQuery):
    _driver = None
    api = ""
    save_path = ""

    def __init__(self):
        super().__init__()
        from selenium import webdriver
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        self._driver = webdriver.Chrome(options=option)

    def target(self, url):
        self.api = url

    def download(self):
        import requests
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
                filename = re.findall(r'.*/(.+\.((jpe?g)|(png)))', url)
                if filename:
                    filename = str(i) + "_" + filename[0][0]
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
        # create relative path dir
        path = './' + name
        path = os.path.abspath(path)
        if not os.path.exists(path):
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


class DmzjComicDownloader(QQComicDownloader):
    """动漫之家漫画下载器
    动漫之家网址格式为 https://manhua.dmzj.com/{漫画缩写}/{具体话数编号}.shtml#@page={页数}
    单html是一话
    图片格式为 https://images.dmzj.com/s/{漫画名}/{话数}/06.jpg
    例如
    https://images.dmzj.com/s/%E5%99%AC%E8%B0%8E%E8%80%85/%E7%AC%AC409%E8%AF%9D/06.jpg
    图片的网络请求需要携带来源页面的Referer，否则会被403
    """

    def __init__(self):
        super().__init__()
        self.current = None
        self.pages = {}

    def target(self, url):
        super(DmzjComicDownloader, self).target(url)
        htmlName = re.findall(r'.*/(.+\.s?html)', url)
        self.current = htmlName[0] if htmlName else None

    def download(self):
        import requests
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                  'Referer': self.api}
        pageUrls = self.query()
        if pageUrls:
            self.createDir(self._driver.title)
            if not os.path.exists(self.save_path):
                print('create dir %s failed!' % self.save_path)
                return
            length = len(pageUrls)
            # 每一张图片下载间隔
            wait = 1000
            for i in range(length):
                url = pageUrls[i]
                print('(%d/%d) downloading %s' % (i+1, length, url))
                filename = re.findall(r'.*/(.+\.((jpe?g)|(png)))', url)
                if filename:
                    filename = str(i) + "_" + filename[0][0]
                    print(filename)
                    try:
                        pic = requests.get(url, headers=header)
                        if pic.status_code == 200:
                            with open(self.save_path + '/' + filename, 'wb') as fp:
                                fp.write(pic.content)
                                fp.close()
                        else:
                            print("Error: " + str(pic.status_code))
                    except Exception as e:
                        print(e)
                    import time
                    time.sleep(wait / 1000)

        print('download finished!')

    def createDir(self, name):
        # create relative path dir
        path = './' + name
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.save_path = path

    def sendQueryRequest(self, **kwargs):
        # 网页内容是动态渲染的，所以我们需要模拟用户访问，让网页渲染出来，但是动漫之家不需要等页面加载完毕
        self._driver.get(self.api)
        html = self._driver.page_source.encode('utf-8')
        return html

    def resolve(self, response):
        # response是目标漫画卷的阅读页html
        # 所有漫画图片地址都在底部selector的值列表中，我们只需要取这一部分的内容，以及下一话和上一话的地址
        bs = BeautifulSoup(response, features="html.parser")
        # 找到选择控件，获得所有图片地址
        bottomBtBox = bs.find_all(name='div', attrs={'class': 'btmBtnBox'})
        if bottomBtBox:
            btmBtBox = bottomBtBox[0]
            pageList = btmBtBox.find_all(name='select', attrs={'id': 'page_select'})
            if not pageList:
                print('no comic found')
                return []
            pages = pageList[0].find_all(name='option')
            imgUrl = []
            suffix = 'https:'
            # 动漫之家的图片地址省略了schema，不能直接给requests用，所以我们加上schema
            for page in pages:
                url = page['value']
                if not url.startswith('http'):
                    if url.startswith('//'):
                        url = suffix + url
                    else:
                        url = suffix + '//' + url
                imgUrl.append(url)

            # 找到左右按钮，获得上下话地址
            prevPage = btmBtBox.find(name='a', attrs={'class': 'btm_chapter_btn fl'})
            nextPage = btmBtBox.find(name='a', attrs={'class': 'btm_chapter_btn fr'})
            if self.current and self.current not in self.pages:
                self.pages[self.current] = {}
                # 只取模板页面路径中缺失的部分, 在动漫之家就是只取html页面
                if prevPage:
                    prevHtml = re.findall(r'([\d]+\.s?html)', prevPage['href'])
                    self.pages[self.current]['prev'] = prevHtml[0] if prevHtml else None
                if nextPage:
                    nextHtml = re.findall(r'([\d]+\.s?html)', nextPage['href'])
                    self.pages[self.current]['next'] = nextHtml[0] if nextHtml else None
                print(self.current, self.pages[self.current])
            return imgUrl
        else:
            print('no comic found')
            return []


class GugumanhuaDownloader(DmzjComicDownloader):
    """
    古古漫画下载器
    http://www.gugu5.com/o/miliuzhiguodeailisi/
    """
    host = "http://www.gugu5.com/"

    def index(self, url):
        self._driver.get(url)
        html = self._driver.page_source.encode('utf-8')
        bs = BeautifulSoup(html, features="html.parser")
        playList = bs.find_all(name='div', attrs={'id': 'play_0'})
        if playList:
            div = playList[0]
            pages = div.find_all(name='a')
            for page in pages:
                self.pages[page['title']] = page['href']

    def resolve(self, response):
        # response是目标漫画卷的阅读页html
        # 每个页面的图片地址都是js计算出来的，所以我们模拟单页访问
        # 找到选择控件，获得本话的图片数量，好加在页面参数里载入下一页
        bs = BeautifulSoup(response, features="html.parser")
        select = bs.find_all(name='select', attrs={'id': 'qTcms_select_i2'})
        if select:
            print('trying to retrieve all pages, please wait...')
            matcher = re.compile(r'(.*/.+\.((jpe?g)|(png)))')
            pages = select[0].find_all(name='option')
            imgUrl = []
            length = len(pages)
            for i in range(length):
                print("(%d/%d) I'm working, don't worry..." % (i, length))
                page = pages[i]
                p = page['value']
                self._driver.get(self.api + '?p=' + p)
                html = self._driver.page_source.encode('utf-8')
                bs = BeautifulSoup(html, features="html.parser")
                imgTable = bs.find_all(name='td', attrs={'id': 'qTcms_Pic_middle'})
                if imgTable:
                    imgTab = imgTable[0]
                    img = imgTab.find_all(name='img')
                    if not img:
                        print('no comic found')
                        continue
                    url = matcher.findall(img[0]['src'])
                    if url:
                        imgUrl.append(url[0][0])
            return imgUrl
        else:
            print('no comic found')
            return []


def startDownloadFromQQComic(url):
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
    startDownloadFromQQComic(option.url)


def testSelenium():
    from selenium import webdriver
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    driver = webdriver.Chrome(options=option)
    driver.get("https://ac.qq.com/ComicView/index/id/549573/cid/1")
    page = driver.page_source.encode('utf-8')
    print(page)


def testDmzjDownloader():
    name = "shz"
    seedPage = "51228"
    urlPtn = "https://manhua.dmzj.com/{}/{}.shtml"
    url = urlPtn.format(name, seedPage)
    downloader = DmzjComicDownloader()
    downloader.target(url)
    downloader.download()


def testGuguDownloader():
    name = "9678"
    seedPage = "160757"
    urlPtn = "http://www.gugu5.com/n/{}/{}.html"
    index = "http://www.gugu5.com/o/miliuzhiguodeailisi/"
    url = urlPtn.format(name, seedPage)
    downloader = GugumanhuaDownloader()
    downloader.index(index)
    downloader.target(url)
    downloader.download()


if __name__=='__main__':
    # use QQComicDownloader as default
    cli()
    # testGuguDownloader()
