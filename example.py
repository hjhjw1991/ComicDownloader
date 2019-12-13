#!/usr/local/bin/python

from ComicDownloader import QQComicDownloader, DmzjComicDownloader


def DownloadFromDmzj():
    downloader = DmzjComicDownloader()
    # 漫画id, 噬谎者
    name = "shz"
    seedMap = {
        "38249.shtml": 409,
        "42677.shtml": 428,
        "51228.shtml": 448,
    }
    seedPage = "42677.shtml"
    pageStart = 448
    pageRange = 20
    pageMax = 530

    # 初始化种子页面
    urlPtn = "https://manhua.dmzj.com/{}/{}"
    url = urlPtn.format(name, seedPage)
    downloader.target(url)
    downloader.query()

    # 按照种子页面的话数和目标起始页面的话数, 从链表中找到起始页面
    if seedPage not in downloader.pages:
        print("download seed page failed")
        return

    currentVol = seedMap[seedPage]
    currentVolUrl = seedPage
    if currentVol < pageStart:
        while currentVol < pageStart and downloader.pages[currentVolUrl]['next']:
            currentVolUrl = downloader.pages[currentVolUrl]['next']
            currentVol += 1
            url = urlPtn.format(name, currentVolUrl)
            downloader.target(url)
            downloader.query()
    elif currentVol > pageStart:
        while currentVol > pageStart and downloader.pages[seedPage]['prev']:
            currentVolUrl = downloader.pages[seedPage]['prev']
            currentVol -= 1
            url = urlPtn.format(name, currentVolUrl)
            downloader.target(url)
            downloader.query()
    if currentVol != pageStart:
        print("start page not found")
        return

    # 从起始页面开始下载, 到达终止页面或者没有下一页时停止
    while currentVol < pageStart + pageRange:
        downloader.download()
        if not downloader.pages[currentVolUrl]['next']:
            break
        currentVolUrl = downloader.pages[currentVolUrl]['next']
        currentVol += 1
        url = urlPtn.format(name, currentVolUrl)
        downloader.target(url)


def DownloadFromQQComic():
    downloader = QQComicDownloader()

    # 漫画id, 噬谎者
    comicId = "549573"
    # 起始话
    cidStart = 374
    # 每次下载的话数
    cidRange = 20
    # 最大免费话数
    cidMax = 494

    # 浏览路径的模式
    urlPtn = "https://ac.qq.com/ComicView/index/id/{}/cid/{}"

    for i in range(cidStart, cidStart+cidRange):
        if i >= cidMax:
            break
        url = urlPtn.format(comicId, i)
        downloader.target(url)
        downloader.download()


if __name__ == "__main__":
    # DownloadFromQQComic()
    DownloadFromDmzj()
