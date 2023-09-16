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


# from gui import *

# from kiwoom.ui import *
# from kiwoom.tools import *

from PyQt5.QtGui import QFont
from PyQt5 import uic
import datetime as dt
import time
import logging
import socket

from ats_const import *
from baseATS import baseWindow

# app 정보
form_class = uic.loadUiType("ui/ui_main.ui")[0]
_mid_risk = -5.0
_disp_title = {
    # key : "타이틀명'
    10: "현재가",
    11: "전일대비",
    12: "등락율"
}

# 거래모드 
TAB_MODE_NOTSELECT = -1
TAB_MODE_BUY = 0
TAB_MODE_SELL = 1
TAB_MODE_UPDATE = 2

# 화면모드 거래/미수량/설정
TRAN_MODE_TRADE = 0
TRAN_MODE_UNPAID = 1
TRAN_MODE_SETUP = 2

# UI
MINISECTIONSIZE = 14
DEFAULTSECTIONSIZE = 14
DEFAULTTRADESECTIONSIZE = 20

# window 시작 옵션
class opt_struct:
    auto_running: bool = False      # 
    trade_min: bool = False
    develop_mode: bool = False
    ui_only_mode: bool = False
    hoga_dump: bool = False
    use_external_srv: bool = False
    external_server: str = ''           


def setDefaultTbl(tbl, defaultSectionSize=DEFAULTSECTIONSIZE, fontname=None, fontsize=None):
    tbl.verticalHeader().setDefaultSectionSize(defaultSectionSize)


# log, config, temp 명 설정
_log_my_stocks_name = 'my_stocks-{}.json'.format(socket.gethostname())
_config_filename = 'config-{}.json'.format(socket.gethostname())


disp_hoga_table = [
    # realtime, req_hoga, row, col, fcolor, bcolor
    ['매도호가1', '매도최우선호가', 0, 1, None, None],
    ['매수호가1', '매수최우선호가', 0, 2, None, None],

    # 매도
    ['매도호가10', '매도10차선호가', 1, 2, None,             QColor(210,210,255)],
    ['매도호가수량10', '매도10차선잔량', 1, 1, QColor(0,0,0), QColor(210,210,255)],

    ['매도호가9', '매도9차선호가', 2, 2, None,             QColor(215,215,255)],
    ['매도호가수량9', '매도9차선잔량', 2, 1, QColor(0,0,0), QColor(215,215,255)],

    ['매도호가8', '매도8차선호가', 3, 2, None,             QColor(220,220,255)],
    ['매도호가수량8', '매도8차선잔량', 3, 1, QColor(0,0,0), QColor(220,220,255)],

    ['매도호가7', '매도7차선호가', 4, 2, None,             QColor(225,225,255)],
    ['매도호가수량7', '매도7차선잔량', 4, 1, QColor(0,0,0), QColor(225,225,255)],

    ['매도호가6', '매도6차선호가', 5, 2, None,             QColor(230,230,255)],
    ['매도호가수량6', '매도6우선잔량', 5, 1, QColor(0,0,0), QColor(230,230,255)],       # 버그 ?

    ['매도호가5', '매도5차선호가', 6, 2, None,             QColor(235,235,255)],
    ['매도호가수량5', '매도5차선잔량', 6, 1, QColor(0,0,0), QColor(235,235,255)],

    ['매도호가4', '매도4차선호가', 7, 2, None,             QColor(240,240,255)],
    ['매도호가수량4', '매도4차선잔량', 7, 1, QColor(0,0,0), QColor(240,240,255)],

    ['매도호가3', '매도3차선호가', 8, 2, None,             QColor(245,245,255)],
    ['매도호가수량3', '매도3차선잔량', 8, 1, QColor(0,0,0), QColor(245,245,255)],

    ['매도호가2', '매도2차선호가', 9, 2, None,             QColor(250,250,255)],
    ['매도호가수량2', '매도2차선잔량', 9, 1, QColor(0,0,0), QColor(250,250,255)],

    ['매도호가1', '매도최우선호가', 10, 2, None,             QColor(255,255,255)],
    ['매도호가수량1', '매도최우선잔량', 10, 1, QColor(0,0,0), QColor(255,255,255)],      

    # 매수

    ['매수호가1', '매수최우선호가', 11, 2, None,             QColor(255,255,255)],
    ['매수호가수량1', '매수최우선잔량', 11, 3, QColor(0,0,0), QColor(255,255,255)],      

    ['매수호가2', '매수2차선호가', 12, 2, None,             QColor(255,250,250)],
    ['매수호가수량2', '매수2차선잔량', 12, 3, QColor(0,0,0), QColor(255,250,250)],       

    ['매수호가3', '매수3차선호가', 13, 2, None,             QColor(255,245,245)],
    ['매수호가수량3', '매수3차선잔량', 13, 3, QColor(0,0,0), QColor(255,245,245)],       

    ['매수호가4', '매수4차선호가', 14, 2, None,             QColor(255,240,240)],
    ['매수호가수량4', '매수4차선잔량', 14, 3, QColor(0,0,0), QColor(255,240,240)],       

    ['매수호가5', '매수5차선호가', 15, 2, None,             QColor(255,235,235)],
    ['매수호가수량5', '매수5차선잔량', 15, 3, QColor(0,0,0), QColor(255,235,235)],       

    ['매수호가6', '매수6우선호가', 16, 2, None,             QColor(255,230,230)],
    ['매수호가수량6', '매수6우선잔량', 16, 3, QColor(0,0,0), QColor(255,230,230)],       # 버그 ?

    ['매수호가7', '매수7차선호가', 17, 2, None,             QColor(255,225,225)],
    ['매수호가수량7', '매수7차선잔량', 17, 3, QColor(0,0,0), QColor(255,225,225)],      

    ['매수호가8', '매수8차선호가', 18, 2, None,             QColor(255,220,220)],
    ['매수호가수량8', '매수8차선잔량', 18, 3, QColor(0,0,0), QColor(255,220,220)],     

    ['매수호가9', '매수9차선호가', 19, 2, None,             QColor(255,215,215)],
    ['매수호가수량9', '매수9차선잔량', 19, 3, QColor(0,0,0), QColor(255,215,215)],      

    ['매수호가10', '매수10차선호가', 20, 2, None,             QColor(255,210,210)],
    ['매수호가수량10', '매수10차선잔량', 20, 3, QColor(0,0,0), QColor(255,210,210)],      

    ['호가시간', '호가잔량기준시간', 21, 2, None, None],

    # 매도/매수 총량
    ['매도호가총잔량', '총매도잔량', 21, 1, QColor(0,0,255),             QColor(225,255,255)],
    ['매수호가총잔량', '총매수잔량', 21, 3, None, QColor(225,255,255)],       

    # 시간외 호가
    ['', '시간외매도잔량', 22, 1, QColor(0,0,255), QColor(225,255,255)],       
    ['', '시간외매수잔량', 22, 3, None, QColor(225,255,255)],    

    # 채결 수량
    # ['LP매도호가수량10','', 1, 0, None, None],       
    # ['LP매도호가수량9', '', 2, 0, None, None],       
    # ['LP매도호가수량8', '', 3, 0, None, None],       
    # ['LP매도호가수량7', '', 4, 0, None, None],       
    # ['LP매도호가수량6', '', 5, 0, None, None],       
    # ['LP매도호가수량5', '', 6, 0, None, None],       
    # ['LP매도호가수량4', '', 7, 0, None, None],       
    # ['LP매도호가수량3', '', 8, 0, None, None],       
    # ['LP매도호가수량2', '', 9, 0, None, None],       
    # ['LP매도호가수량1', '', 10, 0, None, None],       

    # ['LP매수호가수량1',  '', 11, 4, None, None],    
    # ['LP매수호가수량2',  '', 12, 4, None, None],    
    # ['LP매수호가수량3',  '', 13, 4, None, None],    
    # ['LP매수호가수량4',  '', 14, 4, None, None],    
    # ['LP매수호가수량5',  '', 15, 4, None, None],    
    # ['LP매수호가수량6',  '', 16, 4, None, None],    
    # ['LP매수호가수량7',  '', 17, 4, None, None],    
    # ['LP매수호가수량8',  '', 18, 4, None, None],    
    # ['LP매수호가수량9',  '', 19, 4, None, None],    
    # ['LP매수호가수량10', '', 20, 4, None, None],       
]

