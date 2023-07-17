# /usr//bin/python
# -*- coding: utf-8 -*-

import pandas
from dataclasses import dataclass 
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
# from PyQt5.QtWidgets import *

# _EVENT_MSG_NAME = 'onMessage'
# _EVENT_ERROR_NAME = 'onError'
# _EVENT_REALTIME_NAME = 'onRealtime'

__all__ = ['app_ui', 'pandas', 'order_type', 'order_gb1', 'order_gb', 'credit_gubun', 'SIM_INVESTMENT', 'user_info',
           'trade_name_buy', 'trade_name_sell']

REAL_INVESTMENT = 0                 # 실투자
SIM_INVESTMENT = 1                  # 모의투자

trade_name_buy = "1"
trade_name_sell = "2"

# 2023년도. 수익율 계산법
COMMISSION_DEMO_BUY = 0.00350       # // 모의투자 매체수수료
COMMISSION_DEMO_SELL = 0.00350      # // 모의투자 매체수수료
COMMISSION_REAL_BUY = 0.00015       # // 운영서버 매체수수료
COMMISSION_REAL_SELL = 0.00015      # // 운영서버 매체수수료
COMMISSION_TAX = 0.0023             # // 거래세

@dataclass 
class tax: 
    buy: float = COMMISSION_REAL_BUY        # 매수세
    sell: float = COMMISSION_REAL_SELL      # 매도세
    tax: float = COMMISSION_TAX             # 거래세

class user_info:
    def __init__(self, uid: str, passwd: str, transaction_mode: int = SIM_INVESTMENT, auto_connect: bool = True):
        self._uid = uid
        self._passwd = passwd  # 암호화 상태
        self.__transaction_mode = transaction_mode
        self._auto_connect = auto_connect

    def __repr__(self) -> str:
        return (self.__class__.__qualname__)

    @property
    def userId(self):
        return self._uid

    @property
    def transaction_mode(self):
        return self.__transaction_mode  # SIM_INVESTMENT or ?

    @property
    def auto_connect(self):
        return self._auto_connect

# (전일)대비 기호
def sign_icon(s):
    _giho = {
        '1': "↑",
        '2': "▲",
        '3': "",
        '4': "↓",
        '5': "▼"
    }
    return _giho[s] if s in _giho else ""

# ######################## 주식 거래 (매도/매수) ###################
def order_type(orders: str) -> int:
    order_dic = {
        "신규매수": 1,
        "신규매도": 2,
        "매수취소": 3,
        "매도취소": 4,
        "매수정정": 5,
        "매도정정": 6
    }

    return order_dic[orders]

order_gb1 = {
    "지정가": "00",
    "시장가": "03",
    "조건부지정가": "05",
    "최유리지정가": "06",
    "최우선지정가": "07",
    "지정가IOC": "10",
    "시장가IOC": "13",
    "최유리IOC": "16",
    "지정가FOK": "20",
    "시장가FOK": "23",
    "최유리FOK": "26",
    "장전시간외종가": "61",
    "시간외단일가매매": "62",
    "장후시간외종가": "81"
}

def order_gb(orders: str) -> str:
    return order_gb1[orders]

def credit_gubun(gubun):
    gb = {
        '00': "현금",
        '03': "융자",
        '99': "융자합"
    }
    return gb[gubun] if gubun in gb else '현금'

class app_ui():
    def __init__(self):
        #QWidget.__init__(self) # , flags=Qt.Widget)
        self.__win = None

    def print(self, *args, **kwargs):
        # self.event_handler.fire( _EVENT_MSG_NAME, *args, **kwargs )
        """
        """

    def error(self, *args, **kwargs):
        # self.event_handler.fire( _EVENT_ERROR_NAME, *args, **kwargs )
        """
        """

    def event_handler_link(self, event_msg_func):
        # self._set_event_single_handler_link( _EVENT_MSG_NAME, event_msg_func )
        """
        """

    def event_handler_error_link(self, event_err_func):
        # self._set_event_single_handler_link( _EVENT_ERROR_NAME, event_err_func )
        """
        """

    def event_handler_realtime_link(self, event_realtime_func):
        # self._set_event_single_handler_link( _EVENT_REALTIME_NAME, event_realtime_func )
        """
        """

    #def _set_event_single_handler_link(self, msg, func):
    #    # self.event_handler.unregister_event( msg )
    #    # self.event_handler.register_event( msg )
    #    # self.event_handler.link( func, msg )
    #    """
    #    """

    # ------------------- events ------------------- #
    def on_login(self, is_logon: bool, user: user_info):
        pass

    def on_account_detail(self, account_no: str, account_detail: dict, code=None) -> None:
        pass

    def on_trading_finished(self, code, name, cnt, trade_name) -> None:
        pass

    def on_jong_mok_daily(self, code, daily_df: pandas.DataFrame, b_next: bool) -> bool:
        return True

    def on_jong_mok_minute(self, code, tick, minute_df: pandas.DataFrame, b_next: bool) -> bool:
        return True

    # '주식호가잔량'
    def on_hoga_jan(self, code: str, name: str, data: dict):
        return True

    # '업종현재가'
    def on_realtime_jisu(self, code: str, up_jong: str, data: dict):
        return True

    # '업종등락'
    def on_realtime_jisu_updown(self, code: str, up_jong: str, data: dict):
        return True
    
    # undefined data types
    def on_realtime(self, real_type: str, code: str, name: str, data, real_data):
        print("==> ui.py : real-data_slot %s : %s(%s)" % (real_type, name, code)) 

    # 실시간 시세 정보...
    def on_realtime_sise(self, real_type: str, code: str, name: str, data: dict):
        pass

    # 실시간 주식 체결정보
    def on_realtime_che_jan(self, real_type: str, code: str, name: str, data: dict):
        pass

    # '종목프로그램매매'
    def on_realtime_program(self, real_type: str, code: str, name: str, data: dict):
        pass

    # '실시간 주식호가잔량'
    def on_realtime_hoga_jan(self, real_type: str, code: str, name: str, data: dict):
        pass

    # 주식우선호가
    def on_realtime_hoga_trade(self, real_type: str, code: str, name: str, data: dict):
        pass

    # 주식시간외호가
    def on_realtime_overtime_hoga(self, real_type: str, code: str, name: str, data: dict):
        pass

    # 조건검색 리스트 dict 구조로
    def on_conditions_list(self, conditions: dict):
        pass

    # 조건검색에서 받은 데이터, 'L': 검색, 'I' : 실시간 추가발생, 'D' : 실시간 조건검색 제거
    def on_conditions_stocks(self, gubun, code, name, condition_name, condition_index, sno=None):
        pass

    # 신규 주식이 추가 되었을 때..
    def on_new_account_stock(self, code, name):
        pass

    def on_init_tax(self, trans_mode, tax):
        """
        실거래/모의투자에 따라서 매매 수수료가 변경 된다.
        """
        if trans_mode == SIM_INVESTMENT:
           tax.buy = 0.0034974182444062  # 0.35%
           tax.sell = 0.0034974182444062
        return tax
