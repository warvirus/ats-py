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

# -------------- 수정 내용 ----------
#
# 2022.1.15 : 기초 코드 완성
# 2023.6.8  : 실시간 데이터에서 실시간 데이터와 받은 데이터 구분함.
# -----------------------------------

import sys
import numpy as np
import pandas as pd
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QAxContainer import QAxWidget

from .tools import *
from .events import event_list_single
from .kiwoom_conf import *
from .kiwoom_transaction import req_comm, transaction
from .ui import app_ui, order_type, order_gb, SIM_INVESTMENT, user_info, tax
import datetime as dt

DEBUG = True

DEF_USER_RESERVED = '매매정보'
DEF_TRANDATE = '매입시간'
DEF_TRAN_HIGH = '고가'
DEF_TRAN_LOW = '저가'

#########################################################################
DEFAULT_WAIT = 0.5
#########################################################################

def get_cache_dir(subdir=None, base='kiwoom'):
    """
    Function for getting cache directory to store reused files like kernels, or scratch space
    for autotuning, etc.
    """
    import os

    cache_dir = os.environ.get("TEMP")

    if cache_dir is None:
        cache_dir = os.getcwd() + '\\' + base
    else:
        cache_dir = cache_dir + '\\' + base

    if subdir:
        subdir = subdir if isinstance(subdir, list) else [subdir]
        cache_dir = os.path.join(cache_dir, *subdir)

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    return cache_dir 

def get_my_stocks_name(cache_dir, userid = None):
    import socket
    
    if cache_dir is None:
        cache_dir = get_cache_dir()

    hostname = socket.gethostname()
    if userid is None:
        program_name = os.path.splitext(os.path.basename( sys.argv[0]))[0]
    else:
        program_name = os.path.splitext(os.path.basename( sys.argv[0]))[0] + '-' + userid
    return '{}\\{}-{}.json'.format(cache_dir, program_name, hostname)

def isNext(sPrevNext):
    """
    Transaction 에서 더 받을 데이터가 있는지 ?
    :param sPrevNext:
    :return:
    """
    return False if sPrevNext != "2" else True

