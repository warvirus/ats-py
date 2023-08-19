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

# /usr//bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from .kiwoom_conf import *
from .kiwoom_api import kiwoom_api
from .tools import *
from .ui import *

from .web import WebViewPlus
from .kiwoom import kiwoom

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

###############################################################
class kiwoomweb(QObject, kiwoom):
    OnEventConnect = pyqtSignal([int], ['QString'])

    def __init__(self, view):
        super().__init__()

        self._view = view

    def on_login(self, is_logon: bool, user: user_info):
        """
        로그인 됬을때, 이벤트 
        """
        self._view.fireEvent("eventConnect.kiwoom", {
            "login" : is_logon, 
            "userid" : user.userId,
            "transaction": user.transaction_mode
            })
     
    # 로그인
	# 0 - 성공, 음수값은 실패
    @pyqtSlot(result=int)
    def commConnect(self):
        return self.login()

	# 로그인 상태 확인
	# 0:미연결, 1:연결완료, 그외는 에러
    @pyqtSlot(result=int)
    def getConnectState(self):
        return 1 if self.kiwoom.is_connected else 0
    
	# 로그 아웃
    @pyqtSlot(result=int)
    def commTerminate(self):
        self.kiwoom.quit()
        return 0
     
    # @pyqtSlot(str)
    #def addFavories(self, codes):
    #    codes = JSON.codes
        # self.kiwoom.quit()
     

###############################################################
# webview 사용시 전용 클래스
###############################################################
class kiwoomWebview(WebViewPlus):
	"""
	키움 전용 Webview
	"""
	def __init__(self):
		super().__init__()
		self._webkiwoom = kiwoomweb(self)
		self.urlChanged.connect(self._OnUrlChanged)

	def _OnUrlChanged(self, url):
		self.page().mainFrame().addToJavaScriptWindowObject("kiwoom", self._webkiwoom)
