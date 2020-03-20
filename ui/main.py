#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
main.py
漫画下载器Gui 主入口
Created on 2020/3/20
2018-2020 all copyright reserved by huangjun
"""

from PyQt5.QtWidgets import QApplication, QComboBox, QSpinBox, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl
import threading
import os


class DownloadStatus:
    (IDLE, DOWNLOADING, PAUSED) = list(range(3))


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

    def initUI(self):
        # 控制区
        controllerLayout = QGridLayout()

        # 选择源 下载范围
        selector = QComboBox()
        selector.addItems(list(self.SITES.keys()))
        selector.activated.connect(self._selector)
        selectRange = QSpinBox()
        selectRange.setRange(1, 20)
        selectRange.setToolTip("从当前页面开始往后下载多少话")
        self.selector = selector
        self.selectedRange = selectRange
        controllerLayout.addWidget(selector, 0, 0)
        controllerLayout.addWidget(selectRange, 1, 0)

        # 选择下载保存的位置
        chooseFileBtn = QPushButton("保存到...")
        chooseFileBtn.setToolTip("选择下载保存位置")
        chooseFileBtn.clicked.connect(self._chooseFile)
        controllerLayout.addWidget(chooseFileBtn, 0, 1)

        savePath = QLineEdit()
        savePath.setText(os.path.abspath(os.curdir))
        controllerLayout.addWidget(savePath, 0, 2)
        self.savePath = savePath

        # 控制下载开始/暂停
        downloadPanel = QHBoxLayout()
        startBtn = QPushButton()
        startBtn.clicked.connect(self._startDownload)
        stopBtn = QPushButton()
        stopBtn.setVisible(False)
        stopBtn.clicked.connect(self._stopDownload)
        downloadPanel.addWidget(startBtn)
        downloadPanel.addWidget(stopBtn)
        controllerLayout.addItem(downloadPanel, 0, 6, 0, 9)
        self.startBtn = startBtn
        self.stopBtn = stopBtn

        # 下载进度
        downloadStatus = QVBoxLayout()
        downloadProgressText = QLabel("progress now")
        downloadProgress = QProgressBar()
        downloadStatus.addWidget(downloadProgressText)
        downloadStatus.addWidget(downloadProgress)
        controllerLayout.addItem(downloadStatus, 1, 0, 1, 9)
        self.downloadProgress = downloadProgress
        self.downloadProgressText = downloadProgressText

        windowLayout = QVBoxLayout()
        windowLayout.addLayout(controllerLayout)
        windowLayout.addStretch(1)

        # 内置网页浏览器
        webview = QWebEngineView()
        windowLayout.addWidget(webview)
        self.webview = webview
        if selector.currentText() in self.SITES:
            url = self.SITES[selector.currentText()]
            self.webview.load(QUrl(url))


        self.setLayout(windowLayout)


    def _selector(self):
        value = self.selector.currentText()
        if value in self.SITES:
            self.site = self.SITES[value]
            self.webview.load(QUrl(self.site))

    def _chooseFile(self):
        # 选择保存的文件夹
        chooseDialog = QFileDialog.getExistingDirectory(self,
                                                     "选取文件夹",
                                                     self.savePath.text())
        if chooseDialog:
            print(chooseDialog)
            self.savePath.setText(chooseDialog)

    def _startDownload(self):
        # todo pause/continue download
        if self.status == DownloadStatus.IDLE:
            # start
            self.status = DownloadStatus.DOWNLOADING
        elif self.status == DownloadStatus.PAUSED:
            # continue
            self.status = DownloadStatus.DOWNLOADING
        elif self.status == DownloadStatus.DOWNLOADING:
            # pause
            self.status = DownloadStatus.PAUSED

    def _stopDownload(self):
        # todo stop download
        self.status = DownloadStatus.IDLE


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = HJWindow()
    window.show()
    sys.exit(app.exec_())