class kiwoom_api(QObject):
    def __init__(self, _app_ui = None, timeout_ms=-1, *__args):
        super().__init__(*__args)

        self._app_ui =  _app_ui if (_app_ui is not None) and isinstance(_app_ui, app_ui) else app_ui()
        self.__trans_delay = DEFAULT_WAIT
        self.__queue_seq = 0
        self.__transaction_dict = {}  # 트랜잭션 function list
        self.__real_data_dict = {}  # 실시간 데이터에 대한 처리

        self.__is_logon = False
        self.__user_info = None  # 사용자 정보
        # self.__timeout_ms = timeout_ms

        self._user_id = ''  # 사용자 계정
        self.__transaction_mode = 0         # 투자정보(1 -모의투자, other : 실투자)
        self.__account_num_list = []        # 소요한 계정 리스트
        self.__current_account_num_idx = 0  # 현재 운영중인 계정 인덱스

        self.__stock_list = {}              # 주식리스트 {'000000':{'name':"rexx", ...}, '000001':{'name':"rexx", ...}, ...}
        self.__stock_market_list = {}       # 주식 종류 리스트 {'0': {'000000':{'name':'rexx', ...}, '000001':{
        # 'name':'rexx', ...}, ...}, {'10': ...}}

        # 보유종목
        self._account_stocks = {}
        self._trade_detail = {
            '예수금': 0,
            '예수금+1': 0,
            '예수금+2': 0,
            '주문가능금액': 0,
            '당일실현손익(유가)': 0,
            '당일신현손익률(유가)': 0.0,
            '당일실현손익(신용)': 0,
            '당일실현손익률(신용)': 0.0
        }

        item = {'현재가': 0, '등락율': 0.0, '전일대비': 0, '개인순매수': 0, '외인순매수': 0,
                '기관순매수': 0}  # 0-현재가, 1-등락율, 2-전일대비, 3-개인순매수, 4-외인순매수, 5-기관순매수
        self._dashboard = {
            '코스피': item.copy(),
            '코스피200': item.copy(),
            '코스닥': item.copy(),
            '코스닥100': item.copy()
        }

        # 수수료/거래세 비율
        self._tax = tax()

        # events
        self._logon_event_slot = event_list_single()
        self._trans_event_slot = event_list_single()
        self._case_condition_slot = event_list_single()

        # -------------------------------------
        # API init 
        # -------------------------------------
        # self.setControl('KHOPENAPI.KHOpenAPICtrl.1')          # kiwoom OCX
        self.ocx = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')                           # kiwoom OCX
        self.ocx.OnEventConnect[int].connect(self.__login_slot)                             # 로그인 처리 이벤트입니다. 성공이면 인자값
        self.ocx.OnReceiveMsg[str,str,str,str].connect(self.__receive_msg_slot)             # 서버통신 후 수신한 메시지를 알려줍니다
        self.ocx.OnReceiveTrData[str, str, str, str, str, int, str, str, str].connect(self.__transaction_slot)  # 조회요청 응답을 받거나 조회데이터를 수신했을때 호출
        self.ocx.OnReceiveRealData[str,str,str].connect(self.__realtime_slot)               # 실시간 데이터 수신할때마다 호출되며 SetRealReg()함수로 등록한 실시간 데이터도 이 이벤트로 전달
        self.ocx.OnReceiveChejanData[str,int,str].connect(self.__che_jan_slot)              # 주문요청후 주문접수, 체결통보, 잔고통보를 수신할 때 마다 호출되며 GetChejanData()함수
        self.ocx.OnReceiveConditionVer[int,str].connect(self.__receiveCondition_slot)       # 조건검색, 용자 조건식요청에 대한 응답을 서버에서 수신하면 호출되는 이벤트입니다.
        self.ocx.OnReceiveTrCondition[str,str,str,int,int].connect(self.__receiveTrCondition_slot)      # 조건검색 요청으로 검색된 종목코드 리스트를 전달하는 이벤트입니다. 종목코드 리스트는 각 종목코드가 ';'로 구분되서 전달됩니다.
        self.ocx.OnReceiveRealCondition[str,str,str,str].connect(self.__receiveRealCondition_slot)      # 실시간 조건검색 요청으로 신규종목이 편입되거나 기존 종목이 이탈될때 마다 호출됩니다.

        # ---------- 실시간 데이터 처리
        self.__real_data_dict = {
            KEY_REALTIME_SISE: self._app_ui.on_realtime_sise,
            KEY_REALTIME_CHEJAN: self._app_ui.on_realtime_che_jan,
            KEY_REALTIME_PROGRAM: self._app_ui.on_realtime_program,
            KEY_REALTIME_HOGA_JAN: self._app_ui.on_realtime_hoga_jan,
            KEY_REALTIME_HOGA_TRADE: self._app_ui.on_realtime_hoga_trade,
            KEY_REALTIME_OVERTIME_HOGA: self._app_ui.on_realtime_overtime_hoga,

            KEY_REALTIME_ENC_HOGA: self.__realtime_ENC_hoga_slot,
            KEY_REALTIME_ENC_SISE: self.__realtime_ENC_sise_slot,
            KEY_REALTIME_ENC_CHEJAN: self.__realtime_ENC_che_jan_slot,
            KEY_REALTIME_GUESS_CHEJAN: self.__realtime_guess_che_jan_slot,
            KEY_REALTIME_JONGMOK: self.__realtime_jong_mok_slot,
            KEY_REALTIME_OVERTIME: self.__realtime_overtime_slot,
            KEY_REALTIME_TRADER: self.__realtime_trader_slot,
            KEY_REALTIME_TODAY_TRADER: self.__realtime_today_trader_slot,
            KEY_REALTIME_INDUSTRY_IDX: self.__realtime_industry_idx_slot,
            KEY_REALTIME_GUESS_INDUSTRY: self.__realtime_guess_industry_idx_slot, 
            KEY_REALTIME_INDUSTRY_UPDOWN: self.__realtime_industry_updown_slot,
            KEY_REALTIME_TIME: self.__realtime_time_slot,
        }

        # 보유주식에 대한 정보를 저장한 위치 설정
        self._cache_dir = get_cache_dir()
        self._cache_name = get_my_stocks_name(self._cache_dir)

        # task 관리
        # self.task_timer = QTimer(self)
        # self.task_timer.timeout.connect(self.__task_timeout)
        # self.task_timer.start(5000)
        # def __task_timeout(self):
        # for tr_info in self.__transaction_dict.values:
        #    self._app_ui.print(f'==>{tr_info.tr_name} : {tr_info.diff_task_ns / 1000000000.0} s')
        # self._app_ui.print('----------------')
        # pass

    #   def __del__(self):
    # self._app_ui.print("deleted in descriptor object")
    # self.clear()
    #       self.setControl('')

    def init(self):
        pass

    def __del__(self):
        print("kiwoom api finished.")

    def _queue_seq_reset(self):
        self.__queue_seq = 0
        self.__transaction_dict = {}  # 트랜잭션 function list

    def _queue_seq_new_no(self):
        self.__queue_seq += 1
        return self.__queue_seq

    def get_jongmok_real_name(self, jongmok_code):
        """
        종목명을 구한다.
        :param jongmok_code:
        :return:
        """
        str1 = str(self.ocx.dynamicCall("GetMasterCodeName(QString)", jongmok_code))
        return str1.strip()

    def get_jongmok_name(self, jongmok_code):
        """
        종목명을 구한다.
        :param jongmok_code:
        :return:
        """
        str1 = self.ocx.dynamicCall("GetMasterCodeName(QString)", jongmok_code)
        return replace_spaces(str1.strip())

    def get_jongmok_construction(self, jongmok_code):
        """
        종목 구분 코드명
        :param jongmok_code:
        :return:
        """
        str1 = self.ocx.dynamicCall("GetMasterConstruction(QString)", jongmok_code)
        return str1.strip()

    def get_jongmok_market_type(self, jongmok_code) -> str:
        """
        종목 의 타입을 찾는다.
        :param jongmok_code:
        :return:
        """
        str1 = self.ocx.dynamicCall("GetMarketType(QString)", jongmok_code)

        return str(INT(str1))  # .strip()

    def get_jongmok_state(self, jongmok_code) -> str:
        """
        입력한 종목의 증거금 비율, 거래정지, 관리종목, 감리종목, 투자융의종목, 담보대출, 액면분할, 신용가능 여부를 전달합니다.
        :param jongmok_code:
        :return:
        """
        str1 = self.ocx.dynamicCall("GetMasterStockState(QString)", jongmok_code)
        return str1.strip()

    def get_jongmok_listingday(self, jongmok_code) -> str:
        """
        종목 상장일
        :param jongmok_code:
        :return:
        """
        str1 = self.ocx.dynamicCall("GetMasterListedStockDate(QString)", jongmok_code)
        return str1.strip()

    # 로그인한 사용자 정보를 반환한다.
    # “ACCOUNT_CNT” : 전체 계좌 개수를 반환한다.
    # "ACCNO" : 전체 계좌를 반환한다. 계좌별 구분은 ‘;’이다.
    # “USER_ID” - 사용자 ID를 반환한다.
    # “USER_NAME” : 사용자명을 반환한다.
    # “KEY_BSECGB” : 키보드보안 해지여부. 0:정상, 1:해지
    # “FIREW_SECGB” : 방화벽 설정 여부. 0:미설정, 1:설정, 2:해지
    def get_user_id(self):
        return self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")  # 'userid'

    def get_account_list(self):
        return self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")  # '12121;12121'#

    def get_transaction_mode(self):
        return self.ocx.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")

    def get_codelist_by_market_code(self, market_code='0'):
        """
        마켓에서 사용하는 종목 코드의 리스트를 모두 읽어 들인다.
        :param market_code: 시장별 종목코드 구문  값
                    -1 : 전체
                     0 : 장내 default
                     10 : 코스탁
                     3 : ELW
                     8 : ETF
                     50 : KONEX
                     4 : 무쥬얼펀드
                     5 : 신주인수권
                     6 : 리츠
                     9 : 하일럴펀드
                     30 : K-OTC
        :return:
        """
        code_list_str = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market_code)
        # '1212;123123;23324;12312;'
        return code_list_str.split(';')[:-1]

    def __get_account_info(self):
        """
        사용자의 계좌 정보를 읽어 들인다.
        :return:
        """

        # 사용자 정보와 거래모드
        self._user_id = self.get_user_id()  # 'userid'
        self.__transaction_mode = SIM_INVESTMENT if self.get_transaction_mode() == '1' else 0

        # 거래정보 cache 파일을 재 설정
        self._cache_name = get_my_stocks_name(self._cache_dir, self._user_id)
        print('cache file : ' + self._cache_name)

        # 모의투자의 수수율 재조정
        self._tax = self._app_ui.on_init_tax(self.__transaction_mode, self._tax)

        # 계정 리스트, 첫번째 사용(default: 0)
        self.__current_account_num_idx = 0  # 현재 운영중인 계정 인덱스
        self.__account_num_list = self.get_account_list().split(';')  # '12121;12121'
        for idx, account in enumerate(self.__account_num_list):
            if len(account) >= 8+2 and \
                (account[-2:] == '11' or account[-2:] == '10'):
                # '10' : 실거래
                # '11' : 모의투자 계좌
                # '30' : 선물옵션
                # '31' : 선물옵션 모의투자
                # '70' : 해외선물
                # '71' : 해외선물 모으투자
                self.__current_account_num_idx = idx
                break

        logging.debug("login ok ! {}, account_num : {}".format(self._user_id, self.__account_num_list))

    @property
    def get_cache_dir(self):
        return self._cache_dir 

    @property
    def user_id(self):
        return self._user_id

    @property
    def transaction_mode(self):
        return self.__transaction_mode

    @property
    def stocks(self) -> dict:
        return self.__stock_list

    @property
    def app_ui(self):
        return self._app_ui

    @property
    def account_num_list(self):
        return self.__account_num_list

    @property
    def account_num(self):
        """
        소유한 계정번호
        """
        return self.__account_num_list[self.__current_account_num_idx]

    @account_num.setter
    def account_num(self, value):
        """
        소유한 계정번호
        """
        for idx, account in enumerate(self.__account_num_list):
            if account == value:
                self.__current_account_num_idx = idx

    @property
    def account_num_idx(self):
        return self.__current_account_num_idx

    @account_num_idx.setter
    def account_num_idx(self, idx):
        if len(self.__account_num_list) >= 0:
            if 0 <= idx < len(self.__account_num_list):
                self.__current_account_num_idx = idx

    @property
    def account_stocks(self) -> dict:
        """
        보유종목 리스트
        """
        return self._account_stocks

    @property
    def count_account_stock(self):
        return len([cd for cd, stock in self._account_stocks.items() if stock['보유수량'] > 0])

    # function..
    def account_stock(self, code) -> dict:
        """
        보유종목중 주식정보
        """
        return self._account_stocks[code] if code in self._account_stocks else None

    @property
    def trans_delay(self):
        return self.__trans_delay

    @trans_delay.setter
    def trans_delay(self, value):
        self.__trans_delay = value

    @property
    def trade_detail(self):
        return self._trade_detail

    @property
    def balance(self):
        return self._trade_detail['주문가능금액']

    # 수수료 설정
    @property
    def buy_fee(self):
        return self._tax.buy

    @buy_fee.setter
    def buy_fee(self, value):
        self._tax.buy = value

    @property
    def sell_fee(self):
        return self._tax.sell

    @sell_fee.setter
    def sell_fee(self, value):
        self._tax.sell = value

    # 거래세
    @property
    def tax(self):
        return self._tax.tax

    @tax.setter
    def tax(self, value):
        self._tax.tax = value

    # 실시간 코스피/코스닥, 개인/외인/기관 정보
    @property
    def dashboard(self):
        return self._dashboard

    def __get_load_stocks(self):
        market_codes = {
            '0': '장내 (default)',
            '10': '코스닥',
            '3': 'ELW',
            '8': 'ETF',
            '50': 'KONEX',
            '4': '무쥬얼펀드',
            '5': '신주인수권',
            '6': '리츠',
            '9': '하일럴펀드',
            '30': 'K - OTC'
        }

        code_list = []
        for m_type in market_codes:
            l_list = self.get_codelist_by_market_code(m_type)
            if len(l_list) > 0:
                code_list.extend(l_list)

        # sort by stock code
        stock_info_dict = {}
        for code in code_list:
            stock_info = make_stock_info(code, self.get_jongmok_real_name(code),
                                         self.get_jongmok_market_type(code),
                                         self.get_jongmok_state(code),
                                         self.get_jongmok_listingday(code))
            stock_info_dict[code] = stock_info
        self.__stock_list = stock_info_dict

        # sort by market type
        stock_market_dict = {}
        for code in stock_info_dict:
            stock_info = stock_info_dict[code]
            market_type = str(stock_info['market_type'])

            if not (market_type in stock_market_dict):
                stock_market_dict[market_type] = {}

            stock_market_dict[market_type][code] = {
                'name': stock_info['name'],
                'state': stock_info['state'],
                'listing-day': stock_info['listing-day']
            }
        self.__stock_market_list = stock_market_dict

    # 서버한테 받은 데이터의 갯수를 반환한다.
    def get_repeat_cnt(self, trcode, rqname):
        """
        서버한테 받은 데이터의 갯수를 반환한다.
        :param trcode:
        :param rqname:
        :return:
        """
        ret = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return INT(ret)

    # 서버한테 받은 데이터를 반환한다.
    def _get_comm_data(self, code, field_name, index, item_name):
        """
        OnReceiveTRData()이벤트가 호출될때 조회데이터를 얻어오는 함수입니다.
        이 함수는 반드시 OnReceiveTRData()이벤트가 호출될때 그 안에서 사용해야 합니다.
        :param code:
        :param field_name:
        :param index:
        :param item_name:
        :return:
        """
        ret = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", code, field_name, index, item_name)
        return ret.strip()

    # 서버한테 받은 데이터를 반환한다.
    def _get_comm_data_ex(self, code, field_name):
        """
        OnReceiveTRData()이벤트가 호출될때 조회데이터를 얻어오는 함수입니다.
        이 함수는 반드시 OnReceiveTRData()이벤트가 호출될때 그 안에서 사용해야 합니다.
        조회 수신데이터 크기가 큰 차트데이터를 한번에 가져올 목적으로 만든 차트조회 전용함수입니다.
        :param code:
        :param field_name:
        :return:
        """
        data = self.ocx.dynamicCall("GetCommDataEx(QString, QString)", code, field_name)
        return data

    # 서버로부터 실시간 데이터를 반환한다.
    def _get_real_comm_data(self, code, fid):
        """
        서버로부터 실시간 데이터를 반환한다.
        :param code: 종목코드
        :param fid: 실시간데이터 코드값
        :return:
        """
        ret = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return ret.strip()

    # 서버로부터 실시간 데이터를 리스트 형식으로 반환한다.
    def get_rq_comm_data_frame(self, sTrCode, rqName, sName, field_list, index: int = -1):
        """
        서버로부터 실시간 데이터를 리스트 형식으로 반환한다.
        :param sTrCode:
        :param rqName:
        :param sName:
        :param field_list:
        :param index:
        :return:
        """
        _results = []
        _cnt = self.get_repeat_cnt(sTrCode, rqName)
        for i in range(_cnt):
            rets = []
            for key in field_list:
                # ret = ''
                if type(key) is list:
                    ret = self._get_rq_comm_data(sTrCode, sName, i, key[0])
                    if key[1] is int:
                        ret = INT(ret)
                    elif key[1] is float:
                        ret = FLOAT(ret)
                else:
                    ret = self._get_rq_comm_data(sTrCode, sName, i, key)
                rets.append(ret)
            _results.append(rets)
            # _results.append([self._get_rq_comm_data(sTrCode, sName, i, key) for key in field_list])

        if len(_results) > 0:
            # columns
            columns = [key[0] if type(key) is list else key for key in field_list]
            if index >= 0:
                idx = [x[index] for x in _results]
                df = pd.DataFrame(data=np.array(_results), columns=columns, index=idx)
            else:
                df = pd.DataFrame(data=np.array(_results), columns=columns)

            # 형번환...
            for _key in field_list:
                if type(_key) is list:
                    if _key[1] is int:
                        df[_key[0]] = df[_key[0]].astype(int)
                    elif _key[1] is float:
                        df[_key[0]] = df[_key[0]].astype(float)
            return df
        else:
            return pd.DataFrame()

    def _get_rq_comm_data(self, sTrCode, sName, i, key):
        if type(key) is list:
            return INT(self._get_comm_data(sTrCode, sName, i, key[0]))
        elif type(key) is dict:
            return INT(self._get_comm_data(sTrCode, sName, i, key[0]))
        else:
            return str(self._get_comm_data(sTrCode, sName, i, key))

    # 서버로부터 실시간 데이터를 리스트 형식으로 반환한다.
    def get_rq_comm_data_list(self, sTrCode, rqName, field_list):
        """
        서버로부터 실시간 데이터를 반환한다.
        :param sTrCode:
        :param rqName:
        :param field_list: [["field_name_0", fid_0, ret_0,..],["field_name_1", fid_1, ret_1,..],
                                    ... ,["field_name_n", fid_n, ret_n,..]]
        :return:
        """
        cnt = 0
        for fids in field_list:
            fid = int(fids[1])
            if fid > 0:
                fids[2] = self._get_comm_data(sTrCode, rqName, cnt, fids[0])
                cnt += 1

        return cnt

    # 서버로부터 실시간 데이터를 리스트 형식으로 반환한다.
    def get_rq_comm_data_dict(self, sTrCode, rqName, field_list, realmode = False):
        """
        서버로부터 실시간 데이터를 반환한다.
        :param sTrCode:
        :param rqName:
        :param field_list: [["field_name_0", fid_0, ret_0,..],["field_name_1", fid_1, ret_1,..],
                                    ... ,["field_name_n", fid_n, ret_n,..]]
        :param realmode: if True 이면 {{'name': xxx, 'value': xxxx},,,, {'name': xxx, 'value': xxxx}}
        :return:
        """
        results = {}
        if realmode:
            for fids in field_list:
                if type(fids) is list:  # 0: key, 1: type, 2: default, 3: use ?
                    if len(fids) > 1:
                        if fids[1] is int:
                            results[fids[0]] = INT(self._get_comm_data(sTrCode, rqName, 0, fids[0]))
                        elif fids[1] is float:
                            results[fids[0]] = FLOAT(self._get_comm_data(sTrCode, rqName, 0, fids[0]))
                        else:
                            results[fids[0]] = self._get_comm_data(sTrCode, rqName, 0, fids[0])  # string
                    else:
                        results[fids[0]] = self._get_comm_data(sTrCode, rqName, 0, fids[0])
                else:
                    results[fids] = self._get_comm_data(sTrCode, rqName, 0, fids)
                # data[fid] = {
                #     'value': value,
                #     'name': RealType.REALTYPE[sRealType][fid]
                # }        else:
        else:
            for fids in field_list:
                if type(fids) is list:  # 0: key, 1: type, 2: default, 3: use ?
                    if len(fids) > 1:
                        if fids[1] is int:
                            results[fids[0]] = INT(self._get_comm_data(sTrCode, rqName, 0, fids[0]))
                        elif fids[1] is float:
                            results[fids[0]] = FLOAT(self._get_comm_data(sTrCode, rqName, 0, fids[0]))
                        else:
                            results[fids[0]] = self._get_comm_data(sTrCode, rqName, 0, fids[0])  # string
                    else:
                        results[fids[0]] = self._get_comm_data(sTrCode, rqName, 0, fids[0])
                else:
                    results[fids] = self._get_comm_data(sTrCode, rqName, 0, fids)
        return results

        
    # ex. SetInputValue("종목코드","000660")
    def set_input_value(self, fid, value):
        """
        tr 입력값을 서버 통신 전에 입력
        :param fid:
        :param value:
        :return:
        """
        self.ocx.dynamicCall("SetInputValue(QString,QString)", fid, value)

    def _comm_rq_data(self, rq_name, tr_code, b_next, screen_no) -> int:
        """
        CommRqData(QString, QString, int, QString)
        :param rq_name:
        :param tr_code:
        :param b_next:
        :param screen_no:
        :return:
        """
        return self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rq_name, tr_code, b_next, screen_no)

    def _setFavorites(self, code_list, cnt, rq_name: str, stock_opt=0, sno="500001", tr_info: transaction = None,
                      b_next="0"):
        """
        한번에 100종목을 조회할 수 있는 관심종목 조회함수인데 영웅문HTS [0130] 관심종목 화면과는 이름만 같은뿐 전혀관련이 없습니다.
        함수인자로 사용하는 종목코드 리스트는 조회하려는 종목코드 사이에 구분자';'를 추가해서 만들면 됩니다.
        :param code_list: 조회하려는 종목코드 리스트, 구분자';'를 추가해서 만들면 됩니다.
        :param cnt:  종목코드 갯수
        :param rq_name: 사용자 구분명 (관심종목명)
        :param stock_opt:  0:주식 관심종목, 3:선물옵션 관심종목
        :param sno:  화면번호
        :param tr_info
        :return:    """
        # logging.debug("즐겨찿지 설정.")
        req = req_comm(self, rq_name, tr_info, func_name=self._setFavorites.__name__)
        # req.set_callback(self.__setFavorites_callback)

        ret = self.ocx.dynamicCall("CommKwRqData(QString, int, int, int, QString, QString)", code_list, 0, cnt, stock_opt,
                               rq_name, sno)
        return req.comm_rq_data(rq_name, '', b_next, sno, error=ret)

    # def __setFavorites_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, tr_info: transaction) -> bool:
    #    # logging.debug("즐겨찾기 추가 요청: sno %s, tran_code %s" % (sScrNo, sTrCode))
    #    return True

    def set_realRegCondition(self, strScreenNo, strCodeList, strFidList, strOptType):
        """
        실시간 시세를 받으려는 종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.
        한번에 등록가능한 종목과 FID갯수는 100종목, 100개 입니다.
        :param strScreenNo: 화면번호
        :param strCodeList: 종목코드 리스트
        :param strFidList: 실시간 FID리스트
        :param strOptType: 실시간 등록 타입, 0또는 1
        :return:
        """
        # OpenAPI.SetRealReg(_T("0150"), _T("039490"), _T("9001;302;10;11;25;12;13"), "0");  // 039490종목만 실시간 등록
        # OpenAPI.SetRealReg(_T("0150"), _T("000660"), _T("9001;302;10;11;25;12;13"), "1");  // 000660 종목을 실시간 추가등록
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", strScreenNo, strCodeList, strFidList,
                         strOptType)

    def set_realRemoveCondition(self, strScreenNo, strDelCode):
        """
        실시간 시세해지 함수이며 화면번호와 종목코드를 이용해서 상세하게 설정할 수 있습니다.
        :param strScreenNo: 화면번호 또는 ALL
        :param strDelCode: 종목코드 또는 ALL
        :return:
        """
        # OpenAPI.SetRealRemove("0150", "039490");  // "0150"화면에서 "039490"종목해지
        # OpenAPI.SetRealRemove("ALL", "ALL");  // 모든 화면에서 실시간 해지
        # OpenAPI.SetRealRemove("0150", "ALL");  // 모든 화면에서 실시간 해지
        # OpenAPI.SetRealRemove("ALL", "039490");  // 모든 화면에서 실시간 해지
        self.ocx.dynamicCall("SetRealRemove(QString, QString)", strScreenNo, strDelCode)

    def set_disconnectRealData(self, sno):
        """
        시세데이터를 요청할때 사용된 화면번호를 이용하여 해당 화면번호로 등록되어져 있는
        종목의 실시간시세를 서버에 등록해지 요청합니다. 이후 해당 종목의 실시간시세는 수신되지 않습니다.
        단, 해당 종목이 또다른 화면번호로 실시간 등록되어 있는 경우 해당종목에대한 실시간시세 데이터는 계속 수신됩니다.

        :param sno: 화면번호
        :return:
        """
        ret = self.ocx.dynamicCall("DisconnectRealData(QString)", sno)
        return ret

    @pyqtSlot()
    def ShowAccountWindow(self):
        """
        login 창을 뛰운다.
        :return:
        """
        self.ocx.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")

    # 종목 이름 반환. 반환 값이 ""이면 code에 해당하는 종목 없음
    def is_stock(self, code):
        """
        종목 이름 반환. 반환 값이 ""이면 code에 해당하는 종목 없음
        :param code:
        :return:
        """
        ret = self.ocx.dynamicCall("GetMasterCodeName(QString)", [code])
        return ret

    # 주식주문
    def _order(self, gubun, scrno, accno, order_type, jongmok_cd, nqty, nprice, gb, org_orderNo):
        """
        주식 주문을 한다.
        :param gubun:        사용자 구분명
        :param scrno:       화면번호
        :param accno:       계좌번호 10자리
        :param order_type:  주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
        :param jongmok_cd:  종목코드
        :param nqty:        주문수량
        :param nprice:       금액
        :param gb:          거래구분(혹은 호가구분)은 아래 참고
        :param org_orderNo:  원주문 번호. 신규주문에는 공백, 정정(취소)주문할 원주문번호
        :return int:
        """
        req = req_comm(self, gubun, func_name=self._order.__name__)
        req.set_callback(self.__order_callback)

        ret = self.ocx.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                               [gubun, scrno, accno, order_type, jongmok_cd, nqty, nprice, gb, org_orderNo])
        return req.comm_rq_data(gubun, "", "0", scrno, error=ret)

    def __order_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, tr_info: transaction) -> bool:
        logging.debug("%s: sno %s, message '%s'" % (sRQName, sScrNo, tr_info.message))
        return True

    # 체결정보나 잔고 정보
    def get_che_jan_data(self, fid):
        ret = self.ocx.dynamicCall("GetChejanData(int)", int(fid))
        return ret.strip()

    def comm_make_rq(self, rq_name, opt: req_comm) -> transaction:
        seq = self._queue_seq_new_no()
        tr_info = opt.make_transaction(rq_name, seq, event_slot=self._trans_event_slot, wait=self.__trans_delay)
        self.__transaction_dict[rq_name] = tr_info
        return tr_info

    def _comm_wait_rq(self, opt: req_comm) -> bool:
        if opt.tr_info.push:
            opt.tr_info.event_handler_push()
            # logging.debug(f'==> {opt.tr_info.tr_name} : {opt.tr_info.diff_tran} s')
            print(f'==> {opt.tr_info.tr_name} : {opt.tr_info.diff_tran} s')
            return opt.tr_info.result
        else:
            return True

    def comm_rq_data(self, rq_name, tr_code, b_next, screen_no, opt: req_comm, error: int = None, timeout_ms: int = -1):
        result = True

        # logging.debug("%s : trcode: %s, b_next: %s, sno: %s, wait=%s"%(rqname, trcode, str(next), screen_no,
        # str(wait) ))
        if error is None:
            ret = self._comm_rq_data(rq_name, tr_code, b_next, screen_no)
            if ret == 0:
                result = self._comm_wait_rq(opt)
            else:
                logging.error(errors(ret))
                result = False

                # 계좌 비밀번호가 없을때, 비번 입력_connected창을 뛰운다.
                if ret == -301:
                    self.ShowAccountWindow()
        else:
            if error == 0:  # kiwoom_conf.py 의 error 코드값
                result = self._comm_wait_rq(opt)
            else:
                logging.error("오류 : {}".format(errors(error)))

        return result

    @property
    def is_connected(self):
        return self.__is_logon

	# 로그 아웃
    @pyqtSlot()
    def quit(self):
        self.ocx.dynamicCall("CommTerminate()")

    @pyqtSlot()
    def login(self, user: user_info):
        """
        HTS logon 시작
        :return:
        """
        self.__is_logon = False
        self.__user_info = user

        self.ocx.dynamicCall("CommConnect()")
        self._logon_event_slot.push()

        return self.__is_logon

    # def _load_cache_stocks(self):
    #     """
    #     계좌 정보를 임시 파일에서 읽어 들인다.
    #     주위, 온라인 모드와 다를 수 있음.
    #     """
    #     cache_stocks = load_json_file(self._cache_name)
    #     if self.account_num in cache_stocks:
    #         self._account_stocks = cache_stocks[self.account_num]
    #     else:
    #         self._account_stocks = {}

    #     return self._account_stocks

    def _save_cache_account_stocks(self):
        """
        계좌 정보를 임시 파일에 저장 한다.
        """
        account_detail = {code: value for code, value in self._account_stocks.items() if value['보유수량'] > 0}
        
        cache_stocks = load_json_file(self._cache_name)
        cache_stocks[self.account_num] = account_detail

        save_json_file(self._cache_name, cache_stocks)

    # ########################### EVENT FUNCTIONS ########################################

    # ----------------- 로그인 ----------------- #
    def __login_slot(self, err_code):
        """
        login event...
        :param err_code:
        :return:
        """

        self.__is_logon = False
        if err_code == 0:
            # 계정정보
            self.__get_account_info()

            # 주식리스트
            self.__get_load_stocks()

            # 로그인 ok !
            self.__is_logon = True

            logging.info("접속이 성공적으로 이루어 졌습니다.")

        user = user_info(self._user_id, '', self.__transaction_mode)
        self._logon_event_slot.pop()

        # callback
        self._app_ui.on_login(self.__is_logon, user)

    # ----------------- 사용자 정의 함수들의 결과값 ----------------- #

    def __transaction_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        """
        CommRqData 요청을 받는 이벤트 영역이다.
        :param sScrNo: 화면번호
        :param sRQName: 사용자 구분명
        :param sTrCode: TR이름
        :param sRecordName: 레코드 이름
        :param sPrevNext: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
      
		# nDataLength – 1.0.0.1 버전 이후 사용하지 않음.
		# sErrorCode – 1.0.0.1 버전 이후 사용하지 않음.
		# sMessage – 1.0.0.1 버전 이후 사용하지 않음.
		# sSplmMsg - 1.0.0.1 버전 이후 사용하지 않음.
        # 
        # :return:
        """

        if sRQName in self.__transaction_dict:
            tr_info = self.__transaction_dict[sRQName]

            print("==> transaction event : queue %d, scr_n : %s, %s, %s, %s, next %s" % (
                len(self.__transaction_dict), sScrNo, sRQName, sTrCode, sRecordName,
                sPrevNext))

            # logging.debug(f'==> {sRQName}  seq : {tr_info.seq}, sub-seq : {tr_info.seq_sub}')
            print(f'==> {sRQName}  seq : {tr_info.seq}, sub-seq : {tr_info.seq_sub}')
            if tr_info.callback is not None:
                callable(tr_info.callback(sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, tr_info))

            if tr_info.pop:
                # pop-list 정보를 삭제한다.
                tr_info.event_handler_pop()

                # remove from queue list
                self.__transaction_dict.pop(sRQName)
        else:
            logging.debug("==> transaction event(unknown) : queue %d, scr_n : %s, %s, %s, %s, next %s" % (
                len(self.__transaction_dict), sScrNo, sRQName, sTrCode, sRecordName,
                sPrevNext))

    # ----------------- messages ----------------- #

    def __receive_msg_slot(self, sScrNo, sRQNam, sTrCode, sMsg):
        """
        서버 통신 후 수신한 메지시를 알립니다.
        :param sScrNo: 화면번호
        :param sRQNam: 사용자 구분명
        :param sTrCode: TR이름
        :param sMsg: 메시지 내용
        :return:
        """
        if sRQNam in self.__transaction_dict:
            tr_info = self.__transaction_dict[sRQNam]
            tr_info.message = sMsg
        else:
            if sScrNo != '' or sRQNam != '' or sTrCode != '':
                logging.debug("=> message event(unknown) scr_n : %s, %s, %s, '%s' " % (sScrNo, sRQNam, sTrCode, sMsg))
            elif sMsg != '':
                logging.debug("%s" % sMsg)

    # ----------------- 주식 매수/매도/정정/취소 ----------------- #

    def get_tick_price(self, code, price, tick=0):
        # 코스피, 코드닥 기준으로 tick 계산
        if code in self.stocks:
            market_type = self.stocks[code]['market_type']

            tick_v = 0

            if price < 1000:
                tick_v = tick * 1
            elif price >= 1000 and price < 5000:
                tick_v = tick * 5
            elif price >= 5000 and price < 10000:
                tick_v = tick * 10
            elif price >= 10000 and price < 50000:
                tick_v = tick * 50
            elif price >= 50000 and price < 100000:
                tick_v = tick * 100
            elif price >= 100000 and price < 500000:
                tick_v = tick * (500 if market_type == '0' else 100)
            elif price >= 500000:
                tick_v = tick * (1000 if market_type == '0' else 100)

            # 틱값으로 가격 재조정함
            price += tick_v
        return price

    def set_order(self, accno: str, jongmok_cd: str, orders: str, nqty: int, n_price: int, gb: str, credit=None,
                  loandate=None, org_orderNo: str = None, text=None, rq_name='주식주문', sno='000001'):
        """
        주식을 주문한다.
        """
        name = self.get_jongmok_real_name(jongmok_cd)
        logging.debug("%s : %s(%s) => %s, 금액: %s, 수량: %s, gb: %s" % (rq_name, name, jongmok_cd, orders,
                                                                     n_price, nqty, gb))

        credit_str = ""  # 신용거래 구
        loan_date_str = ""  # 대출일
        org_orderNo_str = str("")  # 원주문번호 (취소,정정)

        ret = -1

        # 추가정보 확인
        if credit is not None:
            credit_str = credit

        if loan_date_str is not None:
            loan_date_str = loan_date_str

        if org_orderNo is not None:
            org_orderNo_str = org_orderNo

        n_price = int(n_price)
        order_type_value = order_type(orders)
        order_gb_str = order_gb(gb)

        print("accno: %s, jongmok_cd: %s, order_type_value: %s, nqty: %s, nprice %s, order_gb_str %s, credit_str %s, "
              "loan_date_str %s, org_orderNo_str %s  " % (accno, jongmok_cd,
                                                          order_type_value, nqty, n_price, order_gb_str, credit_str,
                                                          loan_date_str, org_orderNo_str))

        is_validate = [isinstance(accno, str),
                       isinstance(order_type_value, int),
                       isinstance(jongmok_cd, str),
                       isinstance(nqty, int),
                       isinstance(n_price, int),
                       isinstance(order_gb_str, str),
                       isinstance(org_orderNo_str, str)
                       ]
        if False not in is_validate:
            # 거래 안된 종목은 새로 리스트에 추가
            self._new_account_stock(code=jongmok_cd, name=name, cnt_wait=nqty)

            # 주문가능금액 수정 (신규매수: 1)
            if order_type_value == 1:
                self._trade_detail['주문가능금액'] -= int(abs(n_price) * nqty * (1.0 + self._tax.buy))

            # '시장가' 일때, 가격을 0으로 설정한다.
            if order_gb_str == "03":
                n_price = 0

            # 주문
            ret = self._order(rq_name, sno, accno, order_type_value, jongmok_cd, nqty,
                              n_price, order_gb_str, org_orderNo_str)

            # 거래 내역 로그를 출력한다.
            # 1초에 5회만 주문가능하며 그 이상 주문요청하면 에러 - 308을 리턴합니다.
            # 과부하 발생하면, 0.5초 후 함수 재 실행
            if ret == 0:
                logging.info("주문체결 요청완료 %s" % (errors(ret)))
            else:
                logging.error("====== 주문 오류 ===== %s" % (errors(ret)))
        else:
            logging.error("주문체결 데이터 타입이 잘못 : {} ".format(is_validate))

        return ret

    # 실시간 미채널요청
    def _get_che_jan_list(self, account_num, gubun="0", trade_gubun="2", code=None, che_jan="1",
                         sno="300002", tr_info: transaction = None, rq_name: str = "주식미체결요청",
                         tr_code: str = "OPT10075", b_next: str = "0"):
        """
        실시간으로 미체결 정보를 읽어서 화면에 보여준다.
        :return:
        """
        req = req_comm(self, rq_name, tr_info, func_name=self._get_che_jan_list.__name__)

        req.set_input_value("계좌번호", account_num)  # 계좌번호 = 전문 조회할 보유계좌번호
        req.set_input_value("전체종목구분", gubun)  # 전체종목구분 = 0:전체, 1:종목
        req.set_input_value("매매구분", trade_gubun)  # 매매구분 = 0:전체, 1:매도, 2:매수
        if gubun == "1" and code is not None:
            req.set_input_value("종목코드", code)  # 전문 조회할 종목코드
        req.set_input_value("체결구분", che_jan)  # 체결구분 = 0:전체, 2:체결, 1:미체결

        req.set_callback(self.__get_che_jan_list_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)

        return req.tr_info.result_data
    
    def __get_che_jan_list_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext,
                                      tr_info: transaction) -> bool:
        """
        종목코드의 일별 차트 데이터 모두를 수집한다.
        :type tr_info: object
        :param sScrNo:
        :param sRQName:
        :param sTrCode:
        :param sRecordName:
        :param sPrevNext:
        :param tr_info:
        :return:  true -> continue
        """

        field_list = ['계좌번호', 
                      '주문번호', 
                      '관리사번', 
                      '종목코드', 
                      '업무구분', 
                      '주문상태', 
                      '종목명', 
                      '주문수량',
                      '주문가격',
                      '미체결수량', 
                      '체결누계금액',
                      '원주문번호',
                      '주문구분',
                      '매매구분',
                      '시간',
                      '체결번호',
                      '체결가',
                      '체결량',
                      '현재가',
                      '매도호가',
                      '매수호가',
                      '단위체결가',
                      '단위체결량',
                      '당일매매수수료',
                      '당일매매세금',
                      '개인투자자'
                      ]


        sName = "주식미체결조회"
        df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
        tr_info.result_data = df.copy() if tr_info.result_data is None else tr_info.result_data.append(df.copy())

        # 추가 데이터가 있을 때 ?
        # if tr_info.set_req_next(isNext(sPrevNext)):
        #     # 다음 데이터를 요청한다.
        #     base_day = "0"  # df['일자'][-1]

        #     if self._app_ui.on_jong_mok_daily(code=code, daily_df=tr_info.result_data, b_next=True):
        #         self._get_jong_mok_daily(jong_mok_cd=code, base_day=base_day, tr_info=tr_info, rq_name=sRQName,
        #                                  tr_code=sTrCode, sno=sScrNo, b_next=sPrevNext)
        #     else:
        #         tr_info.set_terminate(result=False)  # 사용자 강제 종료
        # else:
        # self._app_ui.on_jong_mok_daily(code=code, daily_df=tr_info.result_data, b_next=False)
        # print(tr_info.result_data)
        return True

    # ----------------- 주문요청후 주문접수, 체결통보, 잔고통보 ----------------- #

    # 주문요청후 주문접수, 체결통보, 잔고통보를 수신할 때 마다 호출되며 GetChejanData()함수
    def on_che_jan_slot(self, sGubun, fid_dict, sotock_list):
        pass

    def __che_jan_slot(self, sGubun, nItemCnt, sFIdList):
        """
        주문요청후 주문접수, 체결통보, 잔고통보를 수신할 때 마다 호출되며 GetChejanData()함수를 이용해서 상세한 정보를 얻을수 있습니다.
        :param sGubun:      # 체결구분 접수와 체결시 '0'값, 국내주식 잔고전달은 '1'값, 파생잔고 전달은 '4'
        :param nItemCnt:
        :param sFIdList:
        :return:
        """

        print("==> che_jan_slot sGubun: %s, nItemCnt: %d, sFIdList: %s " % (sGubun, nItemCnt, sFIdList))

        fid_list = sFIdList.split(';')
        fid_dict = {str(fid): self.get_che_jan_data(fid) for fid in fid_list}

        # log ??
        for fid in fid_dict:
            print("구분[%s] FID[%s] = %s" % (sGubun, FidList.name(int(fid)), fid_dict[fid]))

        # 계좌번호 확인..
        if '9201' not in fid_dict.keys():
            logging.error("잘못된 데이터 입니다.")
            for fid in fid_dict:
                logging.debug("===> 구분[%s] FID[%s] = %s" % (sGubun, FidList.name(int(fid)), fid_dict[fid]))
            return

        # 다른 계좌번호는 탈출...
        if fid_dict['9201'] != self.account_num:
            logging.error("계좌번호가 틀림.")
            for fid in fid_dict:
                logging.debug("===> 구분[%s] FID[%s] = %s" % (sGubun, FidList.name(int(fid)), fid_dict[fid]))
            return

        for fid in fid_dict:
            # logging.debug("==> 구분[%s] FID[%s] = %s" % (sGubun, FidList.name(int(fid)), fid_dict[fid]))
            print("==> 구분[%s] FID[%s] = %s" % (sGubun, FidList.name(int(fid)), fid_dict[fid]))

        # 예수금 정보를 다시 읽어 들이게 한다..
        if sGubun == '1':  #
            # -- 매수 -- #
            # 구분[1] FID[계좌번호] = 8140961911
            # 구분[1] FID[종목코드] = A053980
            # 구분[1] FID[신용구분] = 00
            # 구분[1] FID[대출일] = 00000000
            # 구분[1] FID[종목명] = 오상자이엘
            # 구분[1] FID[현재가] = +12200
            # 구분[1] FID[보유수량] = 175
            # 구분[1] FID[매입단가] = 12150
            # 구분[1] FID[총매입가] = 2126250
            # 구분[1] FID[주문가능수량] = 175
            # 구분[1] FID[당일순매수수량] = 175
            # 구분[1] FID[매도/매수구분] = 2
            # 구분[1] FID[당일총매도손일] = -1746098
            # 구분[1] FID[예수금] = 0
            # 구분[1] FID[(최우선)매도호가)] = +12250
            # 구분[1] FID[(최우선)매수호가] = +12200
            # 구분[1] FID[기준가] = 11400
            # 구분[1] FID[손익율] = -0.46
            # 구분[1] FID[신용금액] = 0
            # 구분[1] FID[신용이자] = 0
            # 구분[1] FID[만기일] = 00000000
            # 구분[1] FID[당일실현손익(유가)] = -1746098
            # 구분[1] FID[당일신현손익률(유가)] = -0.46
            # 구분[1] FID[당일실현손익(신용)] = 0
            # 구분[1] FID[당일실현손익률(신용)] = 0.00
            # 구분[1] FID[담보대출수량] = 0
            # 구분[1] FID[924] = 0
            # 구분[1] FID[저가] = +11550
            # 구분[1] FID[전일대비기호] = 2
            # 구분[1] FID[전일대비] = +800
            # 구분[1] FID[등락율] = 7.02
            # 구분[1] FID[하한가] = -8000
            # 구분[1] FID[상한가] = +14800
            # 구분[1] FID[970] = 10

            # -- 매도 -- #
            # 구분[1] FID[계좌번호] = 8140961911
            # 구분[1] FID[종목코드] = A005390
            # 구분[1] FID[신용구분] = 00
            # 구분[1] FID[대출일] = 00000000
            # 구분[1] FID[종목명] = 신성통상
            # 구분[1] FID[현재가] = +1915
            # 구분[1] FID[보유수량] = 0
            # 구분[1] FID[매입단가] = 0
            # 구분[1] FID[총매입가] = 0
            # 구분[1] FID[주문가능수량] = 0
            # 구분[1] FID[당일순매수수량] = 0
            # 구분[1] FID[매도/매수구분] = 1
            # 구분[1] FID[당일총매도손일] = -2324033
            # 구분[1] FID[예수금] = 0
            # 구분[1] FID[(최우선)매도호가)] = +1925
            # 구분[1] FID[(최우선)매수호가] = +1915
            # 구분[1] FID[기준가] = 1880
            # 구분[1] FID[손익율] = -0.58
            # 구분[1] FID[신용금액] = 0
            # 구분[1] FID[신용이자] = 0
            # 구분[1] FID[만기일] = 00000000
            # 구분[1] FID[당일실현손익(유가)] = -2324033
            # 구분[1] FID[당일신현손익률(유가)] = -0.58
            # 구분[1] FID[당일실현손익(신용)] = 0
            # 구분[1] FID[당일실현손익률(신용)] = 0.00
            # 구분[1] FID[담보대출수량] = 0
            # 구분[1] FID[924] = 0
            # 구분[1] FID[저가] = -1860
            # 구분[1] FID[전일대비기호] = 2
            # 구분[1] FID[전일대비] = +35
            # 구분[1] FID[등락율] = 1.86
            # 구분[1] FID[하한가] = -1320
            # 구분[1] FID[상한가] = +2440
            # 구분[1] FID[970] = 10

            # 당일총매도손일, 손익율
            # if '950' in fid_dict.keys() and '8019' in fid_dict.keys():
            # self.set_my_value( "당일실현손익금", INT( fid_dict['950'] ) )
            # self.set_my_value( "총손익율", FLOAT( fid_dict['8019'] ) )
            #    pass

            # 당일 매도/매수 정보
            if '990' in fid_dict.keys():
                self._trade_detail['당일실현손익(유가)'] = INT(fid_dict['990'])
            if '991' in fid_dict.keys():
                self._trade_detail['당일신현손익률(유가)'] = FLOAT(fid_dict['991'])
            if '992' in fid_dict.keys():
                self._trade_detail['당일실현손익(신용)'] = INT(fid_dict['992'])
            if '993' in fid_dict.keys():
                self._trade_detail['당일실현손익률(신용)'] = FLOAT(fid_dict['993'])

            # 종목코드(9001)
            # 구분[1] FID[매도/매수구분] - 매수도구분(946) - 매수 : 2, 매도 : 1
            # 보유수량(930)
            # 구분[0] FID[주문상태] - 주문상태(913)  - 접수, 체결
            if '9001' in fid_dict.keys() and '946' in fid_dict.keys() and '930' in fid_dict.keys():
                # and '900' in fid_dict.keys() :
                code = fid_dict['9001'][-6:]  # 종목코드
                name = fid_dict['302']  # 종목명

                diff_cnt = 0
                trade_name = ""
                trade_mode = fid_dict['946']

                if trade_mode == "1":  # 매도
                    trade_name = "매도"
                    if code in self._account_stocks:
                        stock = self._account_stocks[code]

                        volume = stock['보유수량']

                        stock['현재가'] = INT(fid_dict['10'])
                        stock['매입가'] = INT(fid_dict['931'])  # 매입단가
                        stock['매입금액'] = INT(fid_dict['932'])  # '총매입가'
                        stock['보유수량'] = INT(fid_dict['930'])
                        stock['주문가능수량'] = INT(fid_dict['933'])

                        # '예수금+2' 과 '주문가능금액' 을 계산한다.
                        diff_cnt = volume - stock['보유수량']
                        if diff_cnt > 0:
                            sell_amount, fee, tax = self._calculate_tax(code, abs(stock['매입가']), diff_cnt,
                                                                        stock['매입금액'], stock['현재가'])
                            self._trade_detail['예수금+2'] += (sell_amount - (fee + tax))
                            self._trade_detail['주문가능금액'] = self._trade_detail['예수금+2']

                elif trade_mode == "2":  # 매수'
                    trade_name = "매수"
                    price = INT(fid_dict['10'])

                    if code in self._account_stocks:
                        stock = self._account_stocks[code]

                        volume = stock['보유수량']

                        stock['현재가'] = price
                        stock['매입가'] = INT(fid_dict['931'])
                        stock['매입금액'] = INT(fid_dict['932'])
                        stock['보유수량'] = INT(fid_dict['930'])
                        stock['주문가능수량'] = INT(fid_dict['933'])
                        diff_cnt = stock['보유수량'] - volume

                    else:
                        stock = self._new_account_stock(code=code, name=name, price=price,
                                                        buy=abs(INT(fid_dict['931'])),
                                                        buy_total=INT(fid_dict['932']),
                                                        cnt=INT(fid_dict['930']),
                                                        sell_cnt=INT(fid_dict['933']),
                                                        cnt_wait=INT(fid_dict['933']) if '933' in fid_dict else 0,
                                                        gu_bun=INT(fid_dict['917']) if '917' in fid_dict else '00')
                        diff_cnt = stock['보유수량']

                    # '예수금+2' 을 계산한다.
                    self._trade_detail['예수금+2'] -= int(diff_cnt * abs(price) * (1.0 + self._tax.buy))
                    if '미체결수량' in stock and stock['미체결수량'] == 0:
                        self._trade_detail['주문가능금액'] = self._trade_detail['예수금+2']
                # if (매도/매수) ?

                # 매수/매도 일때만 마무리 처리
                self.update_account_detail(code=code)  # 결과 다시 계산
                if (trade_mode == "1" or trade_mode == "2") and diff_cnt > 0:
                    self._app_ui.on_trading_finished(code, name, diff_cnt, trade_name)
                    self._save_cache_account_stocks()

        elif sGubun == '0':
            # -- 매수 -- #
            # 구분[0] FID[계좌번호] = 8140961911
            # 구분[0] FID[주문번호] = 0200780
            # 구분[0] FID[관리자사번] =
            # 구분[0] FID[종목코드] = A053980
            # 구분[0] FID[주문업무분류] = JJ
            # 구분[0] FID[주문상태] = 체결
            # 구분[0] FID[종목명] = 오상자이엘
            # 구분[0] FID[주문수량] = 409
            # 구분[0] FID[주문가격] = 12150
            # 구분[0] FID[미체결수량] = 234
            # 구분[0] FID[체결누계금액] = 2126250
            # 구분[0] FID[원주문번호] = 0000000
            # 구분[0] FID[주문구분] = +매수
            # 구분[0] FID[매매구분] = 보통
            # 구분[0] FID[매도수구분] = 2
            # 구분[0] FID[주문/체결시간] = 142257
            # 구분[0] FID[체결번호] = 731195
            # 구분[0] FID[체결가] = 12150
            # 구분[0] FID[체결량] = 175
            # 구분[0] FID[현재가] = +12200
            # 구분[0] FID[(최우선)매도호가)] = +12250
            # 구분[0] FID[(최우선)매수호가] = +12200
            # 구분[0] FID[단위체결가] = 12150
            # 구분[0] FID[단위체결량] = 175
            # 구분[0] FID[당일매매수수료] = 7440
            # 구분[0] FID[당일매매세금] = 0
            # 구분[0] FID[거부사유] = 0
            # 구분[0] FID[화면번호] = 0000
            # 구분[0] FID[터미널번호] = 6406095
            # 구분[0] FID[신용구분(실시간 체결용)] = 00
            # 구분[0] FID[대출일(실시간 체결용)] = 00000000
            # 구분[0] FID[949] = 0
            # 구분[0] FID[저가] = +11550
            # 구분[0] FID[969] = 0
            # 구분[0] FID[819] = 0

            # -- 매도 -- #
            # 구분[0] FID[계좌번호] = 8140961911
            # 구분[0] FID[주문번호] = 0216959
            # 구분[0] FID[관리자사번] =
            # 구분[0] FID[종목코드] = A005390
            # 구분[0] FID[주문업무분류] = JJ
            # 구분[0] FID[주문상태] = 체결
            # 구분[0] FID[종목명] = 신성통상
            # 구분[0] FID[주문수량] = 2566
            # 구분[0] FID[주문가격] = 0
            # 구분[0] FID[미체결수량] = 0
            # 구분[0] FID[체결누계금액] = 4913890
            # 구분[0] FID[원주문번호] = 0000000
            # 구분[0] FID[주문구분] = -매도
            # 구분[0] FID[매매구분] = 시장가
            # 구분[0] FID[매도수구분] = 1
            # 구분[0] FID[주문/체결시간] = 145010
            # 구분[0] FID[체결번호] = 778840
            # 구분[0] FID[체결가] = 1915
            # 구분[0] FID[체결량] = 2566
            # 구분[0] FID[현재가] = +1915
            # 구분[0] FID[(최우선)매도호가)] = +1925
            # 구분[0] FID[(최우선)매수호가] = +1915
            # 구분[0] FID[단위체결가] = 1915
            # 구분[0] FID[단위체결량] = 2566
            # 구분[0] FID[당일매매수수료] = 17190
            # 구분[0] FID[당일매매세금] = 12284
            # 구분[0] FID[거부사유] = 0
            # 구분[0] FID[화면번호] = 0000
            # 구분[0] FID[터미널번호] = 0214003
            # 구분[0] FID[신용구분(실시간 체결용)] = 00
            # 구분[0] FID[대출일(실시간 체결용)] = 00000000
            # 구분[0] FID[949] = 3
            # 구분[0] FID[저가] = -1860
            # 구분[0] FID[969] = 0
            # 구분[0] FID[819] = 0

            # -- 접수 -- #
            # 구분[0] FID[계좌번호] = 8158752111
            # 구분[0] FID[주문번호] = 0063090
            # 구분[0] FID[관리자사번] =
            # 구분[0] FID[종목코드] = A001040
            # 구분[0] FID[주문업무분류] = JJ
            # 구분[0] FID[주문상태] = 접수
            # 구분[0] FID[종목명] = CJ
            # 구분[0] FID[주문수량] = 1
            # 구분[0] FID[주문가격] = 91400
            # 구분[0] FID[미체결수량] = 1
            # 구분[0] FID[체결누계금액] = 0
            # 구분[0] FID[원주문번호] = 0000000
            # 구분[0] FID[주문구분] = +매수
            # 구분[0] FID[매매구분] = 보통
            # 구분[0] FID[매도수구분] = 2
            # 구분[0] FID[주문/체결시간] = 095451
            # 구분[0] FID[체결번호] =
            # 구분[0] FID[체결가] =
            # 구분[0] FID[체결량] =
            # 구분[0] FID[현재가] = 91400
            # 구분[0] FID[(최우선)매도호가)] = +91500
            # 구분[0] FID[(최우선)매수호가] = 91400
            # 구분[0] FID[단위체결가] =
            # 구분[0] FID[단위체결량] =
            # 구분[0] FID[당일매매수수료] = 0
            # 구분[0] FID[당일매매세금] = 0
            # 구분[0] FID[거부사유] = 0
            # 구분[0] FID[화면번호] = 0000
            # 구분[0] FID[터미널번호] = 5402075
            # 구분[0] FID[신용구분(실시간 체결용)] = 00
            # 구분[0] FID[대출일(실시간 체결용)] = 00000000
            # 구분[0] FID[949] = 0
            # 구분[0] FID[저가] = 91400
            # 구분[0] FID[969] = 0
            # 구분[0] FID[819] = 0

            # 당일거래한 종목을 메모리에 저장한다.
            # 주문상태:체결, 매도수구분(907):매수 2, 매도 1
            # 구분[0] FID[주문상태] - 주문상태(913)  - 접수, 체결, 학인
            if '913' in fid_dict.keys():
                order_mode = fid_dict['913']  # 주문상태
                code = fid_dict['9001'][-6:]  # 종목코드
                name = fid_dict['302']  # 종목명

                # 종목 확인
                cnt_wait = INT(fid_dict['902']) if '902' in fid_dict else 0
                stock = self._new_account_stock(code, name, cnt_wait=cnt_wait)

                # 미체결수량
                stock["미체결수량"] = cnt_wait

                if order_mode == "체결":  # 주문 접수후 체결
                    # 매도수구분(907)
                    if '907' in fid_dict:
                        trade_mode = fid_dict['907']

                        # 매수
                        if trade_mode == "2":
                            tr_time = fid_dict['908']  # 주문/체결시간['908'] : HHMMDD
                            today_str = dt.datetime.now().strftime('%Y-%m-%d')
                            tran_date = '%s %s:%s:%s' % (today_str, tr_time[:2], tr_time[2:4], tr_time[4:6])
                            if DEF_USER_RESERVED in stock:
                                stock[DEF_USER_RESERVED][DEF_TRANDATE] = tran_date # now2string()
                            else:
                                stock[DEF_USER_RESERVED] = {DEF_TRANDATE:tran_date}
                        # 매도
                        # if trade_mode == "1":
                        #    pass

                elif order_mode == "접수":  # 주문 접수
                    pass
                elif order_mode == "확인":  # 취소거래
                    pass
            # if '913' ?

    # ----------------- 실시간 데이터 ----------------- #

    def _get_real_comm_data_result(self, code, sRealType) -> dict:
        """
        실시간 데이터를 받아온다.
        :param code:
        :param sRealType:
        :return:
        """

        data = {}
        if sRealType in RealType.REALTYPE:
            for fid in RealType.REALTYPE[sRealType]:
                value = self._get_real_comm_data(code, fid)
                data[fid] = {
                    'value': value,
                    'name': RealType.REALTYPE[sRealType][fid]
                }
        return data

    def __realtime_slot(self, sTrCode, sRealType, sRealData):
        """
        실시간 데이터 수신할때마다 호출되며 SetRealReg()함수로 등록한 실시간 데이터도 이 이벤트로 전달됩니다.
        GetCommRealData()함수를 이용해서 실시간 데이터를 얻을수 있습니다.
        :param sTrCode: 거래 코드
        :param sRealType: 리얼타입
        :param sRealData: 실시간 데이터 전문
        :return:
        """
        code = sTrCode.strip()
        name = self.get_jongmok_real_name(code)

        # 실시간 데이터를 받아온다
        data = self._get_real_comm_data_result(code, sRealType)
        if sRealType in self.__real_data_dict:
            # 시세정보, 실시간, 프로그램 매매시에는 실시간 현재가와 거래량 수정
            if code in self._account_stocks and \
                    (sRealType == KEY_REALTIME_CHEJAN
                    or sRealType == KEY_REALTIME_SISE 
                    or sRealType == KEY_REALTIME_PROGRAM):
                v = {x['name']: x['value'] for x in data.values()}
                # print( "==> 체결 정보 : %s(%s) %s" % (name, code, v) )

                self._account_stocks[code]['현재가'] = INT(v['현재가'])
                self._account_stocks[code]['거래량'] = INT(v['거래량'])

                # 고가,저가 수정
                self.check_traninfo(code)

                # 수익률 계산
                self.calculate_tax(self._account_stocks, code)
            else:
                v = {x['name']: x['value'] for x in data.values()}

            # 실시간 데이터가 없는 경우, 실시간 데이터 전문으로 대체한다.
            callable(self.__real_data_dict[sRealType](sRealType, code, name, v if len(v) > 0 else sRealData))
        else:
            self._app_ui.on_realtime(sRealType, code, name, data, sRealData)
            
        # - old code -
        # if len(data) > 0:
        #     if sRealType in self.__real_data_dict:
        #         # 시세정보, 실시간, 프로그램 매매시 실시간 현재가와 거래량 수정
        #         if code in self._account_stocks and \
        #                 (sRealType == KEY_REALTIME_CHEJAN
        #                  or sRealType == KEY_REALTIME_SISE 
        #                  or sRealType == KEY_REALTIME_PROGRAM):
        #             v = {x['name']: x['value'] for x in data.values()}
        #             # print( "==> 체결 정보 : %s(%s) %s" % (name, code, v) )

        #             self._account_stocks[code]['현재가'] = INT(v['현재가'])
        #             self._account_stocks[code]['거래량'] = INT(v['거래량'])

        #             # 고가,저가 수정
        #             self.check_traninfo(code)

        #             # 수익률 계산
        #             self.calculate_tax(self._account_stocks, code)
        #         # callback...
        #         callable(self.__real_data_dict[sRealType](sRealType, code, name, data))
        #     else:
        #         self._app_ui.on_realtime(sRealType, code, name, data)
        # else:
        #     print("==> real-data_slot %s : %s(%s)" % (sRealType, name, code))

    def __realtime_hoga_trade_slot(self, real_type, code, name, data):
        """ 주식우선호가 """
        logging.debug(f'==> 주식우선호가 - 거래래: {name}({code}) : {data}')
        """
        :param code:
        :param jongmok_name:
        :param data_list:
        :return:

         # 실시간 호가창 (전체)
        elif (sRealType == "주식호가잔량"):
            self.auto_trading_hoga(code, jongmok_name, key_list)  # 호가 매매
            self._app_ui.disp_real_hoga(code, jongmok_name, key_list)  # 호가창에 출력

        """
        pass

    def __realtime_overtime_hoga_slot(self, real_type, code, name, data):
        """" 주식시간외호가 """
        logging.debug(f'==> 주식호가잔량: {name}({code}) : {len(data)} s')
        for data in data:
            v = data[data]
            if v.value != '':
                print('{} : {} - {}'.format(data, v['value'], v['name']))

    # 2005년 5월 30일부터 야간 증시(ECN)이 폐지됨
    def __realtime_ENC_hoga_slot(self, real_type, code, name, data):
        """ ECN주식호가잔량 """
        pass

    def __realtime_ENC_sise_slot(self, real_type, code, name, data):
        """ ECN주식시세 """
        pass

    def __realtime_ENC_che_jan_slot(self, real_type, code, name, data):
        """ ECN주식체결 """
        pass

    def __realtime_guess_che_jan_slot(self, real_type, code, name, data):
        """ 주식예상체결 """

        """
        data = {}
        data['종목코드'] = code  # 종목코드
        data['종목명'] = jongmok_name  # 종목코드
        data['현재가'] = INT(key_list[1][2])  # 현재가
        data['전일대비'] = INT(key_list[2][2])  # 전일대비
        data['등락율'] = FLOAT(key_list[3][2])  # 등락율
        data['거래량'] = INT(key_list[5][2])  # 거래량
        data['대비기호'] = key_list[6][2]  # 전일대비기호
        # self._app_ui.print( "==> %s  : %s(%s), %s, %s" % (sRealType, jongmok_name, code, str(key_list[1][2]), str(key_list[3][2])) )

        ## 변경사항 화면에 출력(가상 데이터는 보유 자산에 영향이 없음)
        self.update_ui_sise(sRealType, code, jongmok_name, data, real_time=False)
        """
        pass

    def __realtime_jong_mok_slot(self, real_type, code, name, data):
        """ 주식종목정보 """
        pass

    def __realtime_overtime_slot(self, real_type, code, name, data):
        """ 시간외종목정보 """
        pass

    def __realtime_trader_slot(self, real_type, code, name, data):
        """ 주식거래원 """
        pass

    def __realtime_today_trader_slot(self, real_type, code, name, data):
        """ 주식당일거래원 """
        pass

    # 실시간 업종지수
    def __realtime_industry_idx_slot(self, real_type, code, name, data):
        """ 
        실시간 업종지수 
        """
        #
        #self._dashboard = {
        #    '코스피': item.copy(),
        #    '코스피200': item.copy(),
        #    '코스닥': item.copy(),
        #    '코스닥100': item.copy()
        #}

        keys = {'001': '코스피', '101': '코스닥', '201': '코스피200', '138': '코스닥100'}
        name = keys[code] if code in keys else ''

        #item  = {
        #    item = {'현재가': 0, '등락율': 0.0, '전일대비': 0, '개인순매수': 0, '외인순매수': 0,
        #        '기관순매수': 0}  # 0-현재가, 1-등락율, 2-전일대비, 3-개인순매수, 4-외인순매수, 5-기관순매수
        #}
        if len(name) > 0:
            self._dashboard[name]['현재가'] = data['현재가']
            self._dashboard[name]['등락율'] = data['등락율']
            self._dashboard[name]['전일대비'] = data['전일대비']
            # self._dashboard[name]['현재가'] = data['현재가']

        self._app_ui.on_realtime_jisu(code, name, data)

    def __realtime_guess_industry_idx_slot(self, real_type, code, name, data):
        """ 
        실시간 예상업종지수 
        """
        keys = {'001': '코스피', '101': '코스닥', '201': '코스피200', '138': '코스닥100'}
        name = keys[code] if code in keys else ''

        #item  = {
        #    item = {'현재가': 0, '등락율': 0.0, '전일대비': 0, '개인순매수': 0, '외인순매수': 0,
        #        '기관순매수': 0}  # 0-현재가, 1-등락율, 2-전일대비, 3-개인순매수, 4-외인순매수, 5-기관순매수
        #}
        if len(name) > 0:
            self._dashboard[name]['현재가'] = data['현재가']
            self._dashboard[name]['등락율'] = data['등락율']
            self._dashboard[name]['전일대비'] = data['전일대비']
            # self._dashboard[name]['현재가'] = data['현재가']

    def __realtime_industry_updown_slot(self, real_type, code, name, data):
        keys = {'001': '코스피', '101': '코스닥', '201': '코스피200', '138': '코스닥100'}
        name = keys[code] if code in keys else ''  
        self._app_ui.on_realtime_jisu_updown(code, name, data)  

    def __realtime_time_slot(self, real_type, code, name, data):
        # self._app_ui.print("==> %s  : %s(%s) :  %s" %
        # (sRealType, jongmok_name, code, self.real_comm_data_to_str(key_list)))
        print("==> kiwoom_api : real-data_slot %s : %s(%s), 장운영구분: %s, 체결시간: %s, 장시작예상잔여시간: %d" % (real_type, name, code, data["장운영구분"], data["체결시간"], int(data["장시작예상잔여시간"])))

    # ----------------- 조건 검색 ----------------- #

    def get_realConditionFunctionLoad(self):
        """
        사용자 조건검색 목록을 서버에 요청합니다. 조건검색 목록을 모두 수신하면 OnReceiveConditionVer()이벤트가 호출됩니다.
        조건검색 목록 요청을 성공하면 1, 아니면 0을 리턴합니다.
        :return:
        """
        self.ocx.dynamicCall("GetConditionLoad()")
        self._case_condition_slot.push()

    def set_realCondition(self, strConditionName, nIndex, sno="80001", nSearch=1):
        """
        서버에 조건검색을 요청하는 함수로 맨 마지막 인자값으로 조건검색만 할것인지 실시간 조건검색도 할 것인지를 지정할 수 있습니다.
        리턴값 1이면 성공이며, 0이면 실패입니다.
        청한 조건식이 없거나 조건명 인덱스와 조건식이 서로 안맞거나 조회횟수를 초과하는 경우 실패하게 됩니다.
        :param strConditionName: 조건식 이름
        :param nIndex: 조건명 인덱스
        :param nSearch: 조회구분, 0:조건검색, 1:실시간 조건검색
        :param sno
        :return:
        """

        # "0^조건식1;3^조건식1;8^조건식3;23^조건식5"일때 조건식3을 검색
        # long lRet = SendCondition("0156", "조건식3", 8, 1);
        nIndex = int(nIndex)
        self.ocx.dynamicCall("SendCondition(QString, QString, int, int)", sno, strConditionName, nIndex, nSearch)

    def set_realStopCondition(self, strConditionName, nIndex, strScrNo="80001"):
        """
        조건검색을 중지할 때 사용하는 함수입니다.
        :param strConditionName: 조건식 이름
        :param nIndex: 조건명 인덱스
        :param strScrNo: 화면변호
        :return:
        """
        # "0^조건식1;3^조건식1;8^조건식3;23^조건식5"일때 조건식3을 검색
        # long lRet = SendCondition("0156", "조건식3", 8, 1);
        nIndex = int(nIndex)
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", strScrNo, strConditionName, nIndex)

    # 조건별 검색 Events
    def __receiveCondition_slot(self, lRet, sMsg):
        """
        # 용자 조건식요청에 대한 응답을 서버에서 수신하면 호출되는 이벤트입니다.

        :param lRet: 호출 성공여부, 1: 성공, 나머지 실패
        :param sMsg: 호출결과 메시지
        """

        condition_dict = {}
        if int(lRet) == 1:
            # 조건식 하나는 조건명 인덱스와 조건식 이름은 '^'로 나뉘어져 있으며 각 조건식은 ';'로 나뉘어져 있습니다.
            # 서버에서 수신한 사용자 조건식을 조건명 인덱스와 조건식 이름을 한 쌍으로 하는 문자열들로 전달합니다.
            # 조건식 하나는 조건명 인덱스와 조건식 이름은 '^'로 나뉘어져 있으며 각 조건식은 ';'로 나뉘어져 있습니다.
            # 이 함수는 반드시 OnReceiveConditionVer()이벤트에서 사용해야 합니다.
            # 예) '003^정배열-급등주;006^단타-실시간;008^단타-오전장;009^단타-눌림목;001^스윙-MACD지표;'
            name_str = str(self.ocx.dynamicCall("GetConditionNameList()"))  # 초기화 되면 검색 리스트를 요청한다.

            # 분할 처리
            name_list = name_str.split(";")
            logging.debug('=> 조건검색 : %s' % name_str)

            for names in name_list:
                if len(names) > 0:
                    tmp = names.split('^')
                    condition_dict[tmp[0]] = tmp[1]

            # 딕셔너리를 키 값 기준으로 정렬된 튜플 리스트로 변환
            # sorted_tuples = sorted(condition_dict.items(), key=lambda x: x[0])

            # 정렬된 튜플 리스트를 다시 딕셔너리로 변환
            # condition_dict =  {k: v for k, v in sorted_tuples}

        self._case_condition_slot.pop()
        self._app_ui.on_conditions_list(condition_dict)

    def __receiveTrCondition_slot(self, sScrNo, strCodeList, strConditionName, nIndex, nNext):
        """
        # 조건검색 요청으로 검색된 종목코드 리스트를 전달하는 이벤트입니다. 종목코드 리스트는 각 종목코드가 ';'로 구분되서 전달됩니다.
        :param sScrNo: 화면번호
        :param strCodeList: 종목코드 리스트
        :param strConditionName: 조건식 이름
        :param nIndex: 조건명 인덱스
        :param nNext: 연속조회 여부
        :return:
        """
        index = int(nIndex)
        strCode_List = strCodeList.split(';')
        for code in strCode_List:
            if len(code) > 0:
                name = self.get_jongmok_real_name(code)
                print('==> %s(%s) : type %s, name : %s, idx %d ' % (name, code, 'L', strConditionName, index))
                self._app_ui.on_conditions_stocks('L', code, name, strConditionName, index, sScrNo)

    def __receiveRealCondition_slot(self, strCode, strType, strConditionName, strConditionIndex):
        """
        # 실시간 조건검색 요청으로 신규종목이 편입되거나 기존 종목이 이탈될때 마다 호출됩니다.
        :param strCode: 종목코드
        :param strType: 이벤트 종류, "I":종목편입, "D", 종목이탈
        :param strConditionName: 조건식 이름
        :param strConditionIndex: 조건명 인덱스
        :return:
        """
        code = strCode.strip()
        name = self.get_jongmok_real_name(code)
        index = int(strConditionIndex)
        print('==> %s(%s) : type %s, name : %s, idx %d ' % (name, code, strType, strConditionName, index))
        self._app_ui.on_conditions_stocks(strType, code, name, strConditionName, index)

    # ----------------- 사용자 정의 Transaction 함수들  ----------------- #

    def _get_account_detail(self, sno: str, tr_info: transaction = None, rq_name="계좌수익률요청", tr_code="OPT10085",
                            b_next="0"):  # pandas.DataFrame:

        """
        계좌의 보유주식별로 수익율을 읽어 들인다.
        :param tr_info:
        :param tr_code:
        :param rq_name:
        :param sno:
        :param b_next:
        :return:
        """
        # logging.debug("계좌의 수익율을 구한다.")
        req = req_comm(self, rq_name, tr_info, func_name=self._get_account_detail.__name__)

        req.set_input_value("계좌번호", self.account_num)

        req.set_callback(self.__get_account_detail_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)
        return ret

    def _new_account_stock(self, code, name, price=0, buy=0, buy_total=0, cnt=0, sell_cnt=0, cnt_wait=0, gu_bun='00'):
        """ 신규 주식이 추가인지... """
        if code not in self._account_stocks:
            self._account_stocks[code] = {
                "종목명": name,
                "현재가": price,
                "매입가": buy,
                "매입금액": buy_total,
                "보유수량": cnt,
                "주문가능수량": sell_cnt,
                "미체결수량": cnt_wait,
                "당일매도손익": 0,
                "신용구분": gu_bun,
                "평가금액": 0,
                "평가손익": 0,
                "수익률": 0,
                "당일매매수수료": 0,
                "당일매매세금": 0,
                "결재잔고": 0,
                "정산가능수량": 0,
                "손실차액": 0,
                # "일자": dt.datetime.now().strftime("%Y%m%d%H%M%s"),
                "신용금액": 0,
                "신용이자": 0,
                "만기일": 0,
                "수수료": 0,
                "매도금액": 0,
                "세금": 0,
            }

            self.check_traninfo(code)
            self._app_ui.on_new_account_stock(code, name)

        return self._account_stocks[code]

    def _set_high_low(self, code, closed, cnt): 
        """
        보유수량이 0보다 클때, 고가,저가를 입력한다.
        :param code: 코드
        :param closed: 종가 또는 현재가
        :param cnt: 보유수량
        """
        if code in self._account_stocks:
            if cnt > 0:
                # '고가' 가 있는지 확인
                if DEF_TRAN_HIGH not in self._account_stocks[code][DEF_USER_RESERVED]:
                    self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_HIGH] = closed
                else:
                    if self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_HIGH] < closed:
                        self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_HIGH] = closed

                # '저가' 가 있는지 확인
                if DEF_TRAN_LOW not in self._account_stocks[code][DEF_USER_RESERVED]:
                    self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_LOW] = closed
                else:
                    if self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_LOW] > closed \
                        or self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_LOW] <= 0:            # 혹시나 ? '저가' 버그 수정
                        self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_LOW] = closed
            else:
                if DEF_USER_RESERVED in self._account_stocks[code]:
                    if DEF_TRAN_HIGH in self._account_stocks[code][DEF_USER_RESERVED]:
                        del (self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_HIGH])
                    if DEF_TRAN_LOW in self._account_stocks[code][DEF_USER_RESERVED]:
                        del (self._account_stocks[code][DEF_USER_RESERVED][DEF_TRAN_LOW])


    def check_traninfo(self, code, account_userinfo = None):
        """
        사용자 정보를 추가 사용한다.
        """
        closed = abs(self._account_stocks[code]['현재가']) if '현재가' in self._account_stocks[code] else 0
        cnt = self._account_stocks[code]['보유수량'] if '보유수량' in self._account_stocks[code] else 0
        if (account_userinfo is not None) and \
           (code in account_userinfo) and (DEF_USER_RESERVED in account_userinfo[code]):
            self._account_stocks[code][DEF_USER_RESERVED] = account_userinfo[code][DEF_USER_RESERVED]

            if DEF_TRANDATE not in self._account_stocks[code][DEF_USER_RESERVED]:
                self._account_stocks[code][DEF_USER_RESERVED][DEF_TRANDATE] = now2string()
            self._set_high_low(code, closed, cnt)
        else:
            if DEF_USER_RESERVED in self._account_stocks[code]:
                # 매입일자 확인
                if DEF_TRANDATE not in self._account_stocks[code][DEF_USER_RESERVED]:
                    self._account_stocks[code][DEF_USER_RESERVED][DEF_TRANDATE] = now2string()
                self._set_high_low(code, closed, cnt)
            else:
                self._account_stocks[code][DEF_USER_RESERVED] = {
                    DEF_TRANDATE : now2string(),
                    DEF_TRAN_HIGH : closed,
                    DEF_TRAN_LOW : closed,
                }

    def __get_account_detail_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext,
                                      tr_info: transaction) -> bool:
        """
        보유종목에 대한 리스트를 얻어온다.
        :param sScrNo:
        :param sRQName:
        :param sTrCode:
        :param sRecordName:
        :param sPrevNext:
        :param tr_info:
        :return:  true -> continue
        """

        # logging.debug("%s(%s) 일봉데이터 요청, 데이터 일수 %d, 기준일 %s"% (jongmok_name, code, cnt, self.base_daily))
        field_list = ["종목코드",  # 0
                      "종목명",  # 1
                      ["현재가", int],  # 'topic', type, default ?
                      ["매입가", int],  # 3
                      ["매입금액", int],  # 4
                      ["보유수량", int],  # 5
                      ["주문가능수량", int],
                      ["당일매도손익", int],  # 6
                      ["미체결수량", int],
                      "신용구분",  # 7
                      ["평가금액", int],  # 8
                      ["평가손익", int],  # 9
                      ["수익률", float],  # 10
                      ["당일매매수수료", int],  # 11
                      ["당일매매세금", int],  # 12
                      ["결재잔고", int],  # 13
                      ["정산가능수량", int],  # 14
                      "일자",  # 15
                      ["신용금액", int],
                      ["신용이자", float],
                      "만기일",
                      ["수수료", int],
                      ["매도금액", int],
                      ["세금", int],
                      ["손실차액", int],
                      ]

        sName = "계좌수익률"

        # 보유수량이 0 이상인 데이터만...
        df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
        if len(df) > 0:
            df['주문가능수량'] = df['보유수량']  # 주문가능 수량이 서버에서 안내려온다.
            tr_info.result_data = df.copy() if tr_info.result_data is None else tr_info.result_data.append(df.copy())

        # 추가 데이터가 있을 때 ?
        if tr_info.set_req_next(isNext(sPrevNext)):
            # 다음 데이터를 요청한다.
            self._get_account_detail(sno=sScrNo, tr_info=tr_info, rq_name=sRQName, tr_code=sTrCode, b_next=sPrevNext)
        else:
            if tr_info.result_data is not None:
                self._account_stocks = tr_info.result_data.set_index('종목코드').T.to_dict()
                # print_df(tr_info.result_data)

                tmp = {c: v for c, v in self._account_stocks.items() if v['보유수량'] > 0}
                # self._account_stocks = tmp

                # 캐쉬에 저장된 다른 사용자 정보를 읽어 들인다.
                cache_stocks = load_json_file(self._cache_name)
                account_detail = cache_stocks[self.account_num] if self.account_num in cache_stocks else None
                for code in self._account_stocks:
                    self.check_traninfo(code, account_detail)

                print("==> 거래 주식 {} 주식 중 {} 주식을 보유".format(len(self._account_stocks), len(tmp)))
                logging.debug("==> 거래 주식 {} 주식 중 {} 주식을 보유".format(len(self._account_stocks), len(tmp)))
            else:
                self._account_stocks = {}
                logging.debug("==> 주식을 보유 {}".format(len(self._account_stocks)))

            self.update_account_detail()
        return True

    def update_account_detail(self, code=None):
        self.calculate_tax(self._account_stocks, code=code)  # 세금 계산함
        self._app_ui.on_account_detail(self.account_num, self._account_stocks, code=code)        
        self._save_cache_account_stocks()           # 최신 소유한 주식정보를 저장한다.

    def _calculate_tax(self, code, buy, buy_cnt, buy_amount, price):
        """
        ------------------
          주식에 대한 계산..
        ------------------

        1. 수수료
        +----------------+----------------+--------------------+----------------------------+-------+------------+
        | 구분            | HTS/WTS/홈페이지 | 영웅문(S+)/카마오증권   | 증권통/유팍스/영웅문(+)/키움T스톡 | ARS   | 반대매매/청산 |
        +----------------+----------------+--------------------+----------------------------+-------+------------|
        | 거래소/코스탁/ETF | 0.15%          | 0.15%              | 0.20%                      | 0.20% | 0.45%      |
        | ELW            | 0.20%          | 0.20%              | 0.20%                      | 0.20% | 0.45%      |
        | K-OTC          | 0.20%          | 0.20%              |                            | 0.40% | 0.5%       |
        +----------------+----------------+--------------------+----------------------------+-------+------------+

        2. 세금
        +------------+------------------------------------+
        | 구분        |               세금                   |
        +------------+-------------------------------------+
        | 거래소 매매   | 매도금액 x (거래세 0.08% + 농특세 0.15%) |
        | 코스탁 매매   | 매도금액 x 거래세 0.23%                |
        | K-OTC 매매  | 매도금액 x 거래세 0.23%                 |
        +------------+------------------------------------+

        3. 위탁 증거금 징수율
        +-----------------------------------------+------------------------------------+
        |     증거금 20%종목 	                       | 20%(대용금액 + 현금/재사용)            |
        +-----------------------------------------+------------------------------------+
        |     증거금 30%종목 	                       | 30%(대용금액 + 현금/재사용)            |
        +-----------------------------------------+------------------------------------+
        |     증거금 40%종목 	                       | 40%(대용금액 + 현금/재사용)            |
        +-----------------------------------------+------------------------------------+
        |     증거금 50%종목	                       | 50%(대용금액 + 현금/재사용)            |
        +-----------------------------------------+------------------------------------+
        |     증거금 60%종목 	                       | 60%(대용금액 + 현금/재사용)            |
        +-----------------------------------------+------------------------------------+
        |     이상급등/관리/투자유의/정리매매/신주인수권증권/ |                                   |
        |     당사가 지정한 증거금 100% 징수종목         	|  현금/재사용 100%                     |
        +-----------------------------------------+------------------------------------+
        |     K-OTC / ELW	현금/재사용 100%
        +-----------------------------------------+------------------------------------+


        . 증거금률 지정 기준은 해당 종목의 시장(거래소, 코스닥, ETF 등)이 아니라 종목의 특성에 따라 당사가 기준을 정함
        . 증거금률 100% 종목은 K-OTC 종목을 제외하고 매도대금 범위내에서 재매수 가능
        . 미성년자, 부실거래자, 연체 등 채무불이행자 및 이에 준하는 자(면책결정자, 신용회복자 등)는 상기 증거금 징수율과
           상관없이 당사 기준에 따라 100%증거금이 적용됩니다.
        . 미수 이자율 : 연19%
        """
        if buy_cnt > 0 and buy > 0:  # 보유수량, 매입가 로 데이터 검증(간혹 매입가, 매입금액이 0으로 들어오는 데이터 있음)
            sell_amount = abs(price) * buy_cnt

            # 나머지는 올림처리.
            buy_fee = int(buy_amount * self._tax.buy)  # 매수 수수료
            sell_fee = int(sell_amount * self._tax.sell)  # 매도 수수료
            fee_total = buy_fee + sell_fee  # 수수료 전체
            tax_amount = int(sell_amount * self._tax.tax)  # 거래세
        else:
            sell_amount = 0
            fee_total = 0
            tax_amount = 0

        # '매도금액', '수수료 전체', '세금',
        return sell_amount, fee_total, tax_amount

    def calculate_sell_tax(self, sell_amount):
        fee_rate = self._tax.sell + self._tax.buy
        return sell_amount * fee_rate

    def calculate_tax(self, account_stocks, code=None) -> None:
        """
        보유 주식에 대한 세금을 계산한다.
        """

        # 전체 주식 or 보유한 특정 주식
        if code is None:
            for code in account_stocks:
                self.calculate_tax(account_stocks, code)
        else:
            if code in account_stocks:
                stock = account_stocks[code]

                # stock['매입금액'] = abs(stock['매입가']) * stock['보유수량']
                # if stock['매입금액'] > 0:
                stock['매도금액'], stock['수수료'], stock['세금'] = self._calculate_tax(code, abs(stock['매입가']),
                                                                               stock['보유수량'], stock['매입금액'],
                                                                               stock['현재가'])
                total_fee = stock['수수료'] + stock['세금']
                stock['손실차액'] = int(stock['매도금액'] - stock['매입금액'] - total_fee)
                stock['수익률'] = (stock['손실차액'] / stock['매입금액']) * 100.0 if stock['매입금액'] != 0 else 0.0
                stock['평가금액'] = int(stock['매도금액'] - total_fee)
                stock['평가손익'] = stock['손실차액']

    def _get_deposit(self, account_num, passwd, sno: str, tr_info: transaction = None, rq_name: str = "예수금상세현황요청",
                     tr_code: str = "OPW00001", b_next: str = "0"):
        """
        예수금 정보를 읽어 들인다. +1, +2 상태 확인
        """
        # logging.debug("계좌의 예수금 정보")
        req = req_comm(self, rq_name, tr_info, func_name=self._get_deposit.__name__)

        req.set_input_value("계좌번호", account_num)
        req.set_input_value("비밀번호", passwd)
        req.set_input_value("비밀번호입력매체구분", "00")
        req.set_input_value("조회구분", "3")  # 3:추정, 2:일반조회

        req.set_callback(self.__get_deposit_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)
        return ret

    def __get_deposit_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, tr_info: transaction) -> bool:
        """
         종목코드의 일별 차트 데이터 모두를 수집한다.
         :type tr_info: object
         :param sScrNo:
         :param sRQName:
         :param sTrCode:
         :param sRecordName:
         :param sPrevNext:
         :param tr_info:
         :return:  true -> continue
         """

        fields = [
            ["예수금", int],
            ["주식증거금현금", int],
            ["수익증권증거금현금", int],
            ["익일수익증권매도정산대금", int],
            ["해외주식원화대용설정금", int],
            ["신용보증금현금", int],
            ["신용담보금현금", int],
            ["추가담보금현금", int],
            ["기타증거금", int],
            ["미수확보금", int],
            ["공매도대금", int],
            ["신용설정평가금", int],
            ["현금미수금", int],
            ["출금가능금액", int],
            ["주문가능금액", int],
            ["d+1추정예수금", int],
            ["d+2추정예수금", int],
            ["출력건수", int],
        ]

        ret = self.get_rq_comm_data_dict(sTrCode, sRQName, fields)

        self._trade_detail['예수금'] = ret["예수금"]
        self._trade_detail['현금미수금'] = ret["현금미수금"]
        self._trade_detail['예수금+1'] = ret["d+1추정예수금"]
        self._trade_detail['예수금+2'] = ret["d+2추정예수금"]
        self._trade_detail['주문가능금액'] = self._trade_detail['예수금+2']

        """
        field_list = ["통화코드",  # 0
                      "외화예수금",  # 1, "종가"
                      "원화대용평가금",  # 2
                      "해외주식증거금",  # 3
                      "출금가능금액(예수금)",  # 4
                      "주문가능금액(예수금)",  # 5
                      "외화미수(합계)",  # 6
                      "외화현금미수금",
                      "연체료",
                      "d+1외화예수금",
                      "d+2외화예수금",
                      "d+3외화예수금",
                      "d+4외화예수금",
                      ]

        sName = "종목별에수금현황"
        df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
        tr_info.result_data = df.copy() if tr_info.result_data is None else tr_info.result_data.append(df.copy())
        """

        # 추가 데이터가 있을 때 ?
        # tr_info.set_terminate()
        if tr_info.set_req_next(isNext(sPrevNext)):
            # 다음 데이터를 요청한다.
            self._get_deposit(self.account_num, "0000", sno=sScrNo, tr_info=tr_info, rq_name=sRQName,
                              tr_code=sTrCode, b_next=sPrevNext)
        return True

    def _get_profit(self, account_num, sno: str, tr_info: transaction = None,
                    rq_name: str = "일자별실현손익요청", tr_code: str = "opt10074",
                    b_next: str = "0"):
        """
        당일 체결잔고 요청
        """

        # logging.debug("계좌의 당일 실현이익 정보를 구한다.")
        req = req_comm(self, rq_name, tr_info, func_name=self._get_profit.__name__)

        today_str = dt.datetime.now().strftime("%Y%m%d")

        req.set_input_value("계좌번호", account_num)
        req.set_input_value("시작일자", today_str)
        req.set_input_value("종료일자", today_str)

        req.set_callback(self.__get_profit_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)

        return ret

    def __get_profit_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext,
                              tr_info: transaction) -> bool:
        """
         종목코드의 일별 차트 데이터 모두를 수집한다.
         :type tr_info: object
         :param sScrNo:
         :param sRQName:
         :param sTrCode:
         :param sRecordName:
         :param sPrevNext:
         :param tr_info:
         :return:  true -> continue
         """

        fields = [
            ["총매수금액", int],
            ["종매도금액", int],
            ["실현손익", int],
            ["매매수수료", int],
            ["매매세금", int],
            ["총융자금액", int],
            ["총대주금액", int],
            ["조회건수", int],
        ]

        ret = self.get_rq_comm_data_dict(sTrCode, sRQName, fields)
        self._trade_detail['당일실현손익(유가)'] = ret["실현손익"]

        # 추가 데이터가 있을 때 ?
        # tr_info.set_terminate()
        if tr_info.set_req_next(isNext(sPrevNext)):
            # 다음 데이터를 요청한다.
            self._get_profit(self.account_num, sno=sScrNo, tr_info=tr_info, rq_name=sRQName,
                             tr_code=sTrCode, b_next=sPrevNext)
        return True

    def _get_jong_mok_daily(self, jong_mok_cd, sno: str, base_day="0", tr_info: transaction = None,
                            rq_name: str = "주식일봉조회요청", tr_code: str = "OPT10081",
                            b_next: str = "0"):
        """
        종목코드의 일별 차트 데이터 모두를 수집한다.
        :type tr_info: object
        :param tr_info:
        :param jong_mok_cd:
        :param base_day:
        :param rq_name:
        :param tr_code:
        :param sno:
        :param b_next:
        :return:
        """
        # logging.debug("%s (%s) 주식 일별 조회." % (self.jong_mok_cd))
        req = req_comm(self, rq_name, tr_info, func_name=self._get_jong_mok_daily.__name__)

        req.set_input_value("종목코드", jong_mok_cd)
        req.set_input_value("수정주가구분", "0")
        # req.set_input_value("기준일자", base_day)

        req.set_callback(self.__get_jong_mok_daily_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)

        return ret

    def __get_jong_mok_daily_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext,
                                      tr_info: transaction) -> bool:
        """
        종목코드의 일별 차트 데이터 모두를 수집한다.
        :type tr_info: object
        :param sScrNo:
        :param sRQName:
        :param sTrCode:
        :param sRecordName:
        :param sPrevNext:
        :param tr_info:
        :return:  true -> continue
        """

        field_list = ['종목코드', '현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가', 
                      # '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가'
                      ]

        code = self._get_comm_data(sTrCode, sRQName, 0, "종목코드")

        sName = "주식일봉차트조회"
        # df = pd.DataFrame(self._get_comm_data_ex(sTrCode, sRQName), columns=field_list)
        df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
        tr_info.result_data = df.copy() if tr_info.result_data is None else tr_info.result_data.append(df.copy())

        # 추가 데이터가 있을 때 ?
        if tr_info.set_req_next(isNext(sPrevNext)):
            # 다음 데이터를 요청한다.
            base_day = "0"  # df['일자'][-1]

            if self._app_ui.on_jong_mok_daily(code=code, daily_df=tr_info.result_data, b_next=True):
                self._get_jong_mok_daily(jong_mok_cd=code, base_day=base_day, tr_info=tr_info, rq_name=sRQName,
                                         tr_code=sTrCode, sno=sScrNo, b_next=sPrevNext)
            else:
                tr_info.set_terminate(result=False)  # 사용자 강제 종료
        else:
            self._app_ui.on_jong_mok_daily(code=code, daily_df=tr_info.result_data, b_next=False)

        return True

    def _get_jong_mok_minute(self, jong_mok_cd, tick_min: int, sno: str, tr_info: transaction = None,
                             rq_name: str = "주식분봉조회요청", tr_code: str = "OPT10080", b_next: str = "0"):
        """
        종목코드의 분별 차트 데이터 모두를 수집한다.
        :type tr_info: object
        :param tr_info:
        :param jong_mok_cd:
        :param tick_min:
        :param rq_name:
        :param tr_code:
        :param sno:
        :param b_next:
        :return:
        """
        # logging.debug("계좌의 수익율을 구한다.")
        req = req_comm(self, rq_name, tr_info, func_name=self._get_jong_mok_minute.__name__)

        tick_min = str(tick_min)
        req.set_input_value("종목코드", jong_mok_cd)
        req.set_input_value("틱범위", tick_min)
        req.set_input_value("수정주가구분", "0")

        req.set_callback(self.__get_jong_mok_minute_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)

        return ret

    def __get_jong_mok_minute_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext,
                                       tr_info: transaction) -> bool:
        """
        종목코드의 일별 차트 데이터 모두를 수집한다.
        :type tr_info: object
        :param sScrNo:
        :param sRQName:
        :param sTrCode:
        :param sRecordName:
        :param sPrevNext:
        :param tr_info:
        :return:  true -> continue
        """
        # field_list = ["체결시간",  # 0
        #              "현재가",  # 1, "종가"
        #              "거래량",  # 2
        #              "거래대금",  # 3
        #              "시가",  # 4
        #              "고가",  # 5
        #              "저가",  # 6
        #              # "대업종구분",
        #              # "소업종구분",
        #              # "종목정보",
        #              # "전일종가"
        #              ]
        field_list = ['현재가', '거래량', '체결시간', '시가', '고가', '저가', 
                      # '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가'
                      ]

        code = self._get_comm_data(sTrCode, sRQName, 0, "종목코드")
        # gubun = INT(self._get_comm_data(sTrCode, sRQName, 0, "수정주가구분"))
        tick = INT(self._get_comm_data(sTrCode, sRQName, 0, "틱범위"))

        sName = "주식분봉차트조회"
        df = pd.DataFrame(self._get_comm_data_ex(sTrCode, sRQName), columns=field_list)
        # df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
        tr_info.result_data = df.copy() if tr_info.result_data is None else tr_info.result_data.append(df.copy())

        # 추가 데이터가 있을 때 ?
        if tr_info.set_req_next(isNext(sPrevNext)):
            # 다음 데이터를 요청한다.
            if self._app_ui.on_jong_mok_minute(code=code, tick=tick, minute_df=tr_info.result_data, b_next=True):
                self._get_jong_mok_minute(jong_mok_cd=code, tick_min=tick, tr_info=tr_info, rq_name=sRQName,
                                          tr_code=sTrCode, sno=sScrNo, b_next=sPrevNext)
            else:
                tr_info.set_terminate(result=False)  # 사용자 강제 종료
        else:
            self._app_ui.on_jong_mok_minute(code=code, tick=tick, minute_df=tr_info.result_data, b_next=False)

        return True

    def _get_stock_hoga(self, jong_mok_cd, sno: str, tr_info: transaction = None,
                             rq_name: str = "주식호가", tr_code: str = "OPT10004", b_next: str = "0"):
        """
        종목코드의 호가 정보를 읽어 들인다.
        :type tr_info: object
        :param tr_info:
        :param jong_mok_cd:
        :param rq_name:
        :param tr_code:
        :param sno:
        :param b_next:
        :return:
        """
        # logging.debug("계좌의 수익율을 구한다.")
        rq_name = rq_name + '-' + jong_mok_cd
        req = req_comm(self, rq_name, tr_info, func_name=self._get_stock_hoga.__name__)

        req.set_input_value("종목코드", jong_mok_cd)

        req.set_callback(self.__get_stock_hoga_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)

        return ret

    def __get_stock_hoga_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, tr_info: transaction) -> bool:
        """
        종목코드의 호가 데이터를 수집한다.
        :type tr_info: object
        :param sScrNo:
        :param sRQName:
        :param sTrCode:
        :param sRecordName:
        :param sPrevNext:kiwoom_api.py :
        :param tr_info:
        :return:  true -> continue
        """

        field_list = [['호가잔량기준시간', str], 
                      ['매도10차선잔량대비', int], 
                      ['매도10차선잔량', int], 
                      ['매도10차선호가', int], 
                      ['매도9차선잔량대비', int], 
                      ['매도9차선잔량', int], 
                      ['매도9차선호가', int], 
                      ['매도8차선잔량대비', int], 
                      ['매도8차선잔량', int], 
                      ['매도8차선호가', int], 
                      ['매도7차선잔량대비', int], 
                      ['매도7차선잔량', int], 
                      ['매도7차선호가', int], 
                      ['매도6차선잔량대비', int], 
                      ['매도6우선잔량', int], 
                      ['매도6차선호가', int], 
                      ['매도5차선잔량대비', int], 
                      ['매도5차선잔량', int], 
                      ['매도5차선호가', int], 
                      ['매도4차선잔량대비', int], 
                      ['매도4차선잔량', int], 
                      ['매도4차선호가', int], 
                      ['매도3차선잔량대비', int], 
                      ['매도3차선잔량', int], 
                      ['매도3차선호가', int], 
                      ['매도2차선잔량대비', int], 
                      ['매도2차선잔량', int], 
                      ['매도2차선호가', int], 
                      ['매도1차선잔량대비', int], 
                      ['매도최우선잔량', int], 
                      ['매도최우선호가', int], 
                      ['매수최우선호가', int], 
                      ['매수최우선잔량', int], 
                      ['매수1차선잔량대비', int], 
                      ['매수2차선호가', int], 
                      ['매수2차선잔량', int], 
                      ['매수2차선잔량대비', int], 
                      ['매수3차선호가', int], 
                      ['매수3차선잔량', int], 
                      ['매수3차선잔량대비', int], 
                      ['매수4차선호가', int], 
                      ['매수4차선잔량', int], 
                      ['매수4차선잔량대비', int], 
                      ['매수5차선호가', int], 
                      ['매수5차선잔량', int], 
                      ['매수5차선잔량대비', int], 
                      ['매수6우선호가', int], 
                      ['매수6우선잔량', int], 
                      ['매수6차선잔량대비', int], 
                      ['매수7차선호가', int], 
                      ['매수7차선잔량', int], 
                      ['매수7차선잔량대비', int], 
                      ['매수8차선호가', int], 
                      ['매수8차선잔량', int], 
                      ['매수8차선잔량대비', int], 
                      ['매수9차선호가', int], 
                      ['매수9차선잔량', int], 
                      ['매수9차선잔량대비', int], 
                      ['매수10차선호가', int], 
                      ['매수10차선잔량', int], 
                      ['매수10차선잔량대비', int],                       

                      ['총매도잔량직전대비', int], 
                      ['총매도잔량', int], 
                      ['총매수잔량', int], 
                      # ['시간외매수잔량대비', int],
                      # ['시간외매도잔량대비', int],
                      ['시간외매도잔량', int],
                      ['시간외매수잔량', int],
                      ]

        # 코드값을 알수 없어서...
        # code = self._get_comm_data(sTrCode, sRQName, 0, "종목코드")
        code = sRQName[-6:]
        name = self.__stock_list[code]['name']

        sName = "주식호가"
        ret = self.get_rq_comm_data_dict(sTrCode, sRQName, field_list)
        tr_info.result_data = ret.copy() if tr_info.result_data is None else tr_info.result_data.append(ret.copy())

        # 추가 데이터가 있을 때 ?
        if tr_info.set_req_next(isNext(sPrevNext)):
            # 다음 데이터를 요청한다.
            if self._app_ui.on_hoga_jan(code, name, tr_info.result_data):
                self._get_stock_hoga(jong_mok_cd=code, tr_info=tr_info, rq_name=sRQName,
                                          tr_code=sTrCode, sno=sScrNo, b_next=sPrevNext)
            else:
                tr_info.set_terminate(result=False)  # 사용자 강제 종료
        else:
            self._app_ui.on_hoga_jan(code, name, tr_info.result_data)

        return True

    def _get_jisu(self, market_cd:str, up_jong, sno: str, tr_info: transaction = None,
                             rq_name: str = "업종현재가요청", tr_code: str = "OPT20001", b_next: str = "0"):
        """
        업종 현재가 요청
        :type tr_info: object
        :param tr_info:
        :param market_cd:  시장구분 = 0:코스피, 1:코스닥, 2:코스피200
        :param up_jong : 001:종합(KOSPI), 002:대형주, 003:중형주, 004:소형주 101:종합(KOSDAQ), 201:KOSPI200, 302:KOSTAR, 701: KRX100 나머지 ※ 업종코드 참고
        :param rq_name:
        :param tr_code:
        :param sno:
        :param b_next:
        :return:
        """
        # logging.debug("계좌의 수익율을 구한다.")
        rq_name = rq_name  + '-' + market_cd + '-' + up_jong
        req = req_comm(self, rq_name, tr_info, func_name=self._get_jisu.__name__)

        req.set_input_value("시장구분", market_cd)
        req.set_input_value("업종코드", up_jong)

        req.set_callback(self.__get_jisu_callback)
        ret = req.comm_rq_data(rq_name, tr_code, b_next, sno)

        keys = {'001': '코스피', '101': '코스닥', '201': '코스피200', '138': '코스닥100'}
        name = keys[up_jong] if up_jong in keys else ''

        #item  = {
        #    item = {'현재가': 0, '등락율': 0.0, '전일대비': 0, '개인순매수': 0, '외인순매수': 0,
        #        '기관순매수': 0}  # 0-현재가, 1-등락율, 2-전일대비, 3-개인순매수, 4-외인순매수, 5-기관순매수
        #}
        data = req.tr_info.result_data
        if (data is not None) and len(name) > 0 and len(data) > 0:
            self._dashboard[name]['현재가'] = data['현재가']
            self._dashboard[name]['등락율'] = data['등락률']        # <-- 여기만 '률' 사용함 
            self._dashboard[name]['전일대비'] = data['전일대비']
            # self._dashboard[name]['현재가'] = data['현재가']

        return data

    def __get_jisu_callback(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, tr_info: transaction) -> bool:
        """
        업종의 현재가를 수집한다.
        :type tr_info: object
        :param sScrNo:
        :param sRQName:
        :param sTrCode:
        :param sRecordName:
        :param sPrevNext:
        :param tr_info:
        :return:  true -> continue
        """

        field_list = [['현재가', str], 
                      ['전일대비기호', int], 
                      ['전일대비', float], 
                      ['등락률', float], 
                      ['거래량', int], 
                      ['거래대금', int], 
                      ['거래형성종목수', int], 
                      ['거래형성비율', float], 
                      ['시가', float], 
                      ['고가', float], 
                      ['저가', float], 
                      ['상한', float], 
                      ['상승', float], 
                      ['보합', float], 
                      ['하락', float], 
                      ['하한', float], 
                      ['52주최고가', float], 
                      ['52주최고가일', int], 
                      ['52주최고가대비율', float], 
                      ['52주최저가', float], 
                      ['52주최저가일', int], 
                      ['52주최저가대비율', float], 
                      ]

        # 코드값을 알수 없어서...
        # code = self._get_comm_data(sTrCode, sRQName, 0, "종목코드")
        # code = sRQName[-6:]
        #name = self.__stock_list[code]['name']
        lst = sRQName.split('-')
        market_code = lst[1]
        up_jong = lst[2]

