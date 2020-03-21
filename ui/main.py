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


class DownloadStatus:
    (IDLE, DOWNLOADING, PAUSED) = list(range(3))


class DownloadThread(QThread):
    """漫画下载线程
    """
    name = ""
    seed = None
    count = 1
    downloader = None
    progress = 0
    progress_max = 100
    finish = False
    progressBarValue = pyqtSignal(int)

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
    site = None

    def __init__(self, title="HJ Window", parent=None):
        super().__init__(parent)
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle(title)

        self.initUI()
        self.status = DownloadStatus.IDLE

    def setupSkin(self):
        BACKGROUND_COLOR = "#222222"
        TITLE_COLOR = '#FFFF00'

        Qss = 'QWidget#widget_2{background-color: %s;}' % BACKGROUND_COLOR
        Qss += 'QWidget#widget{background-color: %s;border-top-right-radius:5 ;border-top-left-radius:5 ;}' % TITLE_COLOR
        Qss += 'QWidget#widget_3{background-color: %s;}' % TITLE_COLOR
        Qss += 'QPushButton#pushButton{background-color: %s;border-image:url(./img/btn_close_normal.png);border-top-right-radius:5 ;}' % TITLE_COLOR
        Qss += 'QPushButton#pushButton:hover{border-image:url(./img/btn_close_down2.png); border-top-right-radius:5 ;}'
        Qss += 'QPushButton#pushButton:pressed{border-image:url(./img/btn_close_down.png);border-top-right-radius:5 ;}'
        Qss += 'QPushButton#pushButton_2{background-color: %s;border-image:url(./img/btn_min_normal.png);}' % TITLE_COLOR
        Qss += 'QPushButton#pushButton_2:hover{background-color: %s;border-image:url(./img/btn_min_normal.png);}' % BACKGROUND_COLOR
        Qss += 'QPushButton#pushButton_2:pressed{background-color: %s;border-top-left-radius:5 ;}' % BACKGROUND_COLOR
        Qss += 'QPushButton#pushButton_3{background-color: %s;border-top-left-radius:5 ;border:0;}' % TITLE_COLOR
        Qss += '#label{background-color:rbga(0,0,0,0);color: %s;}' % BACKGROUND_COLOR
        self.setStyleSheet(Qss)  # 边框部分qss重载

    def initUI(self):
        # 初始化窗口主题配色
        self.setupSkin()

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
        start_btn = QPushButton()
        start_btn.setStyleSheet("QPushButton{border-image: url(assets/play.png)}")
        start_btn.clicked.connect(self._startDownload)
        stop_btn = QPushButton()
        stop_btn.setVisible(False)
        stop_btn.setStyleSheet("QPushButton{border-image: url(assets/stop.png)}")
        stop_btn.clicked.connect(self._stopDownload)
        download_panel.addWidget(start_btn)
        download_panel.addWidget(stop_btn)
        controller_layout.addItem(download_panel, 0, 6, 0, 9)
        self.startBtn = start_btn
        self.stopBtn = stop_btn

        # 下载进度
        download_status = QVBoxLayout()
        download_progress_text = QLabel("progress now")
        download_progress = QProgressBar()
        download_status.addWidget(download_progress_text)
        download_status.addWidget(download_progress)
        controller_layout.addItem(download_status, 1, 0, 1, 9)
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
        import time
        progress = 10
        while not self.worker.is_finished() and self.status == DownloadStatus.DOWNLOADING:
            print("downloading")
            self.worker.update_progress(progress)
            progress += 10
            time.sleep(1)

    def _update_progress(self, progress):
        # todo update progress bar and text
        self.downloadProgress.setValue(progress)
        if self.downloadProgress.value() >= self.downloadProgress.maximum():
            self._stopDownload()

    def _startDownload(self):
        # todo pause/continue download
        if self.status == DownloadStatus.IDLE:
            # start
            self.status = DownloadStatus.DOWNLOADING
            self.startBtn.setStyleSheet("QPushButton{border-image: url(assets/pause.png)}")
            self.stopBtn.setVisible(True)
            # self.worker.resume()
            self.worker = DownloadThread(target=self._download)
            self.worker.progressBarValue.connect(self._update_progress)
            self.worker.start()
        elif self.status == DownloadStatus.PAUSED:
            # continue
            self.status = DownloadStatus.DOWNLOADING
            self.startBtn.setStyleSheet("QPushButton{border-image: url(assets/pause.png)}")
            # self.worker.pause()
        elif self.status == DownloadStatus.DOWNLOADING:
            # pause
            self.status = DownloadStatus.PAUSED
            self.startBtn.setStyleSheet("QPushButton{border-image: url(assets/play.png)}")
            # self.worker.resume()

    def _stopDownload(self):
        # todo stop download
        self.status = DownloadStatus.IDLE
        self.stopBtn.setVisible(False)
        self.startBtn.setStyleSheet("QPushButton{border-image: url(assets/play.png)}")
        if self.worker:
            print(self.worker.isFinished())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = HJWindow()
    window.show()
    sys.exit(app.exec_())
