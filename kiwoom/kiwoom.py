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

"""
    키움 API 주위(제한) 사항 ( 출처: https://kminito.tistory.com/35 )

    키움증권은 서버 과부화 및 API 악용을 막기 위하여 API 사용 조회 및 주문 제한이 있습니다.
    현재 공식적으로는 초당 5회 미만으로 제한을 두고 있으며, 추가적인 제한은 시장 상황과 서버 상황에
    따라 유동적입니다. 1시간 이상 프로그램이 작동하며 많은 조회 및 주문이 이루어진다는 가정 하에,
    3.6초의 시간간격을 두고 TR요청 및 주문을 하는 것이 일반적입니다. (작성일 2020년 10월 31일 기준)

    3.6초 간격 : 1시간에 1,000회 -> 정상 작동
    3.5초 간격 : 1시간에 1,028회 -> 조회 차단 발생

    또한 키움에서는 시세/호가/조건검색/주문체결 등을 모두 실시간데이터로 서비스하고 있으니,
    과도한 조회요청 대신에 실시간 이벤트와 실시간 데이터를 사용할 것을 권고하고 있습니다.

    그리고 주문 및 조회 패턴에 따라 꼭 3.6초 이상으로 설정할 필요는 없으니 참고 바랍니다.
    주문 및 조회가 계속 반복되어 1시간에 1,000회를 넘는 것이 아니라면 시간 간격을 0.2초로
    세팅하여도 문제 없습니다. 사용하시는 패턴에 따라서 적절히 시간 가격을 설정하시면 됩니다.

    조회 차단에 대한 키움증권의 공식적인 답변
    =================================================================================
    출처: https://bbn.kiwoom.com/bbn.genNtcDetail.do

    서버리스크를 회피하면서, OpenAPI 의 모든 고객분들께서 조회 차단을 회피하는 가이드는 아래와 같습니다.
    (1초당 5회로 기작업되어 있다는 전제하에 이를 기준으로 한 가이드 입니다.)

    주문에 대한 제한은 기존 초당5초 외에 추가된 제한이 없습니다.(추가내용)
    제한기준이 시장상황과 서버상황에따라 유동적인 이유로 이에 차단메세지를 수신하신 고객님(Client)들께
    공통적인 가이드를 제시하는데 시간이 지체되었습니다.

    서버운영에 문제를 야기시켰던 부분은 1초당 5회라는 횟수보다는 이를 반복하는 것 입니다.
    서버의 점유율이 해소되기 위한 idle Time을 확보하기가 어렵습니다.

    서버리스크를 회피하면서, OpenAPI 의 모든 고객분들께서 조회 차단을 회피하는 가이드는 아래와 같습니다.
    (1초당 5회로 기작업되어 있다는 전제하에 이를 기준으로 한 가이드 입니다.)

        - 1초당 5회 조회를 1번 발생시킨 경우 : 17초대기
        - 1초당 5회 조회를 5연속 발생시킨 경우 : 90초대기
        - 1초당 5회 조회를 10연속 발생시킨 경우 : 3분(180초)대기

    위 방법으로 대응이 어려운 성격의 프로그램을 운영중이신 고객분께서는 글 올려주시면 별도의 대안으로 답변드리도록 하겠습니다.
    안정적인 서비스 운영이 최우선이니 양해바라겠습니다.

"""
from enum import Enum
class Marketcode(Enum):
    KOSPI = '001' # {'mk':'0', 'name':'001'}
    KOSPI200 = '201' # {'mk':'0', 'name':'201'}
    KOSDAQ = '101' # {'code':'1', 'name':'100'}
    KOSDAQ200 = '138' # {'code':'1', 'name':'138'}
        
