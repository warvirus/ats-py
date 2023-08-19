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

"""
    이 프로그램은 키움증권 API 를 이용하여 응용 프로그램을 개발하기 위한 기초 코드를 모아둔 파일이다.
"""
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import * # QApplication, QFileDialog, qApp, QAction, QMainWindow, QStatusBar, QVBoxLayout, QSplitter, QMessageBox, QInputDialog, QLineEdit
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import pandas
from pandas.core.frame import DataFrame
import socket

from ats_const import *
from utils import load_config_file, save_config_file, get_macd

# Application Name
APP_NAME = os.path.splitext(os.path.basename( sys.argv[0]))[0]

def now_string():
    return dt.datetime.now().strftime("%H%M")

class Stock:
    def __init__(self, code):
        self._code = code
        self._name = ''

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

class tradeStock():
    def __init__(self, kiwoom_api : kiwoom_api):
        """
        trade_stocks 의 구조체를 정의한 것
            [code] = {
                'real-time': code,
                'stock' : kiwoom_api.stocks[code]
            }
        """
        self.__kiwoom_api = kiwoom_api
        self.__trade_stocks = {}
    
    # def __getitem__(self, code):
    #    return self.__trade_stocks[code]

    @property
    def stocks(self):
        return self.__trade_stocks
    @property
    def stock(self, code):
        return self.__trade_stocks[code] if code in self.__trade_stocks else None
    
    def is_exist(self, code):
        return True if code in self.__trade_stocks else False
    
    # @property
    # def __getitem__(self, code):
    #     return self.__trade_stocks[code]
    def clearAll(self):
        self.__trade_stocks.clear()

    def clear(self, code):
        if type(code) is list:
            for key in code:
                if key in self.__trade_stocks:
                    del self.__trade_stocks[key]
        else:
            if code in self.__trade_stocks:
                del self.__trade_stocks[code]

    def set_data(self, code, ohlc_df=None, ohlc=None): #   ohlc = None):
        # code = stock_info['code']  # kiwoom_conf.py 참조
        if code not in self.__trade_stocks:
             self.__trade_stocks[code] = {DESC_STOCK: self.__kiwoom_api.stocks[code]}

        if ohlc_df is not None:
            self.__trade_stocks[code][ohlc_df] = ohlc
            self.__trade_stocks[code][NEW_STOCK] = True

    def set_realtime_data(self, code, realtime_data):
        # if realtime_data is not None:
        if code not in self.__trade_stocks:
            self.__trade_stocks[code] = { DESC_STOCK: self.__kiwoom_api.stocks[code] }

        # 아이템 복사
        for key, item in realtime_data.items():
            if key != DESC_STOCK:
                self.__trade_stocks[code][key] = item

    def get_stock_realtime(self, code):
        """
        실시간 데이터 정보를 읽는다.
        """
        if code in self.__trade_stocks:
            return self.__trade_stocks[code][REALTIME_STOCK] if REALTIME_STOCK in self.__trade_stocks[code] else None   
        else:
            return None 

    def get_stock_info(self, code):
        """
        실시간 데이터 정보를 읽는다.
        """
        if code in self.__trade_stocks:
            return self.__trade_stocks[code][DESC_STOCK] if DESC_STOCK in self.__trade_stocks[code] else None   
        else:
            return None 

class TraderBase:
    def __init__(self, stock: Stock = None):
        self._stock = stock

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        self._stock = value

    def analysis(self, stock: Stock, _df, df_len=20) -> DataFrame:
        df = get_macd(_df)

        # check dataframe
        return df if len(df) >= df_len else None

    def pre(self, stock: Stock, df):
        pass

    def post(self, stock: Stock, df):
        pass

    def processing(self, df):
        """
        트레이딩 ...
        :param df: DataFrame
        :return: 없음
        """

        if self._stock is None:
            return


