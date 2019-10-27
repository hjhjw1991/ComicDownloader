#!/usr/local/bin/python

from qq_comic_downloader import QQComicDownloader

downloader = QQComicDownloader()

# 漫画id, 噬谎者
comicId = "549573"
# 起始话
cidStart = 234
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