###############################################################
class kiwoom(app_ui):
    def __init__(self, _app_ui = None, timeout_ms=-1):
        super().__init__()
        
        # 실시간 데이터 요청 & 즐겨찾기
        self.___real_times = {}
        self.___favorites = {}

        self.kiwoom_api = kiwoom_api(self, timeout_ms)

    @property
    def stocks(self) -> dict:
        return self.kiwoom_api.stocks

    @property
    def stock(self, code) -> dict:
        """
        #         = {
        #            'name': name,
        #            'code': code,
        #             'market_type': market,
        #             'state': state,
        #             'listing-day': listing_day
        #             }
        """

        return self.kiwoom_api.stocks[code]

    @property
    def account_stocks(self):
        return self.kiwoom_api.account_stocks

    def account_stock(self, code):
        return self.kiwoom_api.account_stocks[code]

    def login(self, uid = '', password = '', tran_mode: int = 0, auto: bool = True, login_only = False) -> bool:
        """
        :param callback:
        :param uid:
        :param password:
        :param tran_mode:
        :param auto:
        :return:
        """
        user = user_info(uid, password, tran_mode, auto_connect=auto)

        # 로그인이 되면 자동으로 사용자 정보 와 주식 정보를 읽어 들인다.
        is_connected = self.kiwoom_api.login(user)

        # login 성공시 계좌 정보를 읽어 들인다.
        if login_only == False:
            if is_connected:
                # 소유한 계좌 정보을 읽어 들인다.
                self.get_account_detail()
                
                # 화면 오픈시 서버에 저장된 조건식을 받아온다.
                # 이 함수를 호출하지 않으면 이후 조건명리스트를 불러올수가 없으니 조건 검색을 할 경우
                # 무조건 이 함수를 처음에 불러와야 한다.
                # 조건검색을 시작하려면 한번은 꼭 호출해야한다
                self.kiwoom_api.get_realConditionFunctionLoad()

        return is_connected

    def quit(self):
        self.quit()

    def save_acount_stocks(self):
        self.kiwoom_api._save_cache_account_stocks()

    # 내 계좌 잔고 현황을 board 정보에 출력 해준다.
    # @function_tracer
    def get_account_detail(self, sno: str = "200011"):
        return self.kiwoom_api._get_account_detail(sno=sno)

    def get_deposit(self, account_num, passwd, sno: str = "200012"):
        self.kiwoom_api._get_deposit(account_num=account_num, passwd=passwd, sno=sno)
        sleep_ms(300)
        self.kiwoom_api._get_profit(account_num=account_num, sno=sno)

    # ----- 일별/분별 지원
    def get_ohlcv(self, jong_mok_cd, interval="day", count=200, base_day="0", sno: str = "200012"):
        ret = None
    
        if interval in ["day", "days"]:
            ret = self.kiwoom_api._get_jong_mok_daily(jong_mok_cd, sno=sno, base_day=base_day)
        else:
            minute = 1      # default

            if interval in ["minute1", "minutes1"]:
                minute = 1
            elif interval in ["minute3", "minutes3"]:
                minute = 3
            elif interval in ["minute5", "minutes5"]:
                minute = 5
            elif interval in ["minute10", "minutes10"]:
                minute = 10
            elif interval in ["minute15", "minutes15"]:
                minute = 15
            elif interval in ["minute30", "minutes30"]:
                minute = 30
            elif interval in ["minute60", "minutes60"]:
                minute = 60
            # else:
            #    if interval in ["week", "weeks"]:
            ret = self.kiwoom_api._get_jong_mok_minute(jong_mok_cd=jong_mok_cd, tick_min=minute, sno=sno)

        return ret

    # def get_jong_mok_daily(self, jong_mok_cd, base_day="0", sno: str = "200012"):
    #     return self.kiwoom_api._get_jong_mok_daily(jong_mok_cd, sno=sno, base_day=base_day)

    # def get_jong_mok_minute(self, jong_mok_cd, tick_min: int = 1, sno: str = "200011"):
    #     return self.kiwoom_api._get_jong_mok_minute(jong_mok_cd=jong_mok_cd, tick_min=tick_min, sno=sno)

    # ############ 매도/매수 함수 (현금거래) ######

    def set_real_time(self, code, fid_list: list = None, add: bool = True, sno='400001'):
        self._set_real_time(code, add, fid_list, False, sno)

    def _set_real_time(self, code, add: bool = True, fid_list: list = None, add_list: bool = True, sno='400001'):
        # 실시간 추가

        if add:
            if fid_list is None:
                fid_list = [str(x) for x in RealType.REALTYPE[KEY_REALTIME_SISE]]

            fids = ";".join(fid_list)
            self.kiwoom_api.set_realRegCondition(sno, code, fids, "1" if add_list else "0")

            # def set_realRegCondition(self, strScreenNo, strCodeList, strFidList, strOptType):
            # OpenAPI.SetRealReg(_T("0150"), _T("039490"), _T("9001;302;10;11;25;12;13"), "0");  // 039490종목만 실시간 등록
            # OpenAPI.SetRealReg(_T("0150"), _T("000660"), _T("9001;302;10;11;25;12;13"), "1");  // 000660 종목을 실시간 추가등록

            self.___real_times[code] = ""
        else:
            self.kiwoom_api.set_realRemoveCondition("ALL", code)

            # OpenAPI.SetRealRemove("0150", "039490");  // "0150"화면에서 "039490"종목해지
            # OpenAPI.SetRealRemove("ALL", "ALL");  // 모든 화면에서 실시간 해지
            # OpenAPI.SetRealRemove("0150", "ALL");  // 모든 화면에서 실시간 해지
            # OpenAPI.SetRealRemove("ALL", "039490");  // 모든 화면에서 실시간 해지
            if code in self.___real_times:
                del self.___real_times[code]

    def add_favorites(self, *args, **kwargs):
        """
        즐기찾기에 추가한다. 즐겨찾기에 설정되면, 실시간 데이터를 받아 들인다.
        """
        favorites = []
        for code in args:
            if type(code) is list:  # [...] array 로 입력 받았을 때..
                for in_code in code:
                    # 주식정보가 있는 것만 추가한다.
                    if in_code in self.kiwoom_api.stocks:
                        favorites.append(in_code)
            else:
                code = str(code)
                if code in self.kiwoom_api.stocks:
                    favorites.append(code)

        def divide_list(lst, n):
            # 리스트 lst 의 길이가 n이면 계속 반복
            for bi in range(0, len(lst), n):
                yield lst[bi:bi + n]

        # 중복제거 와 90(최대 100개로 한정 지원 때문에)개로 분할...
        favorites_list = list(divide_list(list(set(favorites)), 90))

        # 즐겨찾기가 기존보다 작으면, 나머지는 즐겨찾기 항목에서 화면제거
        if len(favorites_list) < len(self.___favorites):
            for sno in self.___favorites:
                self.kiwoom_api.set_disconnectRealData(sno)

        #  즐겨찾기 설정
        for idx, favorites in enumerate(favorites_list):
            scr_tr_name = '즐겨찾기-%d' % idx
            sno = '5100%02d' % idx

            # 즐겨찾기 추가
            self.___favorites[sno] = favorites.copy()
            self._set_favorites(favorites, rq_name=scr_tr_name, sno=sno)
            idx += 1

    def remove_favorites(self, *args):
        """
        즐기찾기리스트에서 삭제한다. 즐겨찾기에 설정되면, 실시간 데이터를 더이상 받지 않는다.
        """
        fav_list = []
        real_list = []

        req_del_favorites = []
        for code in args:
            if type(code) is list:  # [...] array 로 입력 받았을 때..
                for in_code in code:
                    # 주식정보가 있는 것만 추가한다.
                    if in_code in self.kiwoom_api.stocks:
                        req_del_favorites.append(in_code)
            else:
                code = str(code)
                if code in self.kiwoom_api.stocks:
                    req_del_favorites.append(code)

        # 즐겨찾기 리스트 다시 생성
        for code in req_del_favorites:
            if code in self.___favorites:
                del (self.___favorites[code])

        # 실시간 리스트에 없는 코드는 실시간 데이터를 더이상 받지 않는다.
        for code in req_del_favorites:
            self._set_real_time(code, add=False)  # , sno = '400001')

        # 즐겨찾기 종목명을 다시 설정한다.
        return self._set_favorites(self.___favorites, rq_name='즐겨찾기-1')

    def _set_favorites(self, favorites, rq_name: str, stock_opt=0, sno='500001') -> int:
        """
        관심종목등록요청
        """
        code_list = ";".join([code for code in favorites])
        cnt = len(favorites)
        logging.debug("관심종목등록요청 : %d 개, %s" % (cnt, code_list))

        return self.kiwoom_api._setFavorites(code_list=code_list, cnt=cnt, rq_name=rq_name, stock_opt=stock_opt, sno=sno)

    def get_current_sise(self, code, sno="30010"):
        """
         실시간 현재가/종목코드를 받아 들인다.
        :param code: 종목코드
        :param sno: 화면 번호
        :return:
        """

    def get_current_hoga(self, code, sno="30010"):
        """
         실시간 현재가/종목코드의 호가 체결 정보를 읽어 들인다.
        :param code: 종목코드
        :param sno: 화면 번호
        :return:
        """
        self.kiwoom_api._get_stock_hoga(code, sno=sno)

    def get_jisu(self, market, sno="30010"):
        """
        코스피(종합지수), 코스닥(코드닥지수), 코스피200(코스피200)
        """
        code = '0' 
        if market == Marketcode.KOSPI200:
            code = '2'
        elif market == Marketcode.KOSDAQ or market == Marketcode.KOSDAQ200:
            code = '1'

        m = market.value if type(market) is Marketcode else market
        ret = self.kiwoom_api._get_jisu(code, m, sno)

        return ret


    def get_che_jan_list(self, account_num, gubun="0", trade_gubun="2", code=None, che_jan="1", sno="300002"):
        """
        미체결 정보를 리스트로 받는다.
        """
        return self.kiwoom_api._get_che_jan_list(account_num=account_num, gubun=gubun, trade_gubun=trade_gubun, 
                                                 code=code, che_jan=che_jan, sno=sno)
 