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