disp_hoga_trade_table = [
    # realtime, req_hoga, row, col, fcolor, bcolor
    ['(최우선)매도호가)', 0, 1, None, None],
    ['(최우선)매수호가', 0, 2, None, None],
]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, baseWindow, form_class):
    def __init__(self, opt: opt_struct):
        super().__init__(auto_run=opt.auto_running, develop_mode=opt.develop_mode, config_file=_config_filename)
        self.setupUi(self)

        # argv, argc
        self.opt = opt
        self.options = {}           # 환경설정 값
        self.__tmp_options = {}     # 임시 환경설정 값

        self._trade_func_method = {
            'default': '4',
            'methods': {
                '1': {'name': '단타매매', 'start': '0900', 'end': '1130', "func": None,
                      'option': {'매도조건': '고정대비'}},
                '2': {'name': '스윙매매', 'start': '0900', 'end': '1310', "func": None,
                      'option': {'매도조건': '평균단가'}},
                '3': {'name': '지능형매매', 'start': '0900', 'end': '1310', "func": None,
                      'option': {'매도조건': '지능형'}},
                '4': {'name': 'MACD매매', 'start': '1300', 'end': '1310', "func": None, # self._trade_macd,
                      'option': {'매도조건': '매수후'}}
            }
        }

        # self.setGeometry(100, 100, 1300, 800)
        self.setWindowTitle("{} ver {} ({}) ".format(ats_info.title, ats_info.version, ats_info.build))
        # self.setWindowIcon( QIcon( "icon.png" ) )

        self.gui_lock(True)

        # logging...
        _log_file = 'ats-{}'.format(socket.gethostname())
        logLayout = setLogging(self, prev_hdr=_log_file)
        self.layoutLogMsg.addLayout(logLayout)  # layout 설정

        # menubar
        self.actionLogin.setShortcut('Ctrl+L')
        self.actionLogin.setStatusTip('HTS 서버에 접속시도')
        self.actionLogin.triggered.connect(self.actionLogin_click)

        self.actionLogout.setShortcut('Ctrl+F')
        self.actionLogout.setStatusTip('HTS 서버로부터 접속해지')
        self.actionLogout.triggered.connect(self.actionLogout_click)

        self.action_Exit.setShortcut('Ctrl+Q')
        self.action_Exit.setStatusTip('프로그램 종료')
        self.action_Exit.triggered.connect(self.action_Exit_click)

        self.actionATS_about.setShortcut('Ctrl+A')
        self.actionATS_about.setStatusTip('HTS 란 ....')
        self.actionATS_about.triggered.connect(self.actionATS_about_click)

        # 윈도우에 있는 콘드롤들에 대한 크기 및 이벤트 설정
        self.sizeControl()

        # ------ user layout ------
        font = QFont()
        font.setPointSize(8)
        stylesheet = "::section{Background-color:rgb(0,170,170)}"
        self.tbl_accounts_detail.setFont(font)
        self.tbl_accounts_detail.horizontalHeader().setStyleSheet(stylesheet)
        self.tbl_accounts_detail.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_accounts_detail.verticalHeader().hide()
        setTableHeader(self.tbl_accounts_detail, headers=['선택', '구분',
                                                          '종목코드',
                                                          '종목명',
                                                          '현재가',
                                                          '보유수량',
                                                          '매입가',
                                                          '평가금액',
                                                          '수익률', '평가손익', '매입시간', '매매방식', '자동매매'])

        self.tbl_account_info.setFont(font)
        self.tbl_account_info.horizontalHeader().setStyleSheet(stylesheet)
        self.tbl_account_info.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_account_info.verticalHeader().hide()
        setTableHeader(self.tbl_account_info, headers=[x for x in self.my_asset])

        self.tbl_account_info.setRowCount(1)
        self.tbl_account_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_account_info.setSelectionMode(QAbstractItemView.NoSelection)
        # self.tbl_account_info.setEnabled(False)
        # ------ user layout ------

        self.showMaximized()

        logging.debug('---------- 주식자동 드레이딩 {} ver {} ({}) 시작 ----------'.format(ats_info.title,
                                                                                 ats_info.version, ats_info.build))

        # 시계
        self.timerClock = QTimer()
        self.timerClock.setInterval(1000)
        self.timerClock.timeout.connect(self.disp_Time)
        self.timerClock.start()

        # GUI 테스트용
        if self.opt.ui_only_mode:
            return

        # auto login
        self.actionLogin_click()

    def sizeControl(self):

        # 매매(자동) 거래 이벤트
        self.btn_ats_START.clicked.connect(self.start_ATS)
        self.btn_ats_STOP.clicked.connect(self.stop_ATS)
        self.btn_AutoAnalysis.clicked.connect(self.do_Analysis)
        self.btn_StopAnalysis.clicked.connect(self.stop_Analysis)

        # 주식 거래 이벤트
        self.btn_Sale.clicked.connect(self.do_Sale)
        self.btn_Buy.clicked.connect(self.do_Buy)
        self.btn_Change.clicked.connect(self.do_Change)
        self.btn_Cancel.clicked.connect(self.do_Cancel)

        self.btn_buy_search.clicked.connect(self.btn_buy_search_click)
        self.btn_sell_search.clicked.connect(self.btn_sell_search_click)

        self.ch_buy_realtime.stateChanged.connect(self.ch_buy_realtime_click)
        self.ch_sell_realtime.stateChanged.connect(self.ch_sell_realtime_click)
        self.ch_update_realtime.stateChanged.connect(self.ch_update_realtime_click)

        self.ch_buy_auto_price.stateChanged.connect(self.ch_buy_auto_price_click)
        self.ch_sell_auto_price.stateChanged.connect(self.ch_sell_auto_price_click)
        self.ch_update_auto_price.stateChanged.connect(self.ch_update_auto_price_click)

        # list 이벤트
        self.tbl_accounts_detail.cellClicked.connect(self.detail_accounts_clicked)  # 거래현황 클릭
        self.tbl_Kwansim.cellClicked.connect(self.detail_kwansim_clicked)  # 관심등록 클릭
        self.tbl_case_condition.cellClicked.connect(self.detail_condition_clicked)  # 실시간 조건 클릭
        self.tbl_unpaid_stocks.cellClicked.connect(self.tbl_unpaid_stocks_clicked)  # 미수거래 클릭
        self.tbl_detail_stock_hoga.cellClicked.connect(self.tbl_detail_stock_hoga_clicked)  # 호가창 클릭
        self.tbl_trade_case.cellClicked.connect(self.tbl_trade_case_cellclicked)  # 조건별 거래창 클릭
        self.tbl_auto_trade.cellClicked.connect(self.tbl_auto_trade_clicked)  # 거래현황 클릭

        self.tabWidget.tabBar().currentChanged.connect(self.tabWidgetChanged)
        self.tabOrder.tabBar().currentChanged.connect(self.tabOrderChanged)

        # chart button
        self.rd_chart_tick.clicked.connect(self.rd_chart_opt_clicked)  # tick 차트 클릭
        self.rd_chart_min.clicked.connect(self.rd_chart_opt_clicked)  # 분봉 차트 클릭
        self.rd_chart_day.clicked.connect(self.rd_chart_opt_clicked)  # 일봉 차트 클릭
        self.rd_chart_week.clicked.connect(self.rd_chart_opt_clicked)  # 주봉 클릭
        self.rd_chart_month.clicked.connect(self.rd_chart_opt_clicked)  # 월봉 클릭

        # tick, minute 선택
        self.chart_step_1.clicked.connect(self.rd_chart_opt_detail_clicked)  # 1분봉 클릭
        self.chart_step_3.clicked.connect(self.rd_chart_opt_detail_clicked)  # 3분봉 클릭
        self.chart_step_5.clicked.connect(self.rd_chart_opt_detail_clicked)  # 5분봉 클릭
        self.chart_step_10.clicked.connect(self.rd_chart_opt_detail_clicked)  # 10분봉 클릭
        self.chart_step_15.clicked.connect(self.rd_chart_opt_detail_clicked)  # 15분봉 클릭
        self.chart_step_20.clicked.connect(self.rd_chart_opt_detail_clicked)  # 20분봉 클릭
        self.chart_step_30.clicked.connect(self.rd_chart_opt_detail_clicked)  # 30분봉 클릭
        self.chart_step_45.clicked.connect(self.rd_chart_opt_detail_clicked)  # 45분봉 클릭
        self.chart_step_60.clicked.connect(self.rd_chart_opt_detail_clicked)  # 60분봉 클릭

        # 초기화 '일' 단위
        self.chart_step_1.setEnabled(False)
        self.chart_step_3.setEnabled(False)
        self.chart_step_5.setEnabled(False)
        self.chart_step_10.setEnabled(False)
        self.chart_step_15.setEnabled(False)
        self.chart_step_20.setEnabled(False)
        self.chart_step_30.setEnabled(False)
        self.chart_step_45.setEnabled(False)
        self.chart_step_60.setEnabled(False)

        # 조건식
        self.btn_load_trade_case.clicked.connect(self.load_trade_case_click)
        self.btn_save_trade_case.clicked.connect(self.save_trade_case_click)

        # 환경설정
        self.btn_opt_loginWindow.clicked.connect(self.option_btn_opt_loginWindow_click)
        # txt_passwd

        # init widgets
        self.init_disp_values()
        self.init_disp_account_detail()
        self.init_disp_kwansim()
        self.init_disp_trade_case()
        self.init_unpaid_stock_list()
        self.init_detail_stock()
        self.init_detail_stock_hoga()

        self.init_controls()

        self.gui_lock(False)
        self.btn_AutoAnalysis.setEnabled(True)
        self.btn_StopAnalysis.setEnabled(False)

        self.ch_Force.setChecked(False)

        """

        # 윈도우 사이즈 고정
        self.setFixedSize(self.size())

        ### chart 설정
        ## 소스 참조 : 
        #           1. https://wikidocs.net/4766
        #           2. https://besixdouze.net/22
        #           3. https://jsp-dev.tistory.com/entry/Python%EC%9C%BC%EB%A1%9C-%EC%BA%94%EB%93%A4%EC%8A%A4%ED%8B%B1-%EC%B0%A8%ED%8A%B8-Candlestick-chart-%EA%B7%B8%EB%A6%AC%EA%B8%B0
        #           4. https://eslife.tistory.com/925
        # Figure 를 먼저 만들고 레이아웃에 들어 갈 sub axes 를 생성 한다.
        font_name = fm.FontProperties(fname="c:/Windows/Fonts/arial.ttf").get_name()
        # ont_name = fm.FontProperties(fname="c:/Windows/Fonts/NanumGothicOTF.ttf").get_name()
        plt.margins(0.2)
        # plt.rc('font', family=font_name) 
        # margin
        plt.subplots_adjust(left=0.1, bottom=0.1, right=0.6, top=0.8)

        self.fig = plt.Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.fig)

        self.chartlayout.addWidget(self.canvas)
        
        """

        # tab colors
        # self.tabWidget.
        self.__tabWidget_tabIndex = 0
        self.tabWidgetChanged(0)
        self.tabOrderChanged(0)

        # btn_1이 눌리면 작동할 함수

    def start_ATS(self):
        logging.info("========================")
        logging.info("자동 매매가 시작 되었습니다.")
        logging.info("========================")

        self.btn_ats_START.setEnabled(False)
        self.btn_ats_STOP.setEnabled(True)
        self.btn_AutoAnalysis.setEnabled(False)
        self.btn_StopAnalysis.setEnabled(False)

        # 자동매매 시작
        self.auto_analysis = True

    def stop_ATS(self):
        logging.info("========================")
        logging.info("자동 매매가 중지 되었습니다.")
        logging.info("========================")

        # 자동매매 중지
        self.auto_analysis = False

        self.btn_ats_START.setEnabled(True)
        self.btn_ats_STOP.setEnabled(False)
        self.btn_AutoAnalysis.setEnabled(True)
        self.btn_StopAnalysis.setEnabled(False)

    def do_Analysis(self):
        retval = QMessageBox.information(
            self, '주식 AI 분석', "주식 자동 분석을 실행 하시겠습니까 ?",
            QMessageBox.Yes, QMessageBox.No
        )

        # retval = msg.exec_()
        if retval == QMessageBox.Yes:
            self.btn_ats_START.setEnabled(False)
            self.btn_ats_STOP.setEnabled(False)

            self.btn_AutoAnalysis.setEnabled(False)
            self.btn_StopAnalysis.setEnabled(True)

            bForce = True
            if self.ch_Force.isChecked():  # 처음부터 ?
                bForce = False

            # # self.ats.do_analysis_stock(force=bForce)

            self.btn_AutoAnalysis.setEnabled(True)
            self.btn_StopAnalysis.setEnabled(False)

            self.btn_ats_START.setEnabled(True)
            self.btn_ats_STOP.setEnabled(False)

    def stop_Analysis(self):
        retval = QMessageBox.information(
            self, '주식 AI 분석', "주식 자동 분석을 중지 하시겠습니까 ?",
            QMessageBox.Yes, QMessageBox.No
        )

        # retval = msg.exec_()
        if retval == QMessageBox.Yes:
            self.btn_ats_START.setEnabled(False)
            self.btn_ats_START.setEnabled(False)

            # # self.ats.stop_analysis_stock()

            self.btn_AutoAnalysis.setEnabled(True)
            self.btn_StopAnalysis.setEnabled(False)

            self.btn_AutoAnalysis.setEnabled(True)
            self.btn_StopAnalysis.setEnabled(False)

    def disp_Time(self):
        clock = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.lbl_disp_timer.setText(clock)

    def ch_buy_realtime_click(self):
        if self.ch_buy_realtime.isChecked():
            print("self.lbl_buy_stock_price.configure( state='enabled')")
        else:
            print("self.lbl_buy_stock_price.configure( state='disabled' )")

    def ch_sell_realtime_click(self):
        if self.ch_sell_realtime.isChecked():
            print("self.lbl_sell_stock_price.configure( state='enabled' )")
        else:
            print("self.lbl_sell_stock_price.configure( state='disabled' )")

    def ch_update_realtime_click(self):
        if self.ch_update_realtime.isChecked():
            print("self.lbl_update_stock_price.configure( state='enabled' )")
        else:
            print("self.lbl_update_stock_price.configure( state='disabled' )")

    def ch_buy_auto_price_click(self):
        if self.ch_buy_auto_price.isChecked():
            print("self.lbl_buy_stock_price.configure( state='enabled' )")
        else:
            print("self.lbl_buy_stock_price.configure( state='disabled' )")

    def ch_sell_auto_price_click(self):
        if self.ch_sell_auto_price.isChecked():
            print("self.lbl_sell_stock_price.configure( state='enabled' )")
        else:
            print("self.lbl_sell_stock_price.configure( state='disabled' )")

    def ch_update_auto_price_click(self):
        if self.ch_update_auto_price.isChecked():
            print("self.lbl_update_stock_price.configure( state='enabled' )")
        else:
            print("self.lbl_update_stock_price.configure( state='disabled' )")

    def actionLogin_click(self):
        """
        loggin...
        :return:
        """
        # login...
        # self.config_filename = 'ats-config.json'
        # self.log_my_stocks_name = 'ats_my_stocks.json'
        is_connected = self.login()
        if is_connected == True: 
            self.gui_lock(False)
            self.processing_ready()

            # auto running ?
            if self.auto_running:
                self.start_ATS()

    def gui_lock(self, bLock):
        if bLock:
            self.btn_ats_START.setEnabled(False)
            self.btn_ats_STOP.setEnabled(False)
        else:
            self.btn_ats_START.setEnabled(True)
            self.btn_ats_STOP.setEnabled(False)

    def actionLogout_click(self):
        """

        :return:
        """

    def action_Exit_click(self):
        """
        :return:
        """
        # QCoreApplication.instance().quit()
        self.close()

    def actionATS_about_click(self):
        """
        :return:
        """

    def processing_ready(self, bauto = False, msec=60000):
        """
        서버에 접속을 하고, 트레이딩 사전 작업을 실행 한다.
        """
        super().processing_ready()

        # 조건 검색을 실행한다.
        if OPTIONS in self.config and OPTIONS_CONDITIONS in self.config[OPTIONS]:
            self.set_realtime_conditions(self.config[OPTIONS][OPTIONS_CONDITIONS])
        

    def init_controls(self):
        cob_db_item_list = list(order_gb1.keys())
        self.cob_sell_gb_list.addItems(cob_db_item_list)
        self.cob_buy_gb_list.addItems(cob_db_item_list)

        # statusbar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.statusBar.showMessage("Ready....")

    def get_current_taborder(self):
        """
        주문창에 현재 선택한 거래 내용
        :return: 0 : 매수, 1 : 매도, 2 : 정정/수정
        """
        if self.tabOrder.currentIndex() == 0:
            return TAB_MODE_BUY
        elif self.tabOrder.currentIndex() == 1:
            return TAB_MODE_SELL
        elif self.tabOrder.currentIndex() == 2:
            return TAB_MODE_UPDATE
        else:
            return TAB_MODE_NOTSELECT

    def get_current_stock(self):
        """
        주문창에 현재 선택한 주식 종목 코드
        :return: 0 : 매수, 1 : 매도, 2 : 정정/수정
        """
        selcted_code = ""
        idx = self.get_current_taborder()
        if idx == TAB_MODE_BUY:
            selcted_code = str(self.lbl_buy_stock_code.currentText())
        elif idx == TAB_MODE_SELL:
            selcted_code = str(self.lbl_sell_stock_code.currentText())

        return selcted_code

    def init_detail_stock(self):
        """
        일반 컨트롤 초기화
        :return:
        """

        # dashboard
        setTableHeader(self.tbl_stock_dashboard, row=4, col=3)
        setDefaultTbl(self.tbl_stock_dashboard, MINISECTIONSIZE)

        setTableWidgetItem(self.tbl_stock_dashboard, 0, 0, "코스피", b_color=QColor(220, 220, 255))
        setTableWidgetItem(self.tbl_stock_dashboard, 1, 0, "코스피200", b_color=QColor(220, 220, 255))
        setTableWidgetItem(self.tbl_stock_dashboard, 2, 0, "코스닥", b_color=QColor(220, 220, 255))
        setTableWidgetItem(self.tbl_stock_dashboard, 3, 0, "코스닥100", b_color=QColor(220, 220, 255))

        # dash board 2 (개인, 외국인, 기관 의 매수/매도 정보
        setTableHeader(self.tbl_stock_dashboard_2, row=4, col=3)
        setDefaultTbl(self.tbl_stock_dashboard_2, MINISECTIONSIZE)

        setTableWidgetItem(self.tbl_stock_dashboard_2, 0, 1, "코스피", b_color=QColor(220, 255, 255))
        setTableWidgetItem(self.tbl_stock_dashboard_2, 0, 2, "코스닥", b_color=QColor(220, 255, 255))
        setTableWidgetItem(self.tbl_stock_dashboard_2, 1, 0, "개  인", b_color=QColor(255, 220, 255))
        setTableWidgetItem(self.tbl_stock_dashboard_2, 2, 0, "외국인", b_color=QColor(255, 220, 255))
        setTableWidgetItem(self.tbl_stock_dashboard_2, 3, 0, "기  관", b_color=QColor(255, 220, 255))

        #####
        # 호가창위의 현재가 정보
        setTableHeader(self.tbl_stock_realtime, row=1, col=5, headers=["현재가", "전일대비", "전일비", "거래량", "비율"])
        setDefaultTbl(self.tbl_stock_realtime, DEFAULTSECTIONSIZE)

        # 호가창 & 정보창
        setDefaultTbl(self.tbl_detail_stock_hoga, MINISECTIONSIZE)
        setDefaultTbl(self.tbl_detail_stock, MINISECTIONSIZE)

        # 주식정보 창
        bcolor = QColor(227, 227, 227)
        setTableHeader(self.tbl_detail_stock, row=7, col=6)
        setTableWidgetItem(self.tbl_detail_stock, 0, 0, "액면가", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 1, 0, "자본금", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 2, 0, "주식수", b_color=bcolor)

        setTableWidgetItem(self.tbl_detail_stock, 3, 0, "250최고", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 4, 0, "250최저", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 5, 0, "연중최고", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 6, 0, "연중최저", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 6, 4, "외인율", b_color=bcolor)

        setTableWidgetItem(self.tbl_detail_stock, 0, 2, "시가총액", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 1, 2, "대용가", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 2, 2, "신용비율", b_color=bcolor)

        setTableWidgetItem(self.tbl_detail_stock, 0, 4, "EPS", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 1, 4, "BPS", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 2, 4, "결산월", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 3, 4, "PER", b_color=bcolor)
        setTableWidgetItem(self.tbl_detail_stock, 4, 4, "PBR", b_color=bcolor)

    def init_disp_trade_case(self):
        """
        조건부 검색에 대한 화면 초기화
        :return:
        """
        ###
        # trade case (조건식 검색)
        setTableHeader(self.tbl_trade_case, row=0, col=7)
        setDefaultTbl(self.tbl_trade_case, DEFAULTTRADESECTIONSIZE)

        # 조건검색 실시간 내용, headers=["조건번호(명)", "종목코드", "종목명", "현재가", "등락율", "매수상태", "편입시간", "경과시간"])
        setTableHeader(self.tbl_case_condition, row=0, col=8)
        setDefaultTbl(self.tbl_case_condition, DEFAULTTRADESECTIONSIZE)

        # 컬럼 헤더를 click 시에만 정렬하기.
        hheader = self.tbl_case_condition.horizontalHeader()
        hheader.sectionClicked.connect(self.tbl_case_conditionhorizontal_header_clicked)

        self.tbl_case_condition.setSortingEnabled(False)  # 정렬기능 off

    def disp_tbl_detail_stock(self, code, detail_data):
        """
        주식 정보를 화면에 출력한다.
        :param detail_data: dict 형식으로 이루어 진 정보
        :return:
        """

        # print(detail_data)
        selcted_code = self.get_current_stock()
        if code == selcted_code:
            setTableWidgetItemEx(self.tbl_detail_stock, 0, 0 + 1, INT(detail_data['액면가']), extra_s='원',
                                 f_color=QColor(0, 0, 0))
            setTableWidgetItemEx(self.tbl_detail_stock, 1, 0 + 1, INT(detail_data['자본금']), extra_s='억',
                                 f_color=QColor(0, 0, 0))
            setTableWidgetItemEx(self.tbl_detail_stock, 2, 0 + 1, INT(detail_data['주식수']), extra_s='천',
                                 f_color=QColor(0, 0, 0))

            setTableWidgetItemEx(self.tbl_detail_stock, 3, 0 + 1, INT(detail_data['250최고']))
            setTableWidgetItemEx(self.tbl_detail_stock, 3, 0 + 2, FLOAT(detail_data['250최고가대비율']), extra_s='%')
            setTableWidgetItemEx(self.tbl_detail_stock, 3, 0 + 3, get_disp_date_simple(detail_data['250최고가일']))
            setTableWidgetItemEx(self.tbl_detail_stock, 4, 0 + 1, INT(detail_data['250최저']))
            setTableWidgetItemEx(self.tbl_detail_stock, 4, 0 + 2, FLOAT(detail_data['250최저가대비율']), extra_s='%')
            setTableWidgetItemEx(self.tbl_detail_stock, 4, 0 + 3, get_disp_date_simple(detail_data['250최저가일']))

            setTableWidgetItemEx(self.tbl_detail_stock, 5, 0 + 1, INT(detail_data['연중최고']))
            setTableWidgetItemEx(self.tbl_detail_stock, 6, 0 + 1, INT(detail_data['연중최저']))

            setTableWidgetItemEx(self.tbl_detail_stock, 6, 4 + 1, FLOAT(detail_data['외국인보유']), extra_s='%')

            setTableWidgetItemEx(self.tbl_detail_stock, 0, 2 + 1, INT(detail_data['시가총액']), extra_s='억',
                                 f_color=QColor(0, 0, 0))
            setTableWidgetItemEx(self.tbl_detail_stock, 1, 2 + 1, INT(detail_data['대용가']), f_color=QColor(0, 0, 0))
            setTableWidgetItemEx(self.tbl_detail_stock, 2, 2 + 1, FLOAT(detail_data['신용비율']), extra_s='%')

            setTableWidgetItemEx(self.tbl_detail_stock, 0, 4 + 1, INT(detail_data['EPS']), extra_s='원')
            setTableWidgetItemEx(self.tbl_detail_stock, 1, 4 + 1, INT(detail_data['BPS']), extra_s='원')
            setTableWidgetItemEx(self.tbl_detail_stock, 2, 4 + 1, detail_data['결산월'], extra_s='월')
            setTableWidgetItemEx(self.tbl_detail_stock, 3, 4 + 1, FLOAT(detail_data['PER']), f_color=QColor(0, 0, 0))
            setTableWidgetItemEx(self.tbl_detail_stock, 4, 4 + 1, FLOAT(detail_data['PBR']), f_color=QColor(0, 0, 0))

    def init_disp_values(self):
        """
        보유주식 현황 화면 초기화
        :return:
        """
        # setTableHeader( self.tbl_account_info, headers=self.ats.get_my_values( 'title' ), row=1 )
        # self.setTableHeader( self.tbl_account_info, headers=self.ats.get_my_values( 'title' ), row=1 )

    def disp_trade_info(self, date_str, jongmok_cd, jongmok_name, ordertyp, nqty, nprice, text):
        """
        거래 내역을 로그 또는 화면에 출력한다.
        :param date_str: 거래시간
        :param jongmok_cd: 종목코드
        :param ordertyp: 거래구분
        :param nqty: 수량
        :param text: 내용
        :return:
        """

        color = QColor(0, 0, 0)

        # 라인 추가
        self.tbl_trade_log.insertRow(0)

        # 시간
        setTableWidgetItem(self.tbl_trade_log, 0, 0, date_str, f_color=color)

        if ordertyp == "매도":
            color = QColor(0, 0, 255)
        elif ordertyp == "매수":
            color = QColor(255, 0, 0)
        elif ordertyp == "취소":
            color = QColor(0, 255, 255)
        elif ordertyp == "정정":
            color = QColor(255, 255, 0)

        # 종목코드
        setTableWidgetItem(self.tbl_trade_log, 0, 1, jongmok_cd, f_color=color)

        # 종목명
        setTableWidgetItem(self.tbl_trade_log, 0, 2, jongmok_name, f_color=color, align=Qt.AlignLeft | Qt.AlignVCenter)

        # TEXT = 내용
        setTableWidgetItem(self.tbl_trade_log, 0, 3, text, f_color=color, align=Qt.AlignLeft | Qt.AlignVCenter)

    def do_Sale(self):
        """
        매도 주문 실행
        :return:
        """
        # btn_Sale
        # 실시간 매도/매수 거래를 한다.

        stock_code = str(self.lbl_sell_stock_code.currentText())
        gubun = str(self.cob_sell_gb_list.currentText())
        stock_cnt = INT(self.lbl_sell_stock_cnt.text())
        stock_price = INT(self.lbl_sell_stock_price.text())

        # 시장가 선택 ?
        # if self.ch_sell_realtime.isChecked() == True or gubun = "시장가":
        #    stock_price = 0
        # else:
        if stock_price == 0:
            gubun = "시장가"

        # 수량
        if stock_cnt == "":
            stock_cnt = 1
        else:
            stock_cnt = int(stock_cnt)

        logging.debug(
            "신규매도 => 종목코드: %s, 구분: %s, 수량:%s, 금액 : %s" % (stock_code, gubun, str(stock_cnt), str(stock_price)))

        self.ats.set_order(self.ats.account_num, stock_code, "신규매도", stock_cnt, stock_price, gubun)

    def do_Buy(self):
        """
        매수 주문 실행
        :return:
        """

        stock_code = str(self.lbl_buy_stock_code.currentText())
        gubun = str(self.cob_buy_gb_list.currentText())
        stock_cnt = INT(self.lbl_buy_stock_cnt.text())
        stock_price = INT(self.lbl_buy_stock_price.text())

        # 시장가 선택 ?
        # if self.ch_buy_realtime.isChecked() == True or gubun = "시장가":
        #    stock_price = 0
        # else:
        if stock_price == 0:
            gubun = "시장가"

        logging.debug(
            "신규매수 => 종목코드: %s, 구분: %s, 수량:%s, 금액 : %s" % (stock_code, gubun, str(stock_cnt), str(stock_price)))

        self.ats.set_order(self.ats.account_num, stock_code.strip(), "신규매수", stock_cnt, stock_price, gubun)

    def do_Change(self):
        """
        매도/매수 주문 변경
        :return:
        """
        # # self.ats.set_order( # self.ats.account_num, "063570", "매도정정", 1, 0, "시장가" )

        #  "신규매수": 1,
        #  "신규매도": 2,
        #  "매수취소": 3,
        #  "매도취소": 4,
        #  "매수정정": 5,
        #  "매도정정": 6

    def do_Cancel(self):
        """
        매도/매수 주문 취소
        :return:
        """
        # # self.ats.set_order( # self.ats.account_num, "063570", "매도취소", 1, 0, "시장가", org_orderNo="146792" )

        # 조건식

    def disp_stock_sise(self, stock_sise):
        """
         현재가: 거래량: 시가:, 고가: 저가:
        :param stock_sise:
        :return:
        """

    def init_disp_account_detail(self):
        """
        종목별 투자 수익율에 대한 화면 출력값
        :return:
        """
        # self.setTableHeader( self.tbl_accounts_detail, headers=self.ats.get_my_value_list( 'title' ), row=0 )
        # setDefaultTbl(self.tbl_accounts_detail, DEFAULTTRADESECTIONSIZE);

    def disp_dashboard(self):
        """
        코스피, 코스닥, 개인,외인,기관의 추세를 보여 준다.
        :return:
        """

        _dashboard = self.ats.dashboard

        setTableWidgetItemEx(self.tbl_stock_dashboard, 0, 1, _dashboard['코스피']['현재가'])
        setTableWidgetItemEx(self.tbl_stock_dashboard, 0, 2, _dashboard['코스피']['등락율'], extra_s='%')
        setTableWidgetItemEx(self.tbl_stock_dashboard, 1, 1, _dashboard['코스피200']['현재가'])
        setTableWidgetItemEx(self.tbl_stock_dashboard, 1, 2, _dashboard['코스피200']['등락율'], extra_s='%')
        setTableWidgetItemEx(self.tbl_stock_dashboard, 2, 1, _dashboard['코스닥']['현재가'])
        setTableWidgetItemEx(self.tbl_stock_dashboard, 2, 2, _dashboard['코스닥']['등락율'], extra_s='%')
        setTableWidgetItemEx(self.tbl_stock_dashboard, 3, 1, _dashboard['코스닥100']['현재가'])
        setTableWidgetItemEx(self.tbl_stock_dashboard, 3, 2, _dashboard['코스닥100']['등락율'], extra_s='%')

        ## 개인, 외인, 기관 거래량
        setTableWidgetItemEx(self.tbl_stock_dashboard_2, 1, 1, _dashboard['코스피']['개인순매수'])
        setTableWidgetItemEx(self.tbl_stock_dashboard_2, 2, 1, _dashboard['코스피']['외인순매수'])
        setTableWidgetItemEx(self.tbl_stock_dashboard_2, 3, 1, _dashboard['코스피']['기관순매수'])
        setTableWidgetItemEx(self.tbl_stock_dashboard_2, 1, 2, _dashboard['코스닥']['개인순매수'])
        setTableWidgetItemEx(self.tbl_stock_dashboard_2, 2, 2, _dashboard['코스닥']['외인순매수'])
        setTableWidgetItemEx(self.tbl_stock_dashboard_2, 3, 2, _dashboard['코스닥']['기관순매수'])

    def init_disp_kwansim(self):
        """
        관심종목 정보 화면을 초기화 한다.
        :return:
        """

        title = ["코드", "종목명", "현재가", "전일대비", "등락율", "거래량"]
        setTableHeader(self.tbl_Kwansim, headers=title, row=0)
        setDefaultTbl(self.tbl_Kwansim, DEFAULTTRADESECTIONSIZE)

        # 컬럼 헤더를 click 시에만 정렬하기.
        hheader = self.tbl_Kwansim.horizontalHeader()
        hheader.sectionClicked.connect(self.tbl_Kwansim_horizontal_header_clicked)

        self.tbl_Kwansim.setSortingEnabled(False)  # 정렬기능 off

    def disp_kwansim(self, kwansim_list):
        """
        관심종목 화면체 출력함
        :return:
        """

        kwansims_t = (code for code in kwansim_list if code in self.ats.stocks)
        kwansims = set(kwansims_t)

        row = self.tbl_Kwansim.rowCount()
        for row_i in range(row):
            _row = row - row_i - 1
            cell = self.tbl_Kwansim.item(_row, 0)  # code
            if cell is not None:
                if cell.text() not in kwansims:
                    self.tbl_Kwansim.removeRow(_row)

        row = len(kwansims)
        if row != self.tbl_Kwansim.rowCount():
            self.tbl_Kwansim.setRowCount(row)

        def find_kwansim(tbl, col, code=None):
            for row in range(tbl.rowCount()):
                cell = tbl.item(row, col)  # code
                if cell is not None:
                    if code == cell.text():
                        return row
                elif code is None:
                    return row

            return -1

        row = 0
        # col_max = self.tbl_Kwansim.columnCount()
        for code in kwansims:
            stock = self.ats.stocks[code]

            # 등록된 코드가 있는지 ?
            row = find_kwansim(self.tbl_Kwansim, 0, code)
            if row >= 0:
                # 코드/종목명 ...
                # setTableWidgetItem(self.tbl_Kwansim, row, 0, code)
                # setTableWidgetItem(self.tbl_Kwansim, row, 1, stock['name'], align=Qt.AlignLeft | Qt.AlignVCenter)
                # setTableWidgetItemEx(self.tbl_Kwansim, row, 2, 0, align=Qt.AlignRight | Qt.AlignVCenter)  # 현재가
                # setTableWidgetItemEx(self.tbl_Kwansim, row, 3, 0)  # 전일대비
                # setTableWidgetItemEx(self.tbl_Kwansim, row, 4, 0.0, extra_s=' %')  # 등락율
                # setTableWidgetItemEx(self.tbl_Kwansim, row, 5, 0, f_color=black())  # 거래량
                pass
            else:
                row = find_kwansim(self.tbl_Kwansim, 0)

                # 코드/종목명 ...
                setTableWidgetItem(self.tbl_Kwansim, row, 0, code)
                setTableWidgetItem(self.tbl_Kwansim, row, 1, stock['name'], align=Qt.AlignLeft | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_Kwansim, row, 2, 0, align=Qt.AlignRight | Qt.AlignVCenter)  # 현재가
                setTableWidgetItemEx(self.tbl_Kwansim, row, 3, 0)  # 전일대비
                setTableWidgetItemEx(self.tbl_Kwansim, row, 4, 0.0, extra_s=' %')  # 등락율
                setTableWidgetItemEx(self.tbl_Kwansim, row, 5, 0, f_color=black())  # 거래량

    def update_real_sise_kwansim(self, code, name, data):
        """
        관심종목 화면체 출력함
        :return:
        """
        #######
        col_max = self.tbl_Kwansim.columnCount()
        # 관심 항목에 출력한다.
        for row in range(self.tbl_Kwansim.rowCount()):
            cell = self.tbl_Kwansim.item(row, 0)  # code
            if cell is not None:
                cell_code = cell.text()
                if cell_code == code:
                    setTableWidgetItemEx(self.tbl_Kwansim, row, 2, data['현재가'], align=Qt.AlignRight | Qt.AlignVCenter)
                    if '전일대비' in data:
                        setTableWidgetItemEx(self.tbl_Kwansim, row, 3, data['전일대비'])  # 전일대비
                    setTableWidgetItemEx(self.tbl_Kwansim, row, 4, data['등락율'], extra_s=' %')  # 등락율
                    setTableWidgetItemEx(self.tbl_Kwansim, row, 5, abs(INT(data['누적거래량'])), f_color=black(),
                                         align=Qt.AlignRight | Qt.AlignVCenter)  # 거래량

                    # for v in kwansim_data.values():
                    #    setTableWidgetItemEx(self.tbl_Kwansim, row, col, v,
                    #                         f_color=chk_fcolor(v) if col != 5 else QColor(0, 0, 0),
                    #                         extra_s=extra_str(v),
                    #                         align=get_disp_align(v,
                    #                                              Qt.AlignLeft | Qt.AlignVCenter if col == 1 else None),
                    #                         sort=True)
                    #    col = col + 1
                    #    if col >= (col_max):
                    #        break
                    # 등락율
                    # setTableWidgetItemEx(self.tbl_case_condition, row, 4, data['등락율'], extra_s=' %',
                    #                     align=Qt.AlignRight | Qt.AlignVCenter, sort=True, b_color=b_color)

                    # 누적거래량
                    # setTableWidgetItemEx(self.tbl_case_condition, row, 5, abs(INT(data['누적거래량'])),
                    #                     f_color=QColor(0, 0, 0), align=Qt.AlignRight | Qt.AlignVCenter,
                    #                     sort=True, b_color=b_color)

                    break
        # for loop

    def _disp_table(self, tbl, cnt, list_obj):

        row = 0
        for item_list in list_obj:

            col = 0
            for item in list_obj[item_list]:
                setTableWidgetItemEx(self.tbl, row, col, item)  # , f_color=QColor( 0, 0, 0 ) )
                col = col + 1

            row = row + 1

    # --------------------------- left order and charts --------------------------- #

    def init_detail_stock_hoga(self):
        """
        호가창을 초기화 한다.
        :return:
        """
        self.hoga_row = 23

        setTableHeader(self.tbl_detail_stock_hoga, row=self.hoga_row, col=5)

        # 증감
        setTableWidgetItem(self.tbl_detail_stock_hoga, 0, 0, "증감",
                           b_color=QColor(200, 200, 200))  # , f_color=QColor( 0, 0, 0 ) )

        row = int((self.tbl_detail_stock_hoga.rowCount() - 3) / 2)
        row_idx = 0

        # 현재가
        setTableWidgetItem(self.tbl_detail_stock_hoga, row_idx, 2, "0",
                           b_color=QColor(255, 210, 210))  # , f_color=QColor( 0, 0, 0 ) )

        # 매도 5호가 색상
        v = 210
        row_idx = 1
        for i in range(row):
            setTableWidgetItem(self.tbl_detail_stock_hoga, row_idx, 2, "0", b_color=QColor(v, v, 255))
            v += 5
            row_idx += 1

        # 매수 5호가 색상
        v = 210
        for i in range(row):
            setTableWidgetItem(self.tbl_detail_stock_hoga, row_idx, 2, "0", b_color=QColor(255, v, v))
            v += 5
            row_idx += 1

        setTableWidgetItem(self.tbl_detail_stock_hoga, row_idx, 2, "00:00:00")
        row_idx += 1

        setTableWidgetItem(self.tbl_detail_stock_hoga, row_idx, 2, "시간외")

    def disp_realTick(self, code, jongmok_name, real_tick_list):
        """
        실시간 체결틱 !!
        :param code:
        :param jongmok_name:
        :param real_tick_list:
        :return:
        """

        print("code : %s, name : %s " % (code, jongmok_name))
        for real_tick in real_tick_list:
            print("시간 : %s, 현재가 : %s, 대비율 : %s, 체결강도 : %s, 체결거래량 : %s, 누적거래량 : %s" %
                  (real_tick['시간'], real_tick['현재가'], real_tick['대비율'],
                   real_tick['체결강도'], real_tick['체결거래량'], real_tick['누적거래량']))

    def disp_hoga(self, code, jongmok_name, hoga_list):
        """
        호가 정보를 받아온다.
        :param code:
        :param jongmok_name:
        :param hoga_list:
        :return:
        """
        hoga_idx_list = [x[0] for x in hoga_list]
        row_idx = 0
        f_c = QColor(0, 0, 0)

        for tbl in disp_hoga_table:
            self.disp_hoga_ex(tbl[1], hoga_idx_list, hoga_list, tbl[2], tbl[3], f_color=tbl[4], b_color=tbl[5])

    def disp_real_hoga(self, code, jongmok_name, hoga_list):
        """
        실시간 호가 정보가 올라온다.
        :return:
        """
        hoga_idx_list = [x[0] for x in hoga_list]

        for tbl in disp_hoga_table:
            self.disp_hoga_ex(tbl[0], hoga_idx_list, hoga_list, tbl[2], tbl[3], f_color=tbl[4], b_color=tbl[5])

    def disp_real_hoga_trade(self, code, jongmok_name, hoga_list):
        """
        실시간 주식우선호가 
        :param code:
        :param jongmok_name:
        :param hoga_list:
        :return:
        """        
        hoga_idx_list = [x[0] for x in hoga_list]

        for tbl in disp_hoga_trade_table:
            self.disp_hoga_ex(tbl[0], hoga_idx_list, hoga_list, tbl[1], tbl[2], f_color=tbl[3], b_color=tbl[4])

    # def disp_realover_hoga(self, code, jongmok_name, hoga_list):
    #     """
    #     시간외 호가 출력
    #     :param code:
    #     :param jongmok_name:
    #     :param hoga_list:
    #     :return:
    #     """
    #     selected_code = self.get_current_stock()
    #     if code == selected_code:
    #         row_idx = self.tbl_detail_stock_hoga.rowCount() - 1
    #         hoga_idx_list = [x[0] for x in hoga_list]

    #         self.disp_hoga_ex("호가시간", hoga_idx_list, hoga_list, row_idx, 2, f_color=QColor(0, 0, 0))
    #         self.disp_hoga_ex("시간외매도호가총잔량", hoga_idx_list, hoga_list, row_idx, 1)
    #         self.disp_hoga_ex("시간외매도호가총잔량직전대비", hoga_idx_list, hoga_list, row_idx, 0)
    #         self.disp_hoga_ex("시간외매수호가총잔량", hoga_idx_list, hoga_list, row_idx, 3)
    #         self.disp_hoga_ex("시간외매수호가총잔량직전대비", hoga_idx_list, hoga_list, row_idx, 4)

    # def disp_pre_hoga(self, code, jongmok_name, hoga_list):
    #     """
    #     주식 우선호가
    #     :param code:
    #     :param jongmok_name:
    #     :param hoga_list:
    #     :return:
    #     """

    #     selected_code = self.get_current_stock()
    #     if code == selected_code:
    #         # key_list = RealType.REALTYPE[sRealType]
    #         # self.get_real_comm_data_list(code, key_list)
    #         print("====> %s  : %s(%s) :  %s" %
    #               ("주식우선호가", jongmok_name, code, hoga_list))

    #         hoga_sell_value = INT(hoga_list[0][2])
    #         # self.tbl_detail_stock_hoga

    #         max_row = self.tbl_detail_stock_hoga.rowCount() - 3  # 현재가, 시간, 시간외
    #         row_idx = 1
    #         col = 2

    #         for bi in range(max_row):
    #             row = row_idx + bi
    #             cell = self.tbl_detail_stock_hoga.item(row, col)
    #             if cell is not None:
    #                 cell_value = cell.text()
    #                 cell_value = cell_value.replace(",", "")  # ',' 제거
    #                 cell_value = INT(cell_value)
    #                 if hoga_sell_value == cell_value:
    #                     setTableWidgetItem(self.tbl_detail_stock_hoga, row, col, cell_value,  # f_color=color,
    #                                        b_color=QColor(0, 255, 0))
    #                     break
    #                 # if value ?
    #             # if cell ?
    #         # for ...

    def disp_hoga_ex(self, key, hoga_idx_list, hoga_list, row, col, f_color=None,
                          b_color=QColor(255, 255, 255)):
        """
        호가창에 상세 데이터로 입력한다.
        :param hoga_list:
        :param row:
        :param col:
        :return:
        """
        if len(key) <= 0:
            return
        
        if key in hoga_idx_list:
            v = hoga_list[hoga_idx_list.index(key)][1]

            if key == "호가시간" or key == '호가잔량기준시간':
                v = str(v)
                value = get_disp_value('{}:{}:{}'.format(v[:2], v[2:4], v[4:]))
                color = f_color
            else:
                if isinstance(v, str):
                    if len(v) > 0:
                        if v.find('.') != -1:
                            value = get_disp_value(abs(float(v)))
                            color = get_disp_color(float(v), f_color)
                        else:
                            value = get_disp_value(abs(int(v)))
                            color = get_disp_color(int(v), f_color)
                    else:
                        value = ''
                        color = f_color
                elif isinstance(v, float):
                    value = get_disp_value(abs(v))
                    color = get_disp_color(v, f_color)
                else:
                    value = get_disp_value(int(abs(v)))
                    color = get_disp_color(int(v), f_color)

            setTableWidgetItem(self.tbl_detail_stock_hoga, row, col, value, f_color=color, b_color=b_color)

    def btn_buy_search_click(self):
        code = str(self.lbl_buy_stock_code.currentText())

        # 코드 확인
        if code in self.ats.stocks:
            self.lbl_buy_stock_name.setText(self.ats.stocks[code]['name'])

            # 수량
            self.lbl_buy_stock_cnt.setText("0")

            # 가격
            self.lbl_buy_stock_price.setText("0")

            # 실시간 종목 코드의 호가및 주식정보를 읽어들인다.
            # self.ats.real_current_jongmok( code )

    def btn_sell_search_click(self):
        code = str(self.lbl_sell_stock_code.currentText())

        # 코드 확인
        if code in self.ats.stocks:
            stock = self.ats.stocks[code]
            self.lbl_sell_stock_name.setText(stock['name'])

            # 수량
            self.lbl_sell_stock_cnt.setText("0")

            # 가격
            self.lbl_sell_stock_price.setText("0")

            # 실시간 종목 코드의 호가및 주식정보를 읽어들인다.
            # self.ats.real_current_jongmok(code)

    def select_stock_code(self, code):
        """
        종목코드를 선택했을때. 매수 매도에 추가 여부
        :param code:
        :return:
        """

        self.lbl_sell_stock_code.insertItem(0, code)
        self.lbl_sell_stock_code.setCurrentIndex(0)
        self.lbl_buy_stock_code.insertItem(0, code)
        self.lbl_buy_stock_code.setCurrentIndex(0)

        # 보유종목일때, 매수, 매도에 체크
        if code in self.ats.account_stocks:
            value = self.ats.account_stocks[code]

            # 종목명
            name = self.ats.get_jongmok_real_name(code)
            self.lbl_sell_stock_name.setText(name)
            self.lbl_buy_stock_name.setText(name)

            # 수량
            self.lbl_sell_stock_cnt.setText(str(value['보유수량']))
            self.lbl_buy_stock_cnt.setText("0")  # str(my_value[4]))

            # 가격
            self.lbl_sell_stock_price.setText("0")  # str(my_value[3]))
            self.lbl_buy_stock_price.setText("0")  # str(my_value[3]))

        else:
            # 종목명
            name = self.ats.get_jongmok_real_name(code)
            self.lbl_sell_stock_name.setText(name)
            self.lbl_buy_stock_name.setText(name)

            # 수량
            self.lbl_sell_stock_cnt.setText("0")  # str(my_value[4]))
            self.lbl_buy_stock_cnt.setText("1")  # str(my_value[4]))

            # 가격
            self.lbl_sell_stock_price.setText("0")  # str(my_value[3]))
            self.lbl_buy_stock_price.setText("0")  # str(my_value[3]))

        # 실시간 종목 코드의 호가및 주식정보를 읽어들인다.
        self.get_current_hoga( code )

        # 차트정보를 읽어들인다.
        now = dt.datetime.now()  # sdatetime.strptime()
        date_str = now.strftime('%Y%m%d')

        # tick count ?
        tick = 0
        if self.chart_step_1.isChecked():
            tick = 1
        elif self.chart_step_3.isChecked():
            tick = 3
        elif self.chart_step_5.isChecked():
            tick = 5
        elif self.chart_step_10.isChecked():
            tick = 10
        elif self.chart_step_15.isChecked():
            tick = 15
        elif self.chart_step_20.isChecked():
            tick = 20
        elif self.chart_step_30.isChecked():
            tick = 30
        elif self.chart_step_45.isChecked():
            tick = 45
        elif self.chart_step_60.isChecked():
            tick = 60

        # chart !!!
        if self.rd_chart_tick.isChecked():
            pass
            # self.ats.get_jongmok_tick_chart( code, tick )  # tick 차트
        elif self.rd_chart_min.isChecked():
            pass
            # self.ats.get_jongmok_minute_chart( code, tick )  # 분봉차트
        elif self.rd_chart_day.isChecked():
            pass
            # self.ats.get_jongmok_daily_chart( code )  # 일봉차트
        elif self.rd_chart_week.isChecked():
            pass
            # self.ats.get_jongmok_weekly_chart( code, date_str )  # 주봉차트
        elif self.rd_chart_month.isChecked():
            pass
            # self.ats.get_jongmok_monthly_chart( code, date_str )  # 월봉차트

    def detail_accounts_clicked(self):
        """
        소요 종목 셀을 선택하였을 때
        :return:
        """
        selected = int(self.tbl_accounts_detail.currentRow())
        cell = self.tbl_accounts_detail.item(selected, 2)  # 종목코드
        if cell is not None:
            self.select_stock_code(cell.text())

    def detail_kwansim_clicked(self):
        """
        관심종목의 셀을 선택하였을 때
        :return:
        """
        selected = int(self.tbl_Kwansim.currentRow())
        cell = self.tbl_Kwansim.item(selected, 0)  # 종목코드
        if cell is not None:
            self.select_stock_code(cell.text())

    def tbl_Kwansim_horizontal_header_clicked(self):
        """
        관심종목의 header 을 선택시 sort 하기
        :return:
        """
        """ 컬럼 헤더 click 시에만, 정렬하고, 다시 정렬기능 off 시킴 
        -- 정렬기능 on 시켜놓으면, 값 바뀌면 바로 자동으로 data 순서 정렬되어 바뀌어 헷갈린다.. 
        :param idx --> horizontalheader index; 0, 1, 2,... 
        :return: 
        """
        # print("hedder2.. ", idx)
        self.tbl_Kwansim.setSortingEnabled(True)  # 정렬기능 on #
        time.sleep(0.2)
        self.tbl_Kwansim.setSortingEnabled(False)  # 정렬기능 off

    def detail_condition_clicked(self):
        """
        조건식 리스트에서 종목을 선택했을때...
        :return:
        """
        selected = int(self.tbl_case_condition.currentRow())
        cell = self.tbl_case_condition.item(selected, 1)  # 종목코드
        if cell is not None:
            self.select_stock_code(cell.text())

    def tbl_case_conditionhorizontal_header_clicked(self):
        """
        실시간조건에 대한 sort
        :return:
        """
        # print("hedder2.. ", idx)
        self.tbl_case_condition.setSortingEnabled(True)  # 정렬기능 on #
        time.sleep(0.2)
        self.tbl_case_condition.setSortingEnabled(False)  # 정렬기능 off

    def tbl_unpaid_stocks_clicked(self):
        """
        미수거래를 선택했을 때..
        """
        selected = int(self.tbl_unpaid_stocks.currentRow())
        cell = self.tbl_unpaid_stocks.item(selected, 1)  # 종목코드
        if cell is not None:
            order_no = cell.text()
            print("==> unpaid : " + order_no)

        # unpaid_list = # self.ats.get_unpaid_list()
        # if selected >= 0 and len(unpaid_list) > selected :
        #    print("미수 선택 : %s" % unpaid_stock_list[selected] )
        #    self.tabOrder.setCuttentIndex(2)

    def tbl_detail_stock_hoga_clicked(self):
        """
        호가창을 클릭할때, 매수금액, 매도 금액을 자동으로 넣어준다.
        :return:
        """

        max_row = self.tbl_detail_stock_hoga.rowCount()
        selected = int(self.tbl_detail_stock_hoga.currentRow())

        if selected != 0 and selected != (max_row - 1) and selected != (max_row - 2):
            cell = self.tbl_detail_stock_hoga.item(selected, 2)  # 호가창  금액 선택
            price = cell.text()
            price = price.strip()  # 스페이스 제거
            price = price.replace(",", "")

            # 부호 제거
            if price[0] == '+' or price[0] == '-':
                price = price[1:]

            # 매수,매도 창에서 자동 매수,매도 선택 취소
            self.ch_buy_auto_price.setChecked(False)

            # 금액을 선택한 값으로 입력
            self.lbl_sell_stock_price.setText(price)
            self.lbl_buy_stock_price.setText(price)


    def tabOrderChanged(self, index):
        tabColors = {
            0: '#887aff',  # 'blue',
            1: '#ff8a8a',  # 'red',
            2: '#abf5ce',  # 'green',
        }
        self.tabOrder.setStyleSheet('''
                    QTabBar::tab {{}}
                    QTabBar::tab:selected {{background-color: {color};}}
                    '''.format(color=tabColors[index]))

    # --------------------------- charts --------------------------- #

    def rd_chart_opt_clicked(self, value):  # chart option 클릭
        """
        """

        opt = '일'

        if self.sender() == self.rd_chart_tick or self.sender() == self.rd_chart_min:
            self.chart_step_1.setEnabled(True)
            self.chart_step_3.setEnabled(True)
            self.chart_step_5.setEnabled(True)
            self.chart_step_10.setEnabled(True)
            self.chart_step_15.setEnabled(True)
            self.chart_step_20.setEnabled(True)
            self.chart_step_30.setEnabled(True)
            self.chart_step_45.setEnabled(True)
            self.chart_step_60.setEnabled(True)
        else:
            self.chart_step_1.setEnabled(False)
            self.chart_step_3.setEnabled(False)
            self.chart_step_5.setEnabled(False)
            self.chart_step_10.setEnabled(False)
            self.chart_step_15.setEnabled(False)
            self.chart_step_20.setEnabled(False)
            self.chart_step_30.setEnabled(False)
            self.chart_step_45.setEnabled(False)
            self.chart_step_60.setEnabled(False)

        # 현재 거래창에 선택된 종목코드를 얻어온다.
        # 차트정보를 읽어들인다.

        code = self.get_current_stock()
        if code != "":
            now = dt.datetime.now()  # sdatetime.strptime()
            date_str = now.strftime('%Y%m%d')

            # tick count ?
            tick = 0
            if self.chart_step_1.isChecked():
                tick = 1
            elif self.chart_step_3.isChecked():
                tick = 3
            elif self.chart_step_5.isChecked():
                tick = 5
            elif self.chart_step_10.isChecked():
                tick = 10
            elif self.chart_step_15.isChecked():
                tick = 15
            elif self.chart_step_20.isChecked():
                tick = 20
            elif self.chart_step_30.isChecked():
                tick = 30
            elif self.chart_step_45.isChecked():
                tick = 45
            elif self.chart_step_60.isChecked():
                tick = 60

            # 차트 종류...
            if self.sender() == self.rd_chart_tick:
                # opt = '틱'
                # self.ats.get_jongmok_tick_chart( code, tick )  # tick 차트
                pass
            elif self.sender() == self.rd_chart_min:
                # opt = '분'
                # self.ats.get_jongmok_minute_chart( code, tick )  # 분봉차트
                pass
            elif self.sender() == self.rd_chart_day:
                # opt = '일'
                # self.ats.get_jongmok_daily_chart( code )  # 일봉차트
                pass
            elif self.sender() == self.rd_chart_week:
                # opt = '주'
                # self.ats.get_jongmok_weekly_chart( code, date_str )  # 주봉차트
                pass
            elif self.sender() == self.rd_chart_month:
                # opt = '월'
                # self.ats.get_jongmok_monthly_chart( code, date_str )  # 월봉차트
                pass

        # print("rd_chart_opt_clicked : " + opt + "분봉 차트 -> " + str(value))

    def rd_chart_opt_detail_clicked(self, value):  # chart 초, tick 선택시 ...
        """
        """
        # print("rd_chart_opt_detail_clicked : " + str(value))
        code = self.get_current_stock()
        if code != "":
            # tick count ?
            tick = 0
            if self.chart_step_1.isChecked():
                tick = 1
            elif self.chart_step_3.isChecked():
                tick = 3
            elif self.chart_step_5.isChecked():
                tick = 5
            elif self.chart_step_10.isChecked():
                tick = 10
            elif self.chart_step_15.isChecked():
                tick = 15
            elif self.chart_step_20.isChecked():
                tick = 20
            elif self.chart_step_30.isChecked():
                tick = 30
            elif self.chart_step_45.isChecked():
                tick = 45
            elif self.chart_step_60.isChecked():
                tick = 60

            # 차트가 '틱', '분' 차트 선택 중인지 ?
            if self.rd_chart_tick.isChecked():
                # self.ats.get_jongmok_tick_chart( code, tick )  # tick 차트
                pass
            elif self.rd_chart_min.isChecked():
                # self.ats.get_jongmok_minute_chart( code, tick )  # 분봉차트
                pass

    def makeMovingAverage(self, chartData, maData, interval):

        # '일자' or '체결시간'
        cnt = len(chartData['일자']) if '일자' in chartData else len(chartData['체결시간'])

        # 이평선 데이터를 구한다.
        for i in range(0, cnt):
            if (i < interval):
                maData.append(float('nan'))
                continue

            sum = 0
            for j in range(0, interval):
                sum += int(chartData['현재가'][i - j])
            ma = sum / interval
            maData.append(ma)

    def drawDayChart(self, chartData, tick_cnt):
        """
        """
        # 기존 거 지운다.
        self.fig.clf()

        # 211 - 2(행) * 1(열) 배치 1번째
        self.ax1 = self.fig.add_subplot(2, 1, 1)
        # 212 - 2(행) * 1(열) 배치 2번째
        self.ax2 = self.fig.add_subplot(2, 1, 2)

        """
        ###############################################
        # 봉차트 그리기
        # self.ax1.xaxis.set_major_formatter(ticker.FixedFormatter(schartData[C_TM]))
        # matfin.candlestick2_ohlc(self.ax1, self.chartData[C_OP], self.chartData[C_HP], self.chartData[C_LP], self.chartData[C_CP],
        #                          width=0.8, colorup='r', colordown='b')
        mpl_finance.candlestick2_ohlc( self.ax1,
                                       chartData['시가'],
                                       chartData['고가'],
                                       chartData['저가'],
                                       chartData['현재가'],
                                       width=0.5, colorup='r', colordown='b' )

        ###############################################
        # '일자' or '체결시간'

        if '일자' in chartData:
            # x 축 인덱스 만들기 - 기본 순차 배열 추가
            x_tick_raw = [i for i in range( len( chartData['일자'] ) )]
            # x 축 인덱스 만들기 - 실제 화면에 표시될 텍스트 만들기
            x_tick_labels = []

            startDate = 0
            dateChanged = True
            cnt_idx = 0
            max_cnt = len( chartData['일자'] )
            for i in range( max_cnt ):
                # 날짜 변경 된 경우 날짜 정보 저장
                date = chartData['일자'][max_cnt - i - 1]
                if (date != startDate):
                    yy, mm = divmod( int( date ), 10000 )
                    mm, dd = divmod( mm, 100 )
                    sDate = '%2d/%d ' % (mm, dd)
                    # print(sDate)
                    startDate = date
                    dateChanged = True

                    if cnt_idx % 10 == 0:
                        x_tick_labels.insert( 0, sDate )
                    else:
                        x_tick_labels.insert( 0, '' )

                    cnt_idx += 1
                else:
                    x_tick_labels.insert( 0, '' )

                # 0 분 또는 30분 단위로 시간 표시
                # hhh, mmm = divmod(int(chartData['시간'][i]), 100)
                # stime = '%02d:%02d' % (hhh, mmm)
                # if (mmm == 0 or mmm == 30):
                #    if dateChanged == True:
                #        sDate += stime
                #        x_tick_labels.append(sDate)
                #        dateChanged = False
                #    else:
                #        x_tick_labels.append(stime)
                # else:
                #    x_tick_labels.append('')
        else:  # 틱, 분봉
            x_tick_raw = [i for i in range( len( chartData['체결시간'] ) )]
            # x 축 인덱스 만들기 - 실제 화면에 표시될 텍스트 만들기
            x_tick_labels = []

            startDate = 0
            dateChanged = True
            cnt_idx = 0
            max_cnt = len( chartData['체결시간'] )
            # YYYYMMDDHHMMSS
            for i in range( max_cnt ):
                # 날짜 변경 된 경우 날짜 정보 저장
                d = chartData['체결시간'][max_cnt - i - 1]
                date = d[:8]
                tm = d[-8:]
                if (date != startDate):
                    yy, mm = divmod( int( date ), 10000 )
                    mm, dd = divmod( mm, 100 )
                    sDate = '%2d/%d ' % (mm, dd)
                    print( sDate )
                    startDate = date
                    dateChanged = True

                    # if cnt_idx % 10 == 0:
                    x_tick_labels.insert( 0, sDate )
                    # else:
                    #    x_tick_labels.insert(0, '')

                    # cnt_idx += 1
                else:
                    x_tick_labels.insert( 0, '' )

                # print(chartData['현재가'])

                # 0 분 또는 30분 단위로 시간 표시
                # hhh, mmm = divmod(int(chartData['시간'][i]), 100)
                # stime = '%02d:%02d' % (hhh, mmm)
                # if (mmm == 0 or mmm == 30):
                #    if dateChanged == True:
                #        sDate += stime
                #        x_tick_labels.append(sDate)
                #        dateChanged = False
                #    else:
                #        x_tick_labels.append(stime)
                # else:
                #    x_tick_labels.append('')

        ###############################################
        # 이동 평균 그리기
        self.ax1.plot( x_tick_raw, chartData['5'], label='5', color='red' )
        self.ax1.plot( x_tick_raw, chartData['10'], label='10', color='silver' )
        self.ax1.plot( x_tick_raw, chartData['20'], label='20', color='green' )

        ###############################################
        # 거래량 그리기
        self.ax2.bar( x_tick_raw, chartData['거래량'] )
        ## print(chartData['거래량'])

        ###############################################
        # x 축 가로 인덱스 지정
        self.ax1.set( xticks=x_tick_raw, xticklabels=x_tick_labels )
        self.ax2.set( xticks=x_tick_raw, xticklabels=x_tick_labels )

        # self.ax1.grid()
        # self.ax2.grid()
        plt.tight_layout()
        self.ax1.legend( loc='upper left' )

        self.canvas.draw()
        """

    def draw_jongmok_chart(self, jongmok_cd, jongmok_name, tick_cnt, chartData):
        """
        차트를 그린다.
        :param jongmok_cd: 종목코드
        :param tick_cnt:    '1', '3', '5' ...
        :param chartData: 차트 데이타
        :return:
        """

        self.makeMovingAverage(chartData, chartData['5'], 5)  # 5일선
        self.makeMovingAverage(chartData, chartData['10'], 10)  # 10일선
        self.makeMovingAverage(chartData, chartData['20'], 20)  # 20일선
        self.makeMovingAverage(chartData, chartData['60'], 60)  # 60일선

        # 차트를 그린다.
        self.drawDayChart(chartData, tick_cnt)

    def option_btn_opt_loginWindow_click(self):
        """
        환경설정에서 Login Auto 설정
        :return:
        """

        # self.ats.ShowAccountWindow( self )


    # --------------------------- options --------------------------- #

    def init_unpaid_stock_list(self):
        """
        미수거래 창 초기화
        :return:
        """
        # setTableHeader( self.tbl_unpaid_stocks, headers=# self.ats.get_unpaid_list( 'title' ) )
        # setDefaultTbl( self.tbl_unpaid_stocks, DEFAULTTRADESECTIONSIZE );

    def disp_unpaid_stocks(self, unpaid_list):

        self.tbl_unpaid_stocks.setRowCount(len(unpaid_list))

        row = 0
        for unpaid_stock in unpaid_list:
            # col = 0
            # chbox = caseCheckBox(self.tbl_unpaid_stocks, row, col)
            # chbox.setChecked( True if chk else False )
            # chbox.stateChanged.connect( self.tbl_unpaid_stocks_checkbox_change )  # sender() 확인용 예..

            col = 0
            for item in unpaid_stock.values():
                # if item[0] >= 0:
                setTableWidgetItem(self.tbl_unpaid_stocks, row, col, item)
                col += 1
            # if
            # for loop
            row += 1

    def tbl_unpaid_stocks_checkbox_change(self):
        """

        :return:
        """
        pass

    def tagWidget_tranMode(self):
        """
        메인화면의 현재 상태
        :return: 0 : 거래화면, 1 : 미수결재량, 2 : 자동매매 환경설정
        """
        if self.tabWidget.currentIndex() == 0:
            return TRAN_MODE_TRADE
        elif self.tabWidget.currentIndex() == 1:
            return TRAN_MODE_UNPAID
        elif self.tabWidget.currentIndex() == 2:
            return TRAN_MODE_SETUP
        else:
            return TRAN_MODE_TRADE
        
    def tabWidgetChanged(self, index):
        tabColors = {
            0: '#abf5ce',  # 'green',
            1: '#ff8a8a',  # 'red',
            2: '#abf5ce',  # 'yellow',
            3: '#fabb78',  # 'orange',
            4: '#887aff',  # 'blue',
        }
        self.tabWidget.setStyleSheet('''
                    QTabBar::tab {{}}
                    QTabBar::tab:selected {{background-color: {color};}}
                    '''.format(color=tabColors[index]))

        if index == 0:  # 매매 현황
            #if self.__tabWidget_tabIndex == 2:
            #    self.save_trade_case_click()
            option = 0

        elif index == 1:  # 미수현황 을 실시간으로 화면에 보여준다.
            # if self.__tabWidget_tabIndex == 2:
            #    self.save_trade_case_click()
            self.untraded()

        elif index == 2:  # 조건식 등록, 자동매매 등록
            self.load_trade_case_click()

        # 마지막 tab index
        self.__tabWidget_tabIndex = index

    def untraded(self):
        """
        미거래 현황
        """

    def load_trade_case_click(self):
        """
        조건식을 서버에서 불러 온다.
        :return:
        """
        if not self.opt.ui_only_mode:
            # 설정 파일을 다시 불러 온다.
            self.load_options()

            # ------ 조건검색 리스트를 불러온다. ----
            self.ats.get_realConditionFunctionLoad()  # 설정 상태를 서버로부터 받아온다.
            # btn_load_trade_case.clicked.connect(self.

    def save_trade_case_click(self):
        """
        조건식으로 설정한 데이터를 실시간 매매 방식을 저장한다.
        :return:
        """
        # self.ats.save_case_trade_config()
        self.save_options()

    def tbl_trade_case_cellclicked(self, row, col):
        print("tbl_trade_case_cellclicked... ", row, col)


    def __set_conditions(self, conditions, option_mode = TRAN_MODE_TRADE):
        """
         서버로부터 조건 검색명이 읽어들인다.
         :param conditions:  # {'000': '5일-골든크로스', '001': '5분-급등주', '002': '매도세-급등주', '003': '매도세-급등주-오전장'}
         :return:
        """
        
        # 리스트 라인 결정
        self.tbl_trade_case.setRowCount(len(conditions))

        # 0-선택, 1-조건번호, 2-조건명, 3- 매수최대금액, 4-동작시간, 5-종료시간, 6-매매방식
        row = 0
        for key, name in conditions.items():
            color = QColor(0, 0, 0)
            key_str = str(key)

            # 선택
            col = 0
            chbox = caseCheckBox(self.tbl_trade_case, row, col)
            chbox.setChecked(False)  # if condition_name[0] is True else False)
            chbox.stateChanged.connect(self.tbl_trade_case_checkbox_change)  # sender() 확인용 예..

            # 조건번호
            setTableWidgetItem(self.tbl_trade_case, row, col+1, key_str)

            # 조건명
            setTableWidgetItem(self.tbl_trade_case, row, col+2, name, align=Qt.AlignLeft | Qt.AlignVCenter)
            self.tbl_trade_case.setColumnWidth(2, 120)

            # 최대 매수대금
            if option_mode == TRAN_MODE_SETUP:
                condition = self.__tmp_options[OPTIONS_CONDITIONS] if OPTIONS_CONDITIONS in self.__tmp_options else {}
                
                # 사용 여부
                bk = False
                if key_str in condition and OPTIONS_CONDITIONS_CHECK in condition[key_str]:
                    bk = bool(condition[key_str][OPTIONS_CONDITIONS_CHECK])
                chbox.setChecked(bk) 

                # 최대 매수 금액
                v = 1000000
                if key_str in condition and OPTIONS_CONDITIONS_AMOUNT in condition[key_str]:
                    v = int(condition[key_str][OPTIONS_CONDITIONS_AMOUNT])
                setTableWidgetItem( self.tbl_trade_case, row, col+3, v, f_color=color )

                # 동작시간
                s = '09:00:00'
                if key_str in condition and OPTIONS_CONDITIONS_START in condition[key_str]:
                    s = str(condition[key_str][OPTIONS_CONDITIONS_START])
                setTableWidgetItem( self.tbl_trade_case, row, col+4, s, f_color=color )

                # 종료시간
                s = '15:20:00'
                if key_str in condition and OPTIONS_CONDITIONS_END in condition[key_str]:
                    s = str(condition[key_str][OPTIONS_CONDITIONS_END])
                setTableWidgetItem( self.tbl_trade_case, row, col+5, s, f_color=color )
                # self.tbl_trade_case.setColumnWidth( col, 70 )

                # 매매방법
                method = self._trade_func_method['default']
                setTableWidgetItem( self.tbl_trade_case, row, 6, method, f_color=color )
                # self.tbl_trade_case.setColumnWidth( col, 120 )

            row += 1

    def __get_conditions(self):
        """
        설정화면에 있는 조건검색의 정보를 dict 형태로 변형한다.
        """
        conditions = {}

        # 조건검색 tab리스트의 정보를 읽어 들인다.
        max_row = self.tbl_trade_case.rowCount()
        for row in range(max_row):
            check = getTableWidgetItem(self.tbl_trade_case, row, 0).isChecked()
            key = self.tbl_trade_case.item(row, 1).text()
            name = self.tbl_trade_case.item(row, 2).text()
            amount = self.tbl_trade_case.item(row, 3).text()
            start = self.tbl_trade_case.item(row, 4).text()
            end = self.tbl_trade_case.item(row, 5).text()
            method = self._trade_func_method['default'] # 'MACD'self.tbl_trade_case.item(row, 6).text()

            conditions[key] = {
                OPTIONS_CONDITIONS_KEY : key,
                OPTIONS_CONDITIONS_CHECK : check,
                OPTIONS_CONDITIONS_NAME : name,
                OPTIONS_CONDITIONS_AMOUNT : int(amount),
                OPTIONS_CONDITIONS_START : start,
                OPTIONS_CONDITIONS_END : end,
                OPTIONS_CONDITIONS_METHOD : 'method',
            }

        return conditions
    
    def __set_options(self, options):
        """
        options dict 을 설정화면에 있는 데이터로 변환 한다.
        :return:
        """
        pass        
    
    # def __get_options(self):
    #     """
    #     설정화면에 있는 데이터를 options dict 으로 변환 한다.
    #     :return:
    #     """        
    #     options = {}

    #     options[OPTIONS_CONDITIONS] = self.__get_conditions()

    #     return options

    def save_options(self):
        """
        설정값을 저장한다.
        :return:
        """
        options = {}

        # 조건검색 설정값을 읽어 들인다.
        options[OPTIONS_CONDITIONS] = self.__get_conditions()

        if len(options) > 0:
            config = self.load_config()

            if 'buy' not in config:
                config['buy'] = {}

            config['buy']['max-stocks'] = int(self.lbl_max_stocks.text())
            config['buy']['use max-stocks'] = self.chk_use_max_stocks.isChecked()

            #  options 기능설정 변경
            pre_opitons = config[OPTIONS] if OPTIONS in config else {} 
            config[OPTIONS] = options

            # 설정값 저장
            self.save_config(config)

            # 조건 검색을 실행한다.
            self.set_realtime_conditions(options[OPTIONS_CONDITIONS], pre_opitons[OPTIONS_CONDITIONS])

    def set_realtime_conditions(self, conditions, pre_conditions = None):
        """
        조건 검색을 재 설정 한다.
        """

        # 기존의 것이 있으면
        if pre_conditions is not None:
            # pre_condition_list = [int(key), item[OPTIONS_CONDITIONS_NAME] for key, item in pre_conditions.items()]
            # for pre_condition in pre_condition_list:
            #    self.ats.set_realStopCondition(pre_condition[0], pre_condition[1])       # name, key
            # 조건 검색을 설정 한다.
            for key, item in pre_conditions.items():
                if item[OPTIONS_CONDITIONS_CHECK]:
                    self.ats.set_realStopCondition(item[OPTIONS_CONDITIONS_NAME], int(item[OPTIONS_CONDITIONS_KEY]))
                    time.sleep(0.1)

        # QTableWidget의 리스트를 모두 삭제 한다.
        self.tbl_case_condition.clearContents()

        # 조건 검색을 설정 한다.
        for key, item in conditions.items():
            if item[OPTIONS_CONDITIONS_CHECK]:
                self.ats.set_realCondition(item[OPTIONS_CONDITIONS_NAME], int(item[OPTIONS_CONDITIONS_KEY]))
                time.sleep(0.1)

    def load_options(self):
        """
        설정값을 읽어 들인다.
        :return:
        """        

        # 설정파일을 불러 온다.    
        config = self.load_config()

        # 설정값에서 'options' 을 읽어 들인다.
        self.__tmp_options = config[OPTIONS] if OPTIONS in config else  {}

        trading_func_list = self._trade_func_method['methods']
        row = len(trading_func_list)

        setTableHeader(self.tbl_auto_trade, row=row, col=5, headers=["기본매매", "번호", "자동매매명", "시작시간", "종료시간"])
        setDefaultTbl(self.tbl_auto_trade, DEFAULTSECTIONSIZE);

        default = self._trade_func_method['default']
        self.btngroup = QButtonGroup()

        row = 0
        for key, trading_func in trading_func_list.items():
            col = 0
            chbox = QRadioButton(self.tbl_auto_trade)  # self)
            chbox.setChecked(True if default == key else False)
            self.btngroup.addButton(chbox, row)

            # align
            cell_widget = QWidget()
            lay_out = QHBoxLayout(cell_widget)
            lay_out.addWidget(chbox)
            lay_out.setAlignment(Qt.AlignCenter)
            lay_out.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(lay_out)
            self.tbl_auto_trade.setCellWidget(row, col, cell_widget)

            setTableWidgetItem(self.tbl_auto_trade, row, 1, key)  # 번호
            setTableWidgetItem(self.tbl_auto_trade, row, 2, trading_func['name'],
                               align=Qt.AlignLeft | Qt.AlignVCenter)  # 이름
            setTableWidgetItem(self.tbl_auto_trade, row, 3, trading_func['start'])  # 시작시간
            setTableWidgetItem(self.tbl_auto_trade, row, 4, trading_func['end'])  # 종료시간

            row += 1
        # for...
        self.btngroup.buttonClicked.connect(self.tbl_auto_trade_radio_clicked)

        # ----- 목표금액
        self.lbl_target_amount.setText(str(config['general']['기본정보']['목표']))
        self.lbl_invest_amount.setText(str(config['general']['기본정보']['투자금']))

        # ------ 매수 조건
        self.lbl_max_stocks.setText(str(config['buy']['max-stocks']))
        self.chk_use_max_stocks.setChecked(
            config['buy']['use max-stocks'] if 'use max-stocks' in config['buy'] else False)

        buy_amount = config['buy']['use max-stocks']

        # cob_max_amount

    def tbl_auto_trade_radio_clicked(self, obj):
        """
        :return:
        """
        row = self.btngroup.id(obj)
        cell = self.tbl_auto_trade.item(row, 1)
        if cell is not None:
            key = cell.text()
            self._trade_func_method['default'] = key
            print("Key was pressed, id is: {} - {}".format(key, self._trade_func_method['methods'][key]))

    def tbl_auto_trade_clicked(self):
        """
        매매방법에 대한 선택
        """
        selected = int(self.tbl_auto_trade.currentRow())
        cell = self.tbl_auto_trade.item(selected, 1)  # 종목코드
        if cell is not None:
            key = cell.text()
            if key in self._trade_func_method['methods']:
                trade_func = self._trade_func_method['methods'][key]
                print("name : {}, start: {}, end: {}, option: {}".format(trade_func['name'], trade_func['start'],
                                                                         trade_func['end'], trade_func['option']))
    # 사용할 계정 정보
    def set_account_info(self, text):
        self.lblAccounNo.setText(text)

    def set_user_id(self, id):
        self.lblAccount.setText(id)

    def set_investment_mode(self, mode):
        if mode == SIM_INVESTMENT:
            self.lbl_invest_mode.setText("모의 투자 모드")
            self.lbl_invest_mode.setStyleSheet("QPlainTextEdit {background-color: #rrggbb;}")
        else:
            self.lbl_invest_mode.setText("실전 투자 모드")

    def disp_account_detail(self, account_no: str, account_detail: dict, code=None) -> None:
        """ 계좌에 등록된 모든 종목을 화면에 출력한다. """
        # 나의 계정정보를 재 설정한다.
        for code in account_detail:
            if code in self.my_stocks:
                # 임시저장 정보에 없는 데이터 복구
                my_stock = self.my_stocks[code]

                if '매매방식' not in my_stock:
                    my_stock['매매방식'] = self._trade_func_method['default']
                if '자동매매' not in my_stock:
                    my_stock['자동매매'] = True

                for data in my_stock:
                    if data not in account_detail[code]:
                        account_detail[code][data] = my_stock[data]
            else:
                if '자동매매' not in account_detail[code]:
                    account_detail[code]['자동매매'] = True

                # 보유주식정보 저장
                self.my_stocks[code] = account_detail[code].copy()
        # ------------------------------------------------------------------------ #
        self.tbl_accounts_detail.setRowCount(len(account_detail))
        for row, code in enumerate(account_detail):
            stock = account_detail[code]

            # 매수/매도 선택
            col = 0
            chbox = caseCheckBox(self.tbl_accounts_detail, row, col)
            chbox.setChecked(False)
            chbox.stateChanged.connect(self.tbl_account_select_chk_change)  # sender() 확인용 예..

            # 신용구분
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 1, credit_gubun(stock['신용구분']), sort=True)
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 2, code, sort=True)
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 3, stock['종목명'], sort=True,
                                 align=Qt.AlignLeft | Qt.AlignVCenter,
                                 b_color=white() if stock['수익률'] > _mid_risk else red())
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 4, INT(stock['현재가']),
                                 align=Qt.AlignRight | Qt.AlignVCenter)
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 5, INT(stock['보유수량']), f_color=black())
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 6, INT(stock['매입가']), f_color=black(),
                                 align=Qt.AlignRight | Qt.AlignVCenter)
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 7, INT(stock['평가금액']),
                                 f_color=red() if stock['손실차액'] > 0 else blue(),
                                 align=Qt.AlignRight | Qt.AlignVCenter)
            s = "{} %".format(get_disp_value(FLOAT(stock['수익률'])))
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 8, s,
                                 f_color=red() if stock['손실차액'] > 0 else blue(), align=Qt.AlignRight | Qt.AlignVCenter)
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 9, INT(stock['손실차액']),
                                 align=Qt.AlignRight | Qt.AlignVCenter)
            # setTableWidgetItemEx(self.tbl_accounts_detail, row, 10, stock['매매정보']['매입시간'][:10] +' ' + stock['매매정보']['매입시간'][-8:])
            setTableWidgetItemEx(self.tbl_accounts_detail, row, 10, stock['매매정보']['매입시간'][-14:])

            # 마지막 매매거래 방법을 선택한다.
            col = 11

            mycom = QComboBox()
            mycom.setProperty("row", row)
            mycom.setProperty("col", col)
            for key, trading_func in self._trade_func_method['methods'].items():  # trading_func_list.keys():
                mycom.addItem(trading_func['name'], key)
            # for loop
            mycom.setCurrentIndex(0)
            self.tbl_accounts_detail.setCellWidget(row, col, mycom)

            trade_idx = stock['매매방식']
            count = mycom.count()
            for idx in range(count):
                key = mycom.itemData(idx)
                if key == trade_idx:
                    mycom.setCurrentIndex(idx)
                    break
                # if ...
            # for loop
            mycom.currentIndexChanged.connect(self.tbl_accounts_detail_trade_method_changed)

            # 자동매매 ?
            col += 1

            chbox = caseCheckBox(self.tbl_accounts_detail, row, col)
            chbox.setChecked(stock['자동매매'])
            chbox.stateChanged.connect(self.tbl_account_auto_tradde_chk_change)  # sender() 확인용 예..

    def tbl_account_select_chk_change(self, check_value):
        """
        주식 선택하여, 개별/일괄 매도
        """
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        cell = self.tbl_accounts_detail.item(chbox.get_row(), 2)  # 종목코드

        # 리스트에 데이터가 있는지 확인 한다.
        if cell is not None:
            code = cell.text().strip()
            print('==> {} - {}'.format(code, check_value))
            if code in self.ats.account_stocks:
                stock = self.ats.account_stocks[code]

    def tbl_accounts_detail_trade_method_changed(self, text):
        """
        매매 방식을 변경하였을 때...
        :return:
        """
        mycom = self.sender()
        row = int(mycom.property("row"))
        # col = int(mycom.property("col"))

        cell = self.tbl_accounts_detail.item(row, 1)  # code
        if cell is not None:
            code = cell.text().strip()  # 주식코드

            #    trading_func_list = self.ats.get_trade_func_list()
            key = mycom.itemData(mycom.currentIndex())
            print("==> {} - {}".format(code, key))
            if code in self.ats.account_stocks:
                stock = self.ats.account_stocks[code]
                stock['매매방식'] = key

                # 상태 저장
                self.save_my_stocks()
        #    if key in trading_func_list:
        # else:

    def tbl_account_auto_tradde_chk_change(self, check_value):
        """
        자동매매를 선택하였을 때....
        :param check_value:
        :return:
        """
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        cell = self.tbl_accounts_detail.item(chbox.get_row(), 2)  # 종목코드

        # 리스트에 데이터가 있는지 확인 한다.
        if cell is not None:
            code = cell.text().strip()
            print('==> {} - {}'.format(code, check_value))
            if code in self.ats.account_stocks:
                stock = self.ats.account_stocks[code]
                stock['자동매매'] = bool(check_value)

                # 상태 저장
                self.save_my_stocks()

    def count_my_stocks(self):
        return len([cd for cd, stock in self.ats.account_stocks.items() if stock['보유수량'] > 0])

    # 실시간 주식 시세/체결정보
    def disp_realtime_sise(self, code, name, data):
        """
        실시간 시세 화면에 출력
        """
        max_row = self.tbl_accounts_detail.rowCount()
        for row in range(max_row):
            cell = self.tbl_accounts_detail.item(row, 2)  # code
            if cell is not None and code == cell.text():
                # col = account_detail.loc[idx]
                if code in self.ats.account_stocks:
                    stock = self.ats.account_stocks[code]

                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 3, stock['종목명'], sort=True,
                                         align=Qt.AlignLeft | Qt.AlignVCenter,
                                         b_color=white() if stock['수익률'] > _mid_risk else red())
                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 4, INT(data['현재가']),
                                         align=Qt.AlignRight | Qt.AlignVCenter)
                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 5, INT(stock['보유수량']), f_color=black())
                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 6, INT(stock['매입가']), f_color=black(),
                                         align=Qt.AlignRight | Qt.AlignVCenter)
                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 7, INT(stock['평가금액']),
                                         f_color=red() if stock['손실차액'] > 0 else blue(),
                                         align=Qt.AlignRight | Qt.AlignVCenter)
                    s = "{} %".format(get_disp_value(FLOAT(stock['수익률'])))
                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 8, s,
                                         f_color=red() if stock['손실차액'] > 0 else blue(),
                                         align=Qt.AlignRight | Qt.AlignVCenter)
                    setTableWidgetItemEx(self.tbl_accounts_detail, row, 9, INT(stock['손실차액']),
                                         align=Qt.AlignRight | Qt.AlignVCenter)

                break
            # if code ?
        # for loop !!

        # 관심종목에 시세정보를 출력한다.
        self.update_real_sise_kwansim(code, name, data)

        # 실시간으로 받은 시세정보를 화면에 출력한다.
        self.update_real_sise_tbl_case_condition(code, name, data)

        # 주문창!!!
        # 주문창에서 현재가 화면에 현재값 출력 ?
        # 실시간으로 받은 시세정보를 화면에 출력한다.

        selected_code = self.get_current_stock()
        if code == selected_code:
            v = INT(data['현재가'])
            f_color = get_disp_color(v)
            # 현재가
            setTableWidgetItemEx(self.tbl_stock_realtime, 0, 0, abs(v), f_color=f_color)

            # 전일대비
            setTableWidgetItemEx(self.tbl_stock_realtime, 0, 2, INT(data['전일대비']))

            # 등락율
            setTableWidgetItemEx(self.tbl_stock_realtime, 0, 3, data['등락율'],
                                 extra_s=' %')
            # 누적거래량
            setTableWidgetItemEx(self.tbl_stock_realtime, 0, 4, INT(data['누적거래량']),
                                 f_color=QColor(0, 0, 0), align=Qt.AlignRight | Qt.AlignVCenter)

            #  ###### 호가창의 현재가 ###########
            # 현재가
            # setTableWidgetItemEx(self.tbl_detail_stock_hoga, 0, 2, abs(v), f_color=f_col
            #                      b_color=QColor(255, 210, 210))

            # # 거래량
            # setTableWidgetItemEx(self.tbl_detail_stock_hoga, 0, 3, INT(data['누적거래량']), f_color=QColor(0, 0, 0),
            #                      b_color=QColor(255, 255, 255), align=Qt.AlignRight | Qt.AlignVCenter)

            # 주문창 (buy, sell) - 현재가 자동 적용 선택시 자동으로 현재가 적용
            # 주문창에 매수/매도/수정/취소 의 현재가를 자동으로 선택되어 있는지 ?
            price = abs(v)

            idx = self.get_current_taborder()
            if idx == TAB_MODE_BUY:
                if self.ch_buy_auto_price.isChecked():
                    self.lbl_buy_stock_price.setText(str(price))
            elif idx == TAB_MODE_SELL:
                if self.ch_sell_auto_price.isChecked():
                    self.lbl_sell_stock_price.setText(str(price))

                # 잔고를 자동으로 설정
                if self.ch_sell_auto_jango.isChecked():
                    if code in self.ats.account_stocks:
                        qnt = self.ats.account_stocks[code]['보유수량']
                        self.lbl_sell_stock_cnt.setText(str(qnt))

            elif idx == TAB_MODE_UPDATE:
                if self.ch_update_auto_price.isChecked():
                    self.lbl_update_stock_price.setText(str(price))

    # 실시간으로 받은 시세정보를 화면에 출력한다.
    def update_real_sise_tbl_case_condition(self, code, name, data):
        """
        실시간으로 받은 시세정보를 화면에 출력한다.
        :return:
        """

        # 조건검색창의 실시간 데이터를 업데이트 한다.
        for row in range(self.tbl_case_condition.rowCount()):
            cell = self.tbl_case_condition.item(row, 1)
            if cell is not None:
                cell_code = cell.text()
                if cell_code == code:
                    b_color = QColor(235, 255, 235)
                    if code in self.ats.account_stocks and self.ats.account_stocks[code]['보유수량'] > 0:
                        b_color = white()

                    # 현재가
                    setTableWidgetItemEx(self.tbl_case_condition, row, 3, INT(data['현재가']),
                                         align=Qt.AlignRight | Qt.AlignVCenter, sort=True, b_color=b_color)

                    # 전일대비

                    # 등락율
                    setTableWidgetItemEx(self.tbl_case_condition, row, 4, data['등락율'], extra_s=' %',
                                         align=Qt.AlignRight | Qt.AlignVCenter, sort=True, b_color=b_color)

                    # 누적거래량
                    setTableWidgetItemEx(self.tbl_case_condition, row, 5, abs(INT(data['누적거래량'])),
                                         f_color=QColor(0, 0, 0), align=Qt.AlignRight | Qt.AlignVCenter,
                                         sort=True, b_color=b_color)

                    break

    def disp_calculate_values(self):
        # ---- 화면 출력 ---- #
        setTableWidgetItemEx(self.tbl_account_info, 0, 0, self.my_asset['목표금액'], f_color=red())
        setTableWidgetItemEx(self.tbl_account_info, 0, 1, self.my_asset['투자금액'], f_color=black())
        setTableWidgetItemEx(self.tbl_account_info, 0, 2, get_disp_percent(self.my_asset['목표달성율']),
                             f_color=red() if self.my_asset['목표달성율'] >= 100.0 else blue())
        setTableWidgetItemEx(self.tbl_account_info, 0, 3, self.my_asset['추정자산'], f_color=black())
        setTableWidgetItemEx(self.tbl_account_info, 0, 4, get_disp_percent(self.my_asset['투자이익률']),
                             f_color=red() if self.my_asset['투자이익률'] >= 100.0 else blue())
        setTableWidgetItemEx(self.tbl_account_info, 0, 5, self.my_asset['매입금액'], f_color=black())
        setTableWidgetItemEx(self.tbl_account_info, 0, 6, self.my_asset['평가금액'],
                             f_color=red() if self.my_asset['총손익'] >= 0 else blue())
        setTableWidgetItemEx(self.tbl_account_info, 0, 7, self.my_asset['총손익'])
        setTableWidgetItemEx(self.tbl_account_info, 0, 8, get_disp_percent(self.my_asset['총수익률']),
                             f_color=red() if self.my_asset['총손익'] >= 0 else blue())
        setTableWidgetItemEx(self.tbl_account_info, 0, 9, self.my_asset['당일실현손익'])
        setTableWidgetItemEx(self.tbl_account_info, 0, 10, self.my_asset['예수금+2'],
                             f_color=black() if self.my_asset['예수금+2'] >= 0 else blue())

    # '주식호가잔량'
    def on_realtime_hoga_jan(self, real_type: str, code: str, name: str, data: dict):
        """
        주식의 실시간 호가 잔량를 구한다.
        """ 
        
        selected_code = self.get_current_stock()
        if code == selected_code:
            hoga_list = [[key, item] for key, item in data.items()]
            self.disp_real_hoga(code, name, hoga_list)

    # 주식우선호가
    def on_realtime_hoga_trade(self, real_type: str, code: str, name: str, data: dict):
        """
        실시간 호가 데이터
        """
        super().on_realtime_hoga_trade(real_type, code, name, data)
        
        # 화면 출력
        selected_code = self.get_current_stock()
        if code == selected_code:
            hoga_list = [[key, item] for key, item in data.items()]
            self.disp_real_hoga_trade(code, name, hoga_list)

    # '주식호가잔량'
    def on_hoga_jan(self, code: str, name: str, data: dict):
        """
        주식의 호가 잔량를 구한다.
        data : dict 이면 'name' : 'values'
        """   
        # '호가잔량기준시간'
        selected_code = self.get_current_stock()
        if code == selected_code:
            hoga_list = [[key, item] for key, item in data.items()]
            self.disp_hoga(code, name, hoga_list)

        return True

    # '업종현재가'
    def on_realtime_jisu(self, code, name, data: dict):
        #keys = {'001': '코스피', '101': '코스닥', '201': '코스피200', '138': '코스닥100'}
        #if code in keys:
        #    key = keys[code]
            # data = self.disp_dashboard[key].copy()
            # data['현재가'] = FLOAT(key_list[1][2])  # 현재가
            # data['등락율'] = FLOAT(key_list[3][2])  # 등락율

            # data['개인순매수']  = INT(self.get_comm_data(sTrCode, sName, i, "개인순매수"))      # 개인순매수
            # data['외인순매수']  = INT(self.get_comm_data(sTrCode, sName, i, "외국인순매수"))    # 외국인순매수
            # data['기관순매수']  = INT(self.get_comm_data(sTrCode, sName, i, "기관계순매수"))        # 기관계순매수
            # data['대비부호' ]  = self.get_comm_data(sTrCode, sName, i, "대비부호")              # 대비부호

            # rate = 2  # <-- 버그라서 강제로 조정
            # data['현재가'] = float(float(data['현재가']) / (10 ** rate))
            # data['등락율'] = float(float(data['등락율']) / (10 ** rate))
        #    logging.debug("===> 업종지수 (%s) :%s,  %s" % (code, key, str(data)))
            # self.disp_dashboard[key] = data.copy()
            # self._app_ui.disp_dashboard()        #       
        
        # print('==> kiwoom_api.py : {} - {} '.format(real_type, data))
        
        return True
    
    # '업종등락'
    def on_realtime_jisu_updown(self, code, name, data: dict):
        #  ==> kiwoom_api.py : code: 201, 업종등락 - {'체결시간': '144040', '현재가': '-339.57', 
        # '전일대비': '-3.01', '등락율': '-0.88', '누적거래량': '102050', '누적거래대금': '5493743', 
        # '상승종목수': '0', '상한종목수': '48', '하락종목수': '8', '하한종목수': '0', 
        # '거래형성종목수': '200', '거래형성비율': '100.00'}
        return True

    # 조건검색 리스트 dict 구조로
    def on_conditions_list(self, conditions: dict):
        """
         서버로부터 조건 검색명이 읽어들인다.
         :param conditions:  # {'000': '5일-골든크로스', '001': '5분-급등주', '002': '매도세-급등주', '003': '매도세-급등주-오전장'}
         :return:
        """
        
        # 리스트 라인 결정
        self.__set_conditions(conditions, self.tagWidget_tranMode())

    def tbl_trade_case_checkbox_change(self, check_value):
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        cell = self.tbl_trade_case.item(chbox.get_row(), 1)  # idx

        # 리스트에 데이터가 있는지 확인 한다.
        if cell is not None:
            key = cell.text()
            # print("key : {}".format(key))

    # 조건검색에서 받은 데이터, 'L': 검색, 'I' : 실시간 추가발생, 'D' : 실시간 조건검색 제거
    def on_conditions_stocks(self, gubun, code, name, condition_name, condition_index, sno=None):
        """
        조건 검색에서 받은 이벤트
        """
        # 전처리
        super().on_conditions_stocks(gubun, code, name, condition_name, condition_index, sno)

        def find_case_condition(tbl, code):
            row_cnt = tbl.rowCount()
            idx = -1
            for row in range(row_cnt):
                cell = tbl.item(row, 1)
                if cell is not None:
                    if cell.text() == code:
                        idx = row
                        break
            return idx

        # 조건검색 리스트)
        if gubun == "L" or gubun == "I":
            if find_case_condition(self.tbl_case_condition, code) < 0:
                condition_stock = self.condition_stock_list[code]

                self.tbl_case_condition.insertRow(0)
                row = 0

                b_color = white() if condition_stock['매수'] == '매수' else QColor(235, 255, 235)

                # 조건번호
                setTableWidgetItem(self.tbl_case_condition, row, 0, str(condition_index), sort=True, b_color=b_color)

                # 종목코드
                setTableWidgetItem(self.tbl_case_condition, row, 1, code, sort=True, b_color=b_color)

                # 종목명
                setTableWidgetItem(self.tbl_case_condition, row, 2, name, align=Qt.AlignLeft | Qt.AlignVCenter,
                                   sort=True, b_color=b_color)

                # 현재가(3), 등락율(4), 거래량(5)
                # 현재가
                setTableWidgetItemEx(self.tbl_case_condition, row, 3, INT(condition_stock['현재가']),
                                     align=Qt.AlignRight | Qt.AlignVCenter, sort=True, b_color=b_color)

                # 전일대비

                # 등락율
                setTableWidgetItemEx(self.tbl_case_condition, row, 4, INT(condition_stock['대비율']), extra_s=' %',
                                     align=Qt.AlignRight | Qt.AlignVCenter, sort=True, b_color=b_color)

                # 누적거래량
                setTableWidgetItemEx(self.tbl_case_condition, row, 5, INT(condition_stock['거래량']),
                                     f_color=QColor(0, 0, 0), align=Qt.AlignRight | Qt.AlignVCenter,
                                     sort=True, b_color=b_color)

                # 매수/미매수
                setTableWidgetItem(self.tbl_case_condition, row, 6, condition_stock['매수'], sort=True, b_color=b_color)

                # 편입시간
                setTableWidgetItem(self.tbl_case_condition, row, 7, condition_stock['편입시간'], sort=True, b_color=b_color)

        # 조건 검색 종목에서 삭제 되었습니다.
        elif gubun == "D":
            row = find_case_condition(self.tbl_case_condition, code)
            if row >= 0:
                self.tbl_case_condition.removeRow(row)

    
if __name__ == '__main__':
    # while True:
    app = QApplication(sys.argv)  # 메인 윈도우를 실행한다.
    app.setStyle('Fusion')

    # argc, argv
    opt = opt_struct()
    opt.ui_only_mode = True

    if len(sys.argv) >= 1:
        argv = sys.argv[1:]
        for arg in argv:
            # if arg.lower() == '-a':
            #    opt.auto_running = True
            if arg.lower() == '-m':
                opt.trade_min = True
            # if arg.lower() == '-d':
            # opt.develop_mode = True

    win = WindowClass(opt)  # WindowClass의 인스턴스 생성
    win.show()
    sys.exit(app.exec_())  # EventsL
