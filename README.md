# ComicDownloader

download comic pictures by simulating a chrome client with selenium

requirements:

- python3
- selenium with chrome driver
- requests
- beautifulsoup4
- PyQt5=5.10 for GUI
- qdarkstyle for GUI


```
usage:
    python ComicDownloader.py -u https://ac.qq.com/ComicView/index/id/549573/cid/1
    python ComicDownloader.py --url https://ac.qq.com/ComicView/index/id/549573/cid/1
```

It supports: QQ comic/dmzj/gugu5  
check `cliexample.py` for command line examples. 
run `ui/main.py`, which is our GUI. 
