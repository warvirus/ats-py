# This file is protected under the GNU General Public License version 2.0 (GPL-2.0).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# Author : Jaosn Lee  2023.08
# Copyright(c) 2023-2025 Aistock, Co. All rights reserved.
#
# This software and its source code are released under the terms of the GPL-2.0 license.
# For more details about GPL-2.0, please visit https://www.gnu.org/licenses/gpl-2.0.html.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#

#!/usr/bin/env pythonw
#-*-coding: utf-8 -*-
import sys
import os.path
import re
from optparse import OptionParser
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QFileDialog, qApp, QAction, QMainWindow, QStatusBar, QVBoxLayout, QSplitter, QMessageBox, QInputDialog, QLineEdit
from kiwoom import kiwoomWebview

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.view = kiwoomWebview()
        self.initUI()

    def menuUI(self):
        openfile_action = QAction('&Open File', self)
        openfile_action.setShortcut('Ctrl+O') 
        openfile_action.setStatusTip('Open files')
        openfile_action.triggered.connect(self.onOpenFile)

        openurl_action = QAction('Open &Url', self)
        openurl_action.setShortcut('Ctrl+U') 
        openurl_action.setStatusTip('Open URL')
        openurl_action.triggered.connect(self.onOpenUrl)
        # exit_action = QAction(QIcon('exit.png'), "&Exit", self)
        
        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q') 
        quit_action.setStatusTip('Exit application')
        quit_action.triggered.connect(qApp.quit)

        fileMenu = self.menuBar().addMenu('Menu')
        fileMenu.addAction(openfile_action)
        fileMenu.addAction(openurl_action)
        fileMenu.addAction(quit_action)

    def initUI(self):
        self.setMinimumSize(1024, 640)
        self.setWindowTitle("QWebview-plus for Kiwoom")
        self.setCentralWidget(self.view)

        self.view.statusbar = QStatusBar()
        self.setStatusBar(self.view.statusbar)
        self.view.statusbar.showMessage("[F4키] 개발자 도구, [F5키] 화면 Refresh")
        # self.view.devTool.setVisible(True)
        
        self.menuUI()
        

    def onOpenFile(self, event):
        vOpenfilename = QFileDialog.getOpenFileName(self, 'Open File', filter="*.*")
        if vOpenfilename == "":
            return
        if os.path.isfile(vOpenfilename[0]):
            self.view.load(QUrl.fromLocalFile(vOpenfilename[0]))         

    def onOpenUrl(self, event):
        url, okPressed = QInputDialog.getText(self, "Open URL","인터넷 주소를 입력해주세요", QLineEdit.Normal, "")
        if okPressed and url != "":
            prefix = "" if bool(re.match('^(?:http)s?://', url)) else "http://"
            self.view.load(QUrl(prefix + url))


if __name__ == "__main__":
    #parsing command line arguments
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
    