class baseWindow(QWidget, kiwoom):
    def __init__(self, auto_run: bool = False, trade_min: bool = False, develop_mode: bool = False, config_file=None):
        super().__init__()

        self._auto_running = auto_run       # 자동 실행/종료
        self._trade_min = trade_min         # 일봉/분봉 데이터 분석
        self._develop_mode = develop_mode
        self._b_auto_analysis = True  if self._auto_running else False   # 자동 Trade

        # config & cache files
        _hostname = socket.gethostname()
        self._config_filename = 'config-{}.json'.format(_hostname) if config_file is None else config_file

        self.new_method()
        self._last_time = "0000"
        self.my_stocks = {}             # 거래중인 주식 종목 (거래방식, 매입시간 ....)
        self.condition_stock_list = {}  # 검색식에서 검색된 주식종목
        self.trade_stocks = tradeStock(self.kiwoom_api)     # code:{info={}, data=dataframe}   # 실시간으로 운영중인 종목
        self.case_searchs = {}
        self.__favorites_list = []     # 즐겨찾기가 중복으로 되는지 내부 검사용
        self.__is_reload = True

        self.my_asset = {
            '목표금액': 0,  # 500000000,  # 목표금액
            '투자금액': 0,  # 100000000,
            '목표달성율': 0.0,  # 목표금액 대비 추정자산 비율
            '추정자산': 0,  # 평가금액합 + 예수금+2
            '투자이익률': 0.0,  # 투자대비 대비 추정자산 비율
            '매입금액': 0,  # 매입금액의 총합
            '평가금액': 0,  # 평가금액의 총합
            '총손익': 0,  # (평가금액 - 매입금액)/매입금액 * 100.0
            '총수익률': 0,
            '당일실현손익': 0,
            '예수금+2': 0
        }

        #  환경설정 파일 내용
        self.__config = {}

        # login...
        self.task_timer = QTimer(self)

    def new_method(self):
        self.msec = 6000

    @property
    def ats(self):
        return self.kiwoom_api

    @property
    def config(self):
        return self.__config

    @property
    def auto_analysis(self):
        return self._b_auto_analysis

    @auto_analysis.setter
    def auto_analysis(self, value):
        self._b_auto_analysis = value

    @property
    def auto_running(self):
        return self._auto_running

    @auto_running.setter
    def auto_running(self, value):
        self._auto_running = value

    @property
    def trade_min(self):
        return self._trade_min

    @trade_min.setter
    def trade_min(self, value):
        self._trade_min = value

    @property
    def develop_mode(self):
        return self._develop_mode

    @develop_mode.setter
    def develop_mode(self, value):
        self._develop_mode = value

    @property
    def config_filename(self):
        return self._config_filename

    @config_filename.setter
    def config_filename(self, value):
        self._config_filename = value

    def load_config(self):
        return load_config_file(self._config_filename)

    def save_config(self, config):
        return save_config_file(config, self._config_filename)

    def closeEvent(self, event):
        """
        윈도우에서 close button을 클릭했을때, 프로그램이 종료할지 결정한다.
        """
        if not self.auto_running:
            reply = QMessageBox.question(self, 'Quit?',
                                         'Are you sure you want to quit?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if not type(event) == bool:
                    event.accept()
                else:
                    sys.exit()
            else:
                if not type(event) == bool:
                    event.ignore()

    def login(self):
        """
        키움증권 API을 이용하여 로그인을 한다.
        """
        # 초기화 한다.
        self.trade_stocks.clearAll()
        self.__favorites_list = []

        # 환경 설정 파일을 읽어 들인다.
        self.__config = self._load_config_file()

        # logging...
        return super().login(uid='', password='', tran_mode=0, auto=True)

    def logoff(self):
        """
        키움증권 API을 이용하여 로그오프를 한다.
        """
        self.quit()

    def load_case_search(self, config):
        """
        키움 HTS에서 설정한 실시간 검색을 선택한다.
        """
        case_searchs = config['case search'].copy() if 'case search' in config else {}

        # 조건검색 리스트가 변경된 경우 다시 불러 온다.
        d = {k: case_searchs[k] for k in case_searchs \
             if k not in self.case_searchs or case_searchs[k] != self.case_searchs[k]}
        if len(d) > 0:
            self.case_searchs = case_searchs.copy()
            for idx, name in self.case_searchs.items():
                self.ats.set_realCondition(name, idx)
                sleep_ms(250)

    def get_fav_list(self, config, key=None):
        """
        환경설정 파일에서 즐겨찾기를 읽어 들인다.
        """
        fav_list = config['favorites'][APP_NAME] if 'favorites' in config and APP_NAME in config['favorites'] else {}
        return fav_list

    def disp_kwansim(self, kwansim_list):
        """
        관심종목 화면체 출력함
        :return:
        """
        
    def load_fav_list(self, config):
        """
        즐겨찾기 및 주식정보를 읽어 들인다.
        """
        fav_code_list = self.get_fav_list(config)
        self.disp_kwansim(fav_code_list)  # 즐겨찾기를 리스트에 추가

        # 즐겨찾기를 다시 불러온다.
        self.__load_fav_list(fav_code_list)

    def get_trade_ohlcv(self, code, trade_stock, trade_min: bool = False, wait_time=500):
        """
        일별/분별 거래정보를 읽어 들인다.
        """
        # 실시간 검색된 종목
        self.trade_stocks.set_realtime_data(code, trade_stock)

        if trade_min:
            self.get_ohlcv(code, interval="minute1")
        else:
            self.get_ohlcv(code, interval="day")

        sleep_ms(wait_time)

    # 사용할 계정 정보
    def set_account_info(self, text):
        pass
    def set_user_id(self, id):
        pass
    def set_investment_mode(self, mode):
        pass

    # 로그인 정보
    def on_login(self, is_logon: bool, user):
        """
        로그인이 되면 발생되는 콜백 함수
        """
        if is_logon:
            idx = 0
            for account_num in self.ats.account_num_list:
                # '10': 실거래, '11' : 모의 종합계좌, '31' : 선물거래
                if account_num[-2:] == '10' or account_num[-2:] == '11': 
                    self.account_num_idx = idx

                    text = self.ats.account_num[:-2]
                    # text = "계정: %s,   계좌번호 : %s" % (user.userId, self.ats.account_num[:-2])  # 11 제거
                    # text = '%s  (모의투자)' % text            pass

                    self.set_account_info(text)
                    logging.info(text)
                    # break
                idx += 1

            # user id
            self.set_user_id(user.userId)

            # 투자 모드 ?
            self.set_investment_mode(user.transaction_mode)

    # 실시간 시세 정보...
    def on_realtime_sise(self, real_type: str, code: str, name: str, data: dict):
        self.realtime_sise(real_type, code, name, data)

    # 실시간 주식 체결정보
    def on_realtime_che_jan(self, real_type: str, code: str, name: str, data: dict):
        self.realtime_sise(real_type, code, name, data)

    # '종목프로그램매매'
    def on_realtime_program(self, real_type: str, code: str, name: str, data: dict):
        self.realtime_sise(real_type, code, name, data)

    def on_jong_mok_minute(self, code, tick, minute_df: pandas.DataFrame, b_next: bool) -> bool:
        minute_df = minute_df.rename(columns={'체결시간': 'date',
                                              '현재가': 'close',
                                              '거래량': 'volume',
                                              '시가': 'open',
                                              '고가': 'high',
                                              '저가': 'low',
                                              '거래대금': 'amount'
                                              })
        minute_df['close'] = np.array([abs(int(x)) for x in minute_df['close']])
        minute_df['volume'] = np.array([abs(int(x)) for x in minute_df['volume']])
        minute_df.set_index('date')
        minute_df = minute_df.sort_values(by='date', axis=0, ascending=True)

        """
        print_df( minute_df.tail() )
        +----+----------------+----------+----------+------------+--------+--------+--------+
        | | 체결시간 | 현재가 | 거래량 | 거래대금 | 시가 | 고가 | 저가 |
        | ----+----------------+----------+----------+------------+--------+--------+-------- |
        | 4 | 20210225151500 | +4390 | 33743 | | +4330 | +4390 | +4325 |
        | 3 | 20210225151600 | +4355 | 35378 | | +4390 | +4395 | +4350 |
        | 2 | 20210225151700 | +4340 | 30583 | | +4360 | +4385 | +4340 |
        | 1 | 20210225151800 | +4325 | 26247 | | +4360 | +4370 | +4320 |
        | 0 | 20210225151900 | +4310 | 34205 | | +4335 | +4340 | +4310 |
        +----+----------------+----------+----------+------------+--------+--------+--------+
        """
        # print('==> code : {}({})'.format(self.stocks[code]['name'], code))
        # logging.debug('==> code : {}({})'.format(self.stocks[code]['name'], code))
        # logging.debug('\n' + tabulate(minute_df.tail(), headers='keys', tablefmt='psql'))
        self.trade_stocks.set_data(code, OHLC_MINUTE, minute_df[-90:].copy())   # 90분만

        return False

    def on_jong_mok_daily(self, code, daily_df: pandas.DataFrame, b_next: bool) -> bool:
        daily_df = daily_df.rename(columns={'일자': 'date',
                                            '현재가': 'close',
                                            '거래량': 'volume',
                                            '시가': 'open',
                                            '고가': 'high',
                                            '저가': 'low',
                                            '거래대금': 'amount'
                                            })
        daily_df['close'] = np.array([abs(int(x)) for x in daily_df['close']])
        daily_df['volume'] = np.array([abs(int(x)) for x in daily_df['volume']])
        daily_df.set_index('date')
        daily_df = daily_df.sort_values(by='date', axis=0, ascending=True)

        # print('==> code : {}({})'.format(self.stocks[code]['name'], code))
        # logging.debug('==> code : {}({})'.format(self.stocks[code]['name'], code))
        # logging.debug('\n' + tabulate(daily_df.tail(), headers='keys', tablefmt='psql'))
        self.trade_stocks.set_data(code, OHLC_DAILY, daily_df[-60:].copy())  # 60일만

        # no more ...
        return False

    # 소요주식에 대한 전체 리스트 화면에 출력
    def disp_account_detail(self, account_no: str, account_detail: dict, code=None) -> None:
        pass

    # 실시간 주식 시세/체결정보
    def disp_realtime_sise(self, code, name, data):
        pass

    def disp_calculate_values(self):
        pass

    def _set_account_detail(self, account_detail: dict, code):
        stock = account_detail[code]
        if stock['보유수량'] > 0:
            if code in self.my_stocks:
                my_stock = self.my_stocks[code]
                for data in my_stock:
                    if data not in stock:
                        stock[data] = my_stock[data]

            # 신규데이터 재설정
            #if '매입시간' not in stock:
            #    stock['매입시간'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 고가,저가 재 설정
            #close = abs(stock['현재가'])
            #if ('고가' not in stock) or (stock['고가'] < close):
            #    stock['고가'] = close
            #if '저가' not in stock or (stock['저가'] > close):
            #    stock['저가'] = close

            # 보유주식정보 저장
            self.my_stocks[code] = stock.copy()
        else:
            # 보유 하지 않는 주식정보 재설정
            # if '고가' in stock:
            #     del (stock['고가'])
            # if '저가' in stock:
            #     del (stock['저가'])
            # if '매입시간' in stock:
            #     del (stock['매입시간'])
            # if 'stoploss' in stock:
            #     del (stock['stoploss'])

            if code in self.my_stocks:
                del (self.my_stocks[code])

    def on_account_detail(self, account_no: str, account_detail: dict, code=None) -> None:
        """ 계좌에 등록된 모든 종목을 화면에 출력한다. """
        # 나의 계정정보를 재 설정한다.
        if code is None:
            for code1 in account_detail:
                self._set_account_detail(account_detail, code1)
        else:
            self._set_account_detail(account_detail, code)

        # 내 주식 정보를 계산
        self.calculate_values()

        # 소유주식을 화면 출력
        # 보유수량이 0 보다 큰 종목을 선택한다.
        new_account_detail = {code1: value1 for code1, value1 in account_detail.items() if value1['보유수량'] > 0}
        self.disp_account_detail(account_no, new_account_detail, code)


    def on_trading_finished(self, code, name, cnt, trade_name) -> None:
        price = format(self.account_stock(code)['현재가'], ',')
        volume = format(self.account_stock(code)['보유수량'], ',')
        cnt_str = format(cnt, ',')
        rate = '{:,.02f}'.format(self.account_stock(code)['수익률'])
        logging.debug("==> %s 처리완료: %s(%s) %s원, %s 주, 보유수량 %s 주, 수익율 %s%%" % (trade_name, name, code,
                                                                              price, cnt_str, volume, rate))
        # refresh..
        self.__is_reload = True

        # 나의 소유 주식종목의 내용이 변경 될때마다 저장한다.
        # self.save_my_stocks()

    # 신규 주식이 추가 되었을 때..
    def on_new_account_stock(self, code, name):
        """ 
        신규 주식이 추가 되었을 때.. 
        """
        self.trade_stocks.set_data(code)

    # 실시간 주식 시세/체결정보
    def realtime_sise(self, real_type, code, name, data):
        """" 실시간 시세정보 
        """
        # 현재가
        if code in self.trade_stocks.stocks:
            self.trade_stocks.stocks[code]['현재가'] = INT(data['현재가'])
            if '누적거래량' in data:
                self.trade_stocks.stocks[code]['누적거래량'] = INT(data['누적거래량'])

        # 보유종목일때, 보유주식 정보 갱신
        if code in self.account_stocks:
            # 실시간 수익율 계산
            self.calculate_values()

        # 실시간 코드정보(현재가, 거래량...)
        self.disp_realtime_sise(code, name, data)

    def calculate_values(self):
        profit_loss = 0
        buy_total = 0

        for stock in self.account_stocks.values():
            if int(stock['보유수량']) > 0:
                profit_loss = profit_loss + (stock['손실차액'] if '손실차액' in stock else 0)
                buy_total += stock['매입금액']

        asset_total = buy_total + profit_loss
        profit_loss_rate = ((asset_total - buy_total) / float(buy_total)) * 100.0 if buy_total != 0 else 0.0

        self.my_asset['추정자산'] = int(asset_total + int(self.kiwoom_api.trade_detail['예수금+2']))
        self.my_asset['목표달성율'] = (self.my_asset['추정자산'] / float(self.my_asset['목표금액'])) * 100
        self.my_asset['투자이익률'] = (self.my_asset['추정자산'] / float(self.my_asset['투자금액'])) * 100

        self.my_asset['매입금액'] = buy_total
        self.my_asset['평가금액'] = asset_total
        self.my_asset['총손익'] = profit_loss
        self.my_asset['총수익률'] = profit_loss_rate
        self.my_asset['당일실현손익'] = INT(self.kiwoom_api.trade_detail['당일실현손익(유가)'])
        self.my_asset['예수금+2'] = INT(self.kiwoom_api.trade_detail['예수금+2'])

        # 결과 화면에 출력
        self.disp_calculate_values()

    # 조건검색에서 받은 데이터, 'L': 검색, 'I' : 실시간 추가발생, 'D' : 실시간 조건검색 제거
    def on_conditions_stocks(self, gubun, code, name, condition_name, condition_index, sno=None):
        """
        조건검색에서 받은 이벤트
        """
        now = dt.datetime.now()
        time_str = now.strftime('%H:%M:%S')

        print('==> {} : {}({}), 상태: {}, 조건명: {}, 조건인덱스: {}'.format(time_str, name, code, gubun, condition_name,
                                                                   condition_index))
        # logging.info('==> {} : {}({}), 상태: {}, 조건명: {}, 조건인덱스: {}'.format(time_str, name, code, gubun,
        #                                                                  condition_name, condition_index))

        # 조건검색 리스트
        if gubun == "L":
            self.condition_stock_list[code] = {
                '조건코드': condition_index,
                '코드명': condition_name,
                '종목코드': code,
                '종목명': name,
                '현재가': 0,
                '대비율': 0.0,
                '거래량': 0,
                '매수': "매수" if code in self.account_stocks and self.account_stock(code)[
                    '보유수량'] > 0 else "미매수",
                '편입시간': time_str,
                '화면번호': "88888"
            }

        # 실시간 조건검색식에 추가
        elif gubun == "I":
            if code not in self.condition_stock_list:
                self.condition_stock_list[code] = {
                    '조건코드': condition_index,
                    '코드명': condition_name,
                    '종목코드': code,
                    '종목명': name,
                    '현재가': 0,
                    '대비율': 0.0,
                    '거래량': 0,
                    '매수': "매수" if code in self.account_stocks and self.account_stocks[code][
                        '보유수량'] > 0 else "미매수",
                    '편입시간': time_str,
                    '화면번호': "88888"
                }
        # 조건 검색 종목에서 삭제 되었습니다.
        elif gubun == "D":
            # 리스트에서 제거
            if code in self.condition_stock_list:
                del self.condition_stock_list[code]

    def _load_config_file(self):
        """
        환경설정 파일을 읽어들인다.
        """
        config = load_config_file(config_file=self._config_filename)

        # 설정에서 받아들인 투자목표 금액..
        self.my_asset['목표금액'] = config['general']['기본정보']['목표']
        self.my_asset['투자금액'] = config['general']['기본정보']['투자금']

        return config

    def disp_dashboard(self):
        """
        코스피, 코스닥, 개인,외인,기관의 추세를 보여 준다.
        :return:
        """

    def processing_ready(self, bauto = False, msec=60000):
        """
        서버에 접속을 하고, 트레이딩 사전 작업을 실행 한다.
        """
        if self.ats.is_connected:
            # 설정파일 읽어 들인다.
            config = self._load_config_file()

            # 예수금 정보를 읽는다.
            self.load_deposit(config)
            
            self.get_jisu(Marketcode.KOSPI)
            sleep_ms(1000)
            self.get_jisu(Marketcode.KOSPI200)
            sleep_ms(1000)
            self.get_jisu(Marketcode.KOSDAQ)
            sleep_ms(1000)
            self.get_jisu(Marketcode.KOSDAQ200)
            sleep_ms(1000)

            logging.info('---------- 주식자동 드레이딩 준비 완료 ----------')

            # 보유주식을 읽어 들인다.
            self.load_fav_list(config)

            self._last_time = now_string()
            self.msec = msec

            self.task_timer.start(5000)
            self.task_timer.timeout.connect(self.__schedule_ready_trade)

    def __load_fav_list(self, codes, wait_time=500):
        """
        설정파일에 즐겨퍄일
        codes : list or dict, turple
        """
        # 소유 종목에 대한 분봉/일봉/주봉/월봉 시세 정보를 받아온다.
        code_dict = {code: {REALTIME_STOCK: None} for code in self.account_stocks}
        
        # 내계정에 없고 즐겨찾기에 있으면 실시간 데이터 ...
        tmp_codes = [code for code in codes if code not in code_dict]
        for code in tmp_codes:
            code_dict[code] = {
                    REALTIME_STOCK: dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    DESC_FAV : '1'  # 즐겨찾기용
                }
            
        # 조건검색에 있는 데이터는 실시간 데이터
        tmp_codes = [code for code in self.condition_stock_list if code not in code_dict]
        for code in tmp_codes:
            code_dict[code] = {
                REALTIME_STOCK: dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                CONDITON_STOCK: self.condition_stock_list[code]
            }

        # 실시간 검색된 종목
        for code, code_info in code_dict.items():
            self.trade_stocks.set_realtime_data(code, code_info)

        # 즐겨찾기 & 실시간 시세 정보 감시 재설정
        # 즐겨찾기(중복검사)
        fav_codes = [code for code in code_dict]
        fav_list = set(fav_codes)
        pre_list = set(self.__favorites_list)

        if fav_list != pre_list:
            self.__favorites_list = fav_codes.copy()
            self.add_favorites(self.__favorites_list)

            # 사용하지 않은 trade_stocks 정보는 삭제
            # codes = [code for code in self.trade_stocks.stocks if code not in self.__favorites_list]
            # self.trade_stocks.clear(codes)

    def __schedule_ready_trade(self):
        """
        자동 트레이딩을 분단위로 실핸 할 수 있도록 waiting 한다.
        """
        # 분단위로 자동 트레이딩 !
        now_s = now_string()
        if self._last_time != now_s:
            minute = int(now_s[-1])
            m = minute % 4
            if m == 0:
                ret = self.get_jisu(Marketcode.KOSPI)
            elif m == 1:
                ret = self.get_jisu(Marketcode.KOSPI200)
            elif m == 2:
                ret = self.get_jisu(Marketcode.KOSDAQ)
            elif m == 3:
                ret = self.get_jisu(Marketcode.KOSDAQ200)
            # print(ret)

            self.__schedule_trade(now_s)

            # 마지막 처리시간
            self._last_time = now_s
        else:
            # 실시간, 코스피/코스닥 정보
            self.disp_dashboard()

    def load_deposit(self, config):
        """
        예수금 상태를 읽어 들인다.
        """
        passwd = config['general']['account']['passwd']
        self.get_deposit(self.ats.account_num, passwd)  # 예수금 정보
        self.calculate_values()

    def __schedule_trade(self, now_s):
        """
        자동 트레이딩 ....
        """
        # 환경설정 파일을 읽어 들인다.
        config = self._load_config_file()

        start_tm = config['general']['trading']['start']
        end_tm = config['general']['trading']['end']
        
        weekday = dt.datetime.now().weekday()
        is_available_trading = (start_tm <= now_s and now_s <= end_tm) and (weekday < 5) # 토/일 은 제외

        # 자동시작일때, 정해진 시간에 프로그램 종료
        if self.auto_running:
            if ('use-auto-finish' in config['general']['trading'] and config['general']['trading']['use-auto-finish']) and \
                (now_s >= config['general']['trading']['auto-finish'] or self.ats.is_connected is False):
                logging.info('%s : 프로그램이 자동 종료합니다.' % now_s)
                # QCoreApplication.instance().quit()
                self.close()
                return

        # 10 분마다.(수익금 계산 다시 계산) - 수익금 오차방지 
        if self._last_time[:3] != now_s[:3]:
            self.do_periodic_check(config, now_s, is_available_trading)
            if self.__is_reload:
                self.load_deposit(config)
                self.__is_reload = False

        # 즐겨찾기에 신규 추가된 종목코드 확인
        self.load_fav_list(config)

        # 조건검색식을 설정한다.
        self.load_case_search(config)

        # 개발모드 & 거래시간
        if self.develop_mode is False and is_available_trading is False:
               return

        # 자동 트레이딩
        # 자동 트래이드 실행 !!!
        if self.auto_analysis:
            self.do_trade_processing(config, now_s, is_available_trading)

        # 소유한 주식정보의 최신내용을 저장한다.        
        self.save_acount_stocks()

        # 소유한 주식정보의 최신내용을 저장한다.        
        self.do_finish_processing(config, now_s)

    ####################### auto trading mode #######################
    def do_periodic_check(self, config, now_s, is_available_trading):
        """
        주기적인 점검 사항
        """
        pass

    def do_trade_processing(self, config, now_s, is_available_trading):
        """
        자동 트래이드 실행!!!
        """
        pass

    def do_finish_processing(self, config, now_s):
        """
        자동 트래이드 최종 실행!!!
        """
        pass


if __name__ == '__main__':
    # ------------------------------------ test code ------------------------------------------- #
    class testWindowClass(baseWindow):
        def __init__(self):
            super().__init__()

            ## self.cmb_account_info = QComboBox() # QLabel()  # 계정 : xxxxxx, 투자방법 : 모의투자
            self.verticalLayoutWidget = QtWidgets.QWidget(self)
            self.verticalLayoutWidget.setGeometry(QtCore.QRect(25, 45, 501, 80))
            self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
            self.layoutAccountInfo = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
            self.layoutAccountInfo.setContentsMargins(0, 0, 0, 0)
            self.layoutAccountInfo.setObjectName("layoutAccountInfo")
            self.middle_widget = QtWidgets.QWidget(self.verticalLayoutWidget)
            self.middle_widget.setObjectName("middle_widget")
            self.lbl_userid = QtWidgets.QLabel(self.middle_widget)
            self.lbl_userid.setGeometry(QtCore.QRect(10, 0, 120, 20))
            self.lbl_userid.setObjectName("label")
            self.cmb_account_info = QtWidgets.QComboBox(self.middle_widget)
            self.cmb_account_info.setGeometry(QtCore.QRect(130, 0, 150, 20))
            self.cmb_account_info.setObjectName("cmb_account_info")
            self.chk_Investment = QtWidgets.QCheckBox(self.middle_widget)
            self.chk_Investment.setEnabled(False)
            self.chk_Investment.setGeometry(QtCore.QRect(300, 0, 81, 20))
            self.chk_Investment.setObjectName("chk_Investment")
            # self.layoutAccountInfo.addWidget(self.middle_widget)
            self.lbl_userid.setText("계정")
            self.chk_Investment.setText("모의투자")
            self.cmb_account_info.currentIndexChanged.connect(self.cmb_account_info_changed)
            
            self.tbl_accounts_detail = QTableWidget()
            self.tbl_account_info = QTableWidget()
            self.tbl_case_search = QTableWidget()
            self.log_widget = setLogging(self, prev_hdr='test-trade-')  # logging..

            # ----- layout ----- #
            font = QFont()
            font.setPointSize(8)
            stylesheet = "::section{Background-color:rgb(0,170,170)}"

            # 계좌정보
            self.tbl_account_info.setFont(font)
            self.tbl_account_info.horizontalHeader().setStyleSheet(stylesheet)
            self.tbl_account_info.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tbl_account_info.verticalHeader().hide()
            self.tbl_account_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tbl_account_info.setSelectionMode(QAbstractItemView.NoSelection)
            self.tbl_account_info.setEnabled(False)
            setTableHeader(self.tbl_account_info, headers=[x for x in self.my_asset])
            self.tbl_account_info.setRowCount(1)
            # self.tbl_account_info.setFocusPolicy(Qt.NoFocus)

            # 보유종목
            self.tbl_accounts_detail.setFont(font)
            self.tbl_accounts_detail.horizontalHeader().setStyleSheet(stylesheet)
            self.tbl_accounts_detail.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tbl_accounts_detail.verticalHeader().hide()
            setTableHeader(self.tbl_accounts_detail, headers=['번호',
                                                            '구분',
                                                            '종목코드',
                                                            '종목명',
                                                            '현재가',
                                                            '보유수량',
                                                            '매입가',
                                                            '매입금액',
                                                            '평가금액',
                                                            '수익률', '수수료', '세금', '평가손익', '매입일자','매입시간'])

            # layout
            layout1_0 = QHBoxLayout()
            # layout1_0.addWidget(self.cmb_account_info)
            layout1_0.addWidget(self.middle_widget)
            
            layout1_1 = QHBoxLayout()
            layout1_1.addWidget(self.tbl_account_info)
            layout1_2 = QHBoxLayout()
            layout1_2.addWidget(self.tbl_accounts_detail)
            layout1_3 = QHBoxLayout()
            layout1_3.addLayout(self.log_widget)

            layout1 = QVBoxLayout()
            layout1.addLayout(layout1_0)
            layout1.addLayout(layout1_1)
            layout1.addLayout(layout1_2)
            layout1.addLayout(layout1_3)
            layout1.setStretch(0, 1)
            layout1.setStretch(1, 1)
            layout1.setStretch(2, 20)
            layout1.setStretch(3, 3)

            self.setLayout(layout1)
            self.setGeometry(100, 100, 1300, 800)
            center(self)

            # --- API --- #
            self.login()
            self.processing_ready(True)

        # 사용할 계정 정보
        def set_account_info(self, text):
            # self.lbl_account_info.setText(text)
            self.cmb_account_info.addItem(text)

        def set_user_id(self, id):
            self.lbl_userid.setText("계정: %s" % (id))

        def set_investment_mode(self, mode):
            if mode == SIM_INVESTMENT:
                self.chk_Investment.setChecked(True)
   
        def cmb_account_info_changed(self):
            print("account : %s" % self.cmb_account_info.currentIndex())

        def disp_account_detail(self, account_no: str, account_detail: dict, code=None) -> None:
            """ 계좌에 등록된 모든 종목을 화면에 출력한다. """
            self.tbl_accounts_detail.setRowCount(len(account_detail))
            for row, code in enumerate(account_detail):
                stock = account_detail[code]

                setTableWidgetItemEx(self.tbl_accounts_detail, row, 0, row + 1, f_color=black())
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 1, credit_gubun(stock['신용구분']))
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 2, code)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 3, stock['종목명'], align=Qt.AlignLeft | Qt.AlignVCenter,
                                    b_color=white() if stock['수익률'] > -5.0 else red())
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 4, INT(stock['현재가']),
                                    align=Qt.AlignRight | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 5, INT(stock['보유수량']), f_color=black())

                setTableWidgetItemEx(self.tbl_accounts_detail, row, 6, INT(stock['매입가']), f_color=black(),
                                    align=Qt.AlignRight | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 7, INT(stock['매입금액']), f_color=black(),
                                    align=Qt.AlignRight | Qt.AlignVCenter)

                setTableWidgetItemEx(self.tbl_accounts_detail, row, 8, INT(stock['평가금액']),
                                    f_color=red() if stock['손실차액'] > 0 else blue(),
                                    align=Qt.AlignRight | Qt.AlignVCenter)

                s = '%0.2f %%' % FLOAT(stock['수익률'])
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 9, s,
                                    f_color=red() if stock['손실차액'] > 0 else blue(),
                                    align=Qt.AlignRight | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 10, INT(stock['수수료']), f_color=black(),
                                    align=Qt.AlignRight | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 11, INT(stock['세금']), f_color=black(),
                                    align=Qt.AlignRight | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 12, INT(stock['손실차액']),
                                    align=Qt.AlignRight | Qt.AlignVCenter)
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 13, stock['매매정보']['매입시간'][:10])
                setTableWidgetItemEx(self.tbl_accounts_detail, row, 14, stock['매매정보']['매입시간'][-8:])

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
                    if code in self.account_stocks:
                        stock = self.account_stocks[code]

                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 3, stock['종목명'],
                                            align=Qt.AlignLeft | Qt.AlignVCenter,
                                            b_color=white() if stock['수익률'] > -5.0 else red())

                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 4, stock['현재가'],
                                            align=Qt.AlignRight | Qt.AlignVCenter)

                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 8, INT(stock['평가금액']),
                                            f_color=red() if stock['손실차액'] > 0 else blue(),
                                            align=Qt.AlignRight | Qt.AlignVCenter)

                        s = '%0.2f %%' % FLOAT(stock['수익률'])
                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 9, s,
                                            f_color=red() if stock['손실차액'] > 0 else blue(),
                                            align=Qt.AlignRight | Qt.AlignVCenter)
                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 10, INT(stock['수수료']), f_color=black(),
                                            align=Qt.AlignRight | Qt.AlignVCenter)
                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 11, INT(stock['세금']), f_color=black(),
                                            align=Qt.AlignRight | Qt.AlignVCenter)
                        setTableWidgetItemEx(self.tbl_accounts_detail, row, 12, INT(stock['손실차액']),
                                            align=Qt.AlignRight | Qt.AlignVCenter)
                    break
                # if code ?
            # for loop !!

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

    # while True:
    app = QApplication(sys.argv)  # 메인 윈도우를 실행한다.
    app.setStyle('Fusion')

    win = testWindowClass()
    win.show()

    sys.exit(app.exec_())
