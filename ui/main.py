#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
main.py
漫画下载器Gui 主入口
Created on 2020/3/20
2018-2020 all copyright reserved by huangjun
"""

from PyQt5.QtWidgets import QApplication, QComboBox, QSpinBox, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, QAction, QToolBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, QSize, pyqtSignal, QThread
import os
import re
import qdarkstyle
from ComicDownloader import QQComicDownloader


class DownloadStatus:
    (IDLE, DOWNLOADING, PAUSED) = list(range(3))


class DownloadThread(QThread):
    """漫画下载线程
    """
    name = ""
    seed = None
    count = 1
    downloader = {
        "https://ac.qq.com/": QQComicDownloader(), # qq下载器
        "https://www.dmzj.com/": None,
        "http://www.gugu5.com/": None,
    }
    progress = 0
    progress_max = 100
    finish = False
    progressBarValue = pyqtSignal(int)
    currentDownload = pyqtSignal(str)

    def __init__(self, seed="", count=1, target=None):
        super().__init__()
        self.seed = seed
        self.count = count
        self.target = target

    def update_progress(self, progress):
        self.progress = progress
        self.progressBarValue.emit(progress)
        if self.progress >= self.progress_max:
            self.finish = True

    def download(self, type="https://ac.qq.com/", url="", count=1):
        if url and type in self.downloader:
            qqdownloader = self.downloader[type]
            if "https://ac.qq.com/" != type:
                # todo supprot other site
                print("其他源暂不支持下载")
            # 浏览路径的模式
            urlPtn = "https://ac.qq.com/ComicView/index/id/{}/cid/{}"
            pattern = re.compile(urlPtn.format("([\d]+)", "([\d]+)"))
            matched = pattern.search(url)
            if matched:
                comicId = int(matched.group(1))
                cidStart = int(matched.group(2))
                progress = 0
                for id in range(cidStart, cidStart+count):
                    progress += 1
                    self.currentDownload.emit("第%d话" % id)
                    url = urlPtn.format(comicId, id)
                    qqdownloader.target(url)
                    qqdownloader.download()
                    # update progress ui
                    self.update_progress(progress*100//count)

    def save_and_exit(self):
        # todo save and exit
        self.finish = True

    def is_finished(self):
        return self.finish

    def run(self):
        if self.target:
            self.target()


class HJBrowser(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置浏览器
        self.browser = QWebEngineView()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addStretch(1)
        # 添加浏览器到窗口中
        self.setLayout(layout)

        ###使用QToolBar创建导航栏，并使用QAction创建按钮
        # 添加导航栏
        navigation_bar = QToolBar('Navigation')
        # 设定图标的大小
        navigation_bar.setIconSize(QSize(16, 16))
        # 添加导航栏到窗口中
        layout.addWidget(navigation_bar)

        # QAction类提供了抽象的用户界面action，这些action可以被放置在窗口部件中
        # 添加前进、后退、停止加载和刷新的按钮
        back_button = QAction(QIcon('icons/previous.png'), 'Back', self)
        next_button = QAction(QIcon('icons/next.png'), 'Forward', self)
        stop_button = QAction(QIcon('icons/stop_cross.png'), 'stop', self)
        reload_button = QAction(QIcon('icons/reload.png'), 'reload', self)

        back_button.triggered.connect(self.browser.back)
        next_button.triggered.connect(self.browser.forward)
        stop_button.triggered.connect(self.browser.stop)
        reload_button.triggered.connect(self.browser.reload)

        # 将按钮添加到导航栏上
        navigation_bar.addAction(back_button)
        navigation_bar.addAction(next_button)
        navigation_bar.addAction(stop_button)
        navigation_bar.addAction(reload_button)

        # 添加URL地址栏
        self.urlbar = QLineEdit()
        # 让地址栏能响应回车按键信号
        # self.urlbar.returnPressed.connect(self.navigate_to_url)
        # 不允许编辑
        self.urlbar.setReadOnly(True)

        navigation_bar.addSeparator()
        navigation_bar.addWidget(self.urlbar)

        # 让浏览器相应url地址的变化
        self.browser.urlChanged.connect(self.update_urlbar)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        self.browser.load(q)

    def update_urlbar(self, q):
        # 将当前网页的链接更新到地址栏
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def load(self, url):
        if url:
            self.browser.load(QUrl(url))


class HJWindow(QWidget):
    SITES = {
        "腾讯漫画": "https://ac.qq.com/",
        "动漫之家": "https://www.dmzj.com/",
        "古古漫画网": "http://www.gugu5.com/",
    }
    site = "https://ac.qq.com/"

    def __init__(self, title="HJ Window", parent=None):
        super().__init__(parent)
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle(title)

        self.initUI()
        self.status = DownloadStatus.IDLE

    def initUI(self):
        # 控制区
        controller_layout = QGridLayout()

        # 选择源 下载范围
        selector = QComboBox()
        selector.addItems(list(self.SITES.keys()))
        selector.activated.connect(self._selector)
        select_range = QSpinBox()
        select_range.setRange(1, 20)
        select_range.setToolTip("从当前页面开始往后下载多少话")
        self.selector = selector
        self.selectedRange = select_range
        controller_layout.addWidget(selector, 0, 0)
        controller_layout.addWidget(select_range, 1, 0)

        # 选择下载保存的位置
        choose_file_btn = QPushButton("保存到...")
        choose_file_btn.setToolTip("选择下载保存位置")
        choose_file_btn.clicked.connect(self._chooseFile)
        controller_layout.addWidget(choose_file_btn, 0, 1)

        save_path = QLineEdit()
        save_path.setText(os.path.abspath(os.curdir))
        controller_layout.addWidget(save_path, 0, 2)
        self.savePath = save_path

        # 控制下载开始/暂停
        download_panel = QHBoxLayout()
        download_ctr = QToolBar('Download')
        download_ctr.setIconSize(QSize(16, 16))
        start_btn = QAction(QIcon('assets/play.png'), 'start/pause', self)
        start_btn.triggered.connect(self._startDownload)
        stop_btn = QAction(QIcon('assets/stop.png'), 'stop', self)
        stop_btn.setVisible(False)
        stop_btn.triggered.connect(self._stopDownload)
        download_ctr.addAction(start_btn)
        download_ctr.addAction(stop_btn)
        download_panel.addWidget(download_ctr)
        controller_layout.addItem(download_panel, 0, 6, 0, 8)
        self.startBtn = start_btn
        self.stopBtn = stop_btn

        # 下载进度
        download_status = QVBoxLayout()
        download_progress_text = QLabel("当前没有下载")
        download_progress_text.setToolTip("当前下载")
        download_progress = QProgressBar()
        download_status.addWidget(download_progress_text)
        download_status.addWidget(download_progress)
        controller_layout.addItem(download_status, 2, 0, 2, 9)
        self.downloadProgress = download_progress
        self.downloadProgressText = download_progress_text

        window_layout = QVBoxLayout()
        window_layout.addLayout(controller_layout)
        window_layout.addStretch(1)

        # 内置网页浏览器
        webview = HJBrowser()
        window_layout.addWidget(webview)
        self.webview = webview
        if selector.currentText() in self.SITES:
            url = self.SITES[selector.currentText()]
            self.webview.load(QUrl(url))

        self.setLayout(window_layout)

    def _selector(self):
        value = self.selector.currentText()
        if value in self.SITES:
            self.site = self.SITES[value]
            self.webview.load(self.site)

    def _chooseFile(self):
        # 选择保存的文件夹
        choose_dialog = QFileDialog.getExistingDirectory(self,
                                                         "选取文件夹",
                                                         self.savePath.text())
        if choose_dialog:
            print(choose_dialog)
            self.savePath.setText(choose_dialog)

    def _download(self):
        # todo 断点续传
        import time
        save_path = self.savePath.text()
        if os.path.exists(save_path) and os.path.isdir(save_path):
            cwd = os.getcwd()
            os.chdir(save_path)
            print("downloading")
            qurl = self.webview.browser.url()
            self.worker.download(type=self.site, url=qurl.toString(), count=int(self.selectedRange.text()))
            os.chdir(cwd)
        else:
            self._stopDownload()

    def _update_progress(self, progress):
        self.downloadProgress.setValue(progress)
        if self.downloadProgress.value() >= self.downloadProgress.maximum():
            self._stopDownload()

    def _update_progress_target(self, name):
        if name:
            self.downloadProgressText.setText(name)

    def _startDownload(self):
        if self.status == DownloadStatus.IDLE:
            # 创建线程开始下载
            self.status = DownloadStatus.DOWNLOADING
            self.startBtn.setIcon(QIcon("assets/pause.png"))
            self.stopBtn.setVisible(True)
            self.worker = DownloadThread(target=self._download)
            self.worker.progressBarValue.connect(self._update_progress)
            self.worker.currentDownload.connect(self._update_progress_target)
            self.worker.start()
        elif self.status == DownloadStatus.PAUSED:
            # todo 继续下载
            self.status = DownloadStatus.DOWNLOADING
            self.startBtn.setIcon(QIcon("assets/pause.png"))
            # self.worker = DownloadThread(target=self._download)
            # self.worker.progressBarValue.connect(self._update_progress)
            # self.worker.start()
        elif self.status == DownloadStatus.DOWNLOADING:
            # todo 暂停下载
            self.status = DownloadStatus.PAUSED
            self.startBtn.setIcon(QIcon("assets/play.png"))
            # self.worker.save_and_exit()

    def _stopDownload(self):
        self.status = DownloadStatus.IDLE
        self.stopBtn.setVisible(False)
        self.startBtn.setIcon(QIcon("assets/play.png"))
        self._update_progress(0)
        self._update_progress_target("当前没有下载")
        if self.worker:
            print(self.worker.isFinished())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = HJWindow()
    window.show()
    sys.exit(app.exec_())