#        field_list = ['종목코드', '현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가', '수정주가구분', '수정비율',
#                       '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가']

#         code = self._get_comm_data(sTrCode, sRQName, 0, "종목코드")

#         sName = "주식일봉차트조회"
#         # df = pd.DataFrame(self._get_comm_data_ex(sTrCode, sRQName), columns=field_list)
#         df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
#         tr_info.result_data = df.copy() if tr_info.result_data is None else tr_info.result_data.append(df.copy())

        sName = "업종현재가"
        # df = pd.DataFrame(self._get_comm_data_ex(sTrCode, sRQName), columns=field_list)
        # df = self.get_rq_comm_data_frame(sTrCode, sRQName, sName, field_list)
        ret = self.get_rq_comm_data_dict(sTrCode, sRQName, field_list)
        tr_info.result_data = ret.copy() #  if tr_info.result_data is None else tr_info.result_data.append(ret.copy())

        # # 추가 데이터가 있을 때 ?
        # if tr_info.set_req_next(isNext(sPrevNext)):
        #     # 다음 데이터를 요청한다.
        #     if self._app_ui.on_jisu('code', 'name', tr_info.result_data):
        #         self._get_jisu(market_cd='', up_jong='', tr_info=tr_info, rq_name=sRQName,
        #                                   tr_code=sTrCode, sno=sScrNo, b_next=sPrevNext)
        #     else:
        #         tr_info.set_terminate(result=False)  # 사용자 강제 종료
        # else:
        tr_info.result_data['시장구분'] = market_code
        tr_info.result_data['업종코드'] = up_jong

        # self._app_ui.on_jisu(market_code, up_jong, tr_info.result_data)

        return True



## TR_OPT10001      주식정보
## TR_OPT10003      체결틱


# if __name__ == '__main__':
#    import sys 
#    # while True:
#    app = QApplication(sys.argv)  # 메인 윈도우를 실행한다.
    # app.setStyle('Fusion')
    #win = testWindowClass()
    #win.show()

    #sys.exit(app.exec_())
