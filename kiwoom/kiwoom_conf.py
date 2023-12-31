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

# 실시간 거래에 필요한 데이터 정의
class FidList(object):
    """ receiveChejanData() 이벤트 메서드로 전달되는 FID 목록 """

    CHEJAN = {
        10: '현재가',
        11: '전일대비',
        12: '등락율',
        13: '누적거래량',
        14: '누적거래대금',
        15: '거래량',
        16: '시가',
        17: '고가',
        18: '저가',

        20: '체결시간',
        21: '호가시간',

        23: '예상체결가',
        24: '예상체결수량',
        25: '전일대비기호',
        26: '전일거래량대비(계약,주)',
        27: '(최우선)매도호가)',
        28: '(최우선)매수호가',
        29: '거래대금증감',
        30: '전일거래량대비(비율)',
        31: '거래회전율',
        32: '거래비용',

        10010: '저가',

        302: '종목명',
        305: '상한가',
        306: '하한가',
        397: '파생상품거래단위',

        9001: '종목코드',
        900: '주문수량',
        901: '주문가격',
        902: '미체결수량',
        903: '체결누계금액',
        904: '원주문번호',
        905: '주문구분',
        906: '매매구분',
        907: '매도수구분',
        908: '주문/체결시간',
        909: '체결번호',
        910: '체결가',
        911: '체결량',
        912: '주문업무분류',
        913: '주문상태',
        914: '단위체결가',
        915: '단위체결량',
        916: '대출일',
        917: '신용구분',

        919: '거부사유',
        920: '화면번호',
        9201: '계좌번호',
        9203: '주문번호',
        9205: '관리자사번',
        921: '터미널번호',
        922: '신용구분(실시간 체결용)',
        923: '대출일(실시간 체결용)',
        924: '924',

        930: '보유수량',
        931: '매입단가',
        932: '총매입가',
        933: '주문가능수량',
        938: '당일매매수수료',
        939: '당일매매세금',

        945: '당일순매수수량',
        946: '매도/매수구분',
        949: '949',

        950: '당일총매도손일',
        951: '예수금',
        307: '기준가',
        8019: '손익율',
        957: '신용금액',
        958: '신용이자',
        959: '담보대출수량',
        918: '만기일',
        990: '당일실현손익(유가)',
        991: '당일신현손익률(유가)',
        992: '당일실현손익(신용)',
        993: '당일실현손익률(신용)'
    }

    @classmethod
    def name(cls, fid):
        return cls.CHEJAN[fid] if fid in cls.CHEJAN else str(fid)


# ----------------------------------- #
KEY_REALTIME_SISE = '주식시세'
KEY_REALTIME_CHEJAN = '주식체결'
KEY_REALTIME_PROGRAM = '종목프로그램매매'
KEY_REALTIME_HOGA_JAN = '주식호가잔량'
KEY_REALTIME_HOGA_TRADE = '주식우선호가'
KEY_REALTIME_OVERTIME_HOGA = '주식시간외호가'
KEY_REALTIME_ENC_HOGA = 'ECN주식호가잔량'
KEY_REALTIME_ENC_SISE = 'ECN주식시세'
KEY_REALTIME_ENC_CHEJAN = 'ECN주식체결'
KEY_REALTIME_GUESS_CHEJAN = '주식예상체결'
KEY_REALTIME_JONGMOK = '주식종목정보'
KEY_REALTIME_OVERTIME = '시간외종목정보'
KEY_REALTIME_TRADER = '주식거래원'
KEY_REALTIME_TODAY_TRADER = '주식당일거래원'
KEY_REALTIME_INDUSTRY_IDX = '업종지수'
KEY_REALTIME_GUESS_INDUSTRY = '예상업종지수'
KEY_REALTIME_INDUSTRY_UPDOWN = '업종등락'
KEY_REALTIME_TIME = '장시작시간'



class RealType(object):
    REALTYPE = {
        KEY_REALTIME_SISE: {  # "[key_name", "key", value] ....
            10: "현재가",
            11: "전일대비",
            12: "등락율",
            27: "(최우선)매도호가)",
            28: "(최우선)매수호가",
            15: "거래량",
            13: "누적거래량",
            14: "누적거래대금",
            16: "시가",
            17: "고가",
            18: "저가",
            25: "전일대비기호",
            26: "전일거래량대비(계약,주)",
            29: "거래대금증감",
            30: "전일거래량대비(비율)",
            31: "거래회전율",
            32: "거래비용",
            311: "시가총액(억)",
            567: "상한가발생시간",
            568: "하한가발생시간"
        },

        KEY_REALTIME_CHEJAN: {
            20: "체결시간",
            10: "현재가",
            11: "전일대비",
            12: "등락율",
            27: "매도호가",
            28: "매수호가",
            15: "거래량",
            13: "누적거래량",
            14: "누적거래대금",
            16: "시가",
            17: "고가",
            18: "저가",
            25: "전일대비기호",
            26: "전일거래량대비(계약,주)",
            29: "거래대금증감",
            30: "전일거래량대비(비율)",
            31: "거래회전율",
            32: "거래비용",
            228: "체결강도",
            311: "시가총액(억)",
            290: "장구분",
            691: "KO잡근도",
            567: "상한가발생시간",
            568: "하한가발생시간",

            # 27: "(최우선)매도호가)",
            # 28: "(최우선)매수호가"
        },

        KEY_REALTIME_PROGRAM: {
            20: "체결시간",  # 0
            10: "현재가",  # 1
            11: "전일대비",  # 2
            12: "등락율",  # 3
            15: "거래량",
            13: "누적거래량",  # 4
            16: "시가",
            17: "고가",
            18: "저가",
            202: "매도수량",
            204: "매도금액",
            206: "매수수량",
            208: "매수금액",
            212: "순매수금액",
            210: "순매수수량",
            213: "순매수금액증감",
            214: "장시작예상잔여시간",
            215: "장운영구분"
        },

        KEY_REALTIME_HOGA_JAN: {
            21: "호가시간",
            61: "총매도잔량",
            71: "총매수잔량",
            13: "누적거래량",
            
            299: "전일거래량대비예상체결률",
            215: "장운영구분",
            216: "투자자별ticker",

            41: "매도호가1",
            61: "매도호가수량1",
            81: "매도호가직전대비1",
            51: "매수호가1",
            71: "매수호가수량1",
            91: "매수호가직전대비1",

            42: "매도호가2",
            62: "매도호가수량2",
            82: "매도호가직전대비2",
            52: "매수호가2",
            72: "매수호가수량2",
            92: "매수호가직전대비2",

            43: "매도호가3",
            63: "매도호가수량3",
            83: "매도호가직전대비3",
            53: "매수호가3",
            73: "매수호가수량3",
            93: "매수호가직전대비3",

            44: "매도호가4",
            64: "매도호가수량4",
            84: "매도호가직전대비4",
            54: "매수호가4",
            74: "매수호가수량4",
            94: "매수호가직전대비4",

            45: "매도호가5",
            65: "매도호가수량5",
            85: "매도호가직전대비5",
            55: "매수호가5",
            75: "매수호가수량5",
            95: "매수호가직전대비5",

            46: "매도호가6",
            66: "매도호가수량6",
            86: "매도호가직전대비6",
            56: "매수호가6",
            76: "매수호가수량6",
            96: "매수호가직전대비6",

            47: "매도호가7",
            67: "매도호가수량7",
            87: "매도호가직전대비7",
            57: "매수호가7",
            77: "매수호가수량7",
            97: "매수호가직전대비7",

            48: "매도호가8",
            68: "매도호가수량8",
            88: "매도호가직전대비8",
            58: "매수호가8",
            78: "매수호가수량8",
            98: "매수호가직전대비8",

            49: "매도호가9",
            69: "매도호가수량9",
            89: "매도호가직전대비9",
            59: "매수호가9",
            79: "매수호가수량9",
            99: "매수호가직전대비9",

            50: "매도호가10",
            70: "매도호가수량10",
            90: "매도호가직전대비10",
            60: "매수호가10",
            80: "매수호가수량10",
            100: "매수호가직전대비10",

            121: "매도호가총잔량",
            122: "매도호가총잔량직전대비",
            125: "매수호가총잔량",
            126: "매수호가총잔량직전대비",

            23: "예상체결가",
            24: "예상체결수량",
            128: "순매수잔량",
            129: "매수비율",
            138: "순매도잔량",
            139: "매도비율",

            621: "LP매도호가수량1",
            631: "LP매수호가수량1",
            622: "LP매도호가수량2",
            632: "LP매수호가수량2",
            623: "LP매도호가수량3",
            633: "LP매수호가수량3",
            624: "LP매도호가수량4",
            634: "LP매수호가수량4",
            625: "LP매도호가수량5",
            635: "LP매수호가수량5",
            626: "LP매도호가수량6",
            636: "LP매수호가수량6",
            627: "LP매도호가수량7",
            637: "LP매수호가수량7",
            628: "LP매도호가수량8",
            638: "LP매수호가수량8",
            629: "LP매도호가수량9",
            639: "LP매수호가수량9",
            640: "LP매도호가수량10",
            650: "LP매수호가수량10"
        },

        KEY_REALTIME_HOGA_TRADE: {
            27: "(최우선)매도호가)",
            28: "(최우선)매수호가"
        },

        KEY_REALTIME_OVERTIME_HOGA: {
            21: "호가시간",
            131: "시간외매도호가총잔량",
            132: "시간외매도호가총잔량직전대비",
            135: "시간외매수호가총잔량",
            136: "시간외매수호가총잔량직전대비"
        },

        # 시간외 ECN 지원 안함
        KEY_REALTIME_ENC_HOGA: {
            # 10: '현재가',
        },

        KEY_REALTIME_ENC_SISE: {
            # 10: "현재가",
        },

        KEY_REALTIME_ENC_CHEJAN: {
            # 10: "현재가",
        },

        # 주식당일거래원
        '주식당일거래원': {
            261: "외국계매도추정합",
            262: "외국계매도추정합변동",
            263: "외국계매수추정합",
            264: "외국계매수추정합변동",
            267: "외국계순매수추정합",
            268: "외국계순매수변동",
            337: "거래소구분"
        },

        KEY_REALTIME_GUESS_CHEJAN: {
            20: "체결시간",  # 0
            10: "현재가",  # 1
            11: "전일대비",  # 2
            12: "등락율",  # 3
            15: "거래량",  # 4
            13: "누적거래량",
            25: "전일대비기호",
        },

        KEY_REALTIME_JONGMOK: {
            297: "임의연장",  # 0
            592: "장전임의연장",  # 1
            593: "장후임의연장",  # 2
            305: "상한가",  # 3
            306: "하한가",  # 4
            307: "기준가",
            689: "조기종료ELW발생",
            594: "동화단위",
            382: "증거금율표시",
            370: "종목정보",
        },

        KEY_REALTIME_OVERTIME: {  # 시간외종목정보
            10297: "임의연장정보",  # 0
            10305: "상한가",  # 1
            10306: "하한가",  # 2
            10307: "기준가"  # 3
        },

        KEY_REALTIME_TRADER: {
            10: "현재가",
            11: "전일대비",
            12: "등락율",
            25: "전일대비기호",
            9001: "종목코드,업종코드",  # 0
            9026: "회원사코드(거래원)",  # 1
            302: "종목명",  # 2
            334: "거래원명",  # 3
            20: "체결시간",  # 4
            203: "매도증감",
            207: "매수증감",
            210: "순매수수량",
            211: "순매수수량증감",
            260: "매매구분Text",
            337: "거래소구분"
        },

        KEY_REALTIME_INDUSTRY_IDX: {
            9001: "종목코드,업종코드",
            20: "체결시간",
            10: "현재가",
            11: "전일대비",
            12: "등락율",
            13: "누적거래량",
            14: "누적거래대금",
            15: "거래량",
            16: "시가",
            17: "고가",
            18: "저가",
            25: "전일대비기호",
            26: "전일거래량대비(계약,주)"
        },

        KEY_REALTIME_GUESS_INDUSTRY: {
            9001: "종목코드,업종코드",
            20: "체결시간",
            10: "현재가",
            11: "전일대비",
            12: "등락율",
            13: "누적거래량",
            14: "누적거래대금",
            15: "거래량",
            16: "시가",
            17: "고가",
            18: "저가",
            25: "전일대비기호",
            26: "전일거래량대비(계약,주)"
        },

        KEY_REALTIME_INDUSTRY_UPDOWN: {
            20: "체결시간",
            10: "현재가",
            11: "전일대비",
            12: "등락율",
            13: "누적거래량",
            14: "누적거래대금",
            251: "상승종목수",
            252: "상한종목수",
            253: "하락종목수",
            254: "하한종목수",
            256: "거래형성종목수",
            257: "거래형성비율"
        },

        KEY_REALTIME_TIME: {
            215: "장운영구분",
            20: "체결시간",
            214: "장시작예상잔여시간"
        },
    }


class realtime_info:
    def __init__(self, key, callback: callable):
        self._key = key
        self._callback = callback

    def callback(self, *args, **kwargs):
        return self._callback(*args, **kwargs) if self._callback is not None else False


def errors(err_code):
    err_dic = {
        0: {'OP_ERR_NONE', '정상처리'},

        -10: {'OP_ERR_FAIL', '실패'},
        -11: {'OP_ERR_LOGIN', '없슴'},
        -12: {'OP_ERR_SENTENCE', '조건번호와 조건식 불일치'},
        -13: {'OP_ERR_SEARCH', '조건검색 조회요청 초과'},

        -100: {'OP_ERR_LOGIN', '사용자정보교환 실패'},
        -101: {'OP_ERR_CONNECT', '서버 접속 실패'},
        -102: {'OP_ERR_VERSION', '버전처리 실패'},
        -103: {'OP_ERR_FIREWALL', '개인방화벽 실패'},
        -104: {'OP_ERR_MEMORY', '메모리 보호실패'},
        -105: {'OP_ERR_INPUT', '함수입력값 오류'},
        -106: {'OP_ERR_SOCKET_CLOSED', '통신연결 종료'},
        -107: {'OP_ERR_SECURITY', '보안모듈 오류'},
        -108: {'OP_ERR_PUBLIC_LICENSE', '공인인증 로그인 필요'},

        -200: {'OP_ERR_SISE_OVERFLOW', '시세조회 과부하'},
        -201: {'OP_ERR_RQ_STRUCT_FAIL', '전문작성 초기화 실패'},
        -202: {'OP_ERR_RQ_STRING_FAIL', '전문작성 입력값 오류'},
        -203: {'OP_ERR_NO_DATA', '데이터 없음'},
        -204: {'OP_ERR_OVER_MAX_DATA', '조회가능한 종목수 초과. 한번에 조회 가능한 종목개수는 최대 100종목'},
        -205: {'OP_ERR_DATA_RCV_FAIL', '데이터 수신 실패'},
        -206: {'OP_ERR_OVER_MAX_FID', '조회가능한 FID수 초과. 한번에 조회 가능한 FID개수는 최대 100개'},
        -207: {'OP_ERR_REAL_CANCEL', '실시간 해제오류'},
        -209: {'OP_ERR_SISE_LIMITED', '시세조회제한'},

        -300: {'OP_ERR_ORD_WRONG_INPUT', '입력값 오류'},
        -301: {'OP_ERR_ORD_WRONG_ACCNO', '계좌비밀번호 없음'},
        -302: {'OP_ERR_OTHER_ACC_USE', '타인계좌 사용오류'},
        -303: {'OP_ERR_MIS_2BILL_EXC', '주문가격이 주문착오 금액기준 초과'},
        -304: {'OP_ERR_MIS_5BILL_EXC', '주문가격이 주문착오 금액기준 초과'},
        -305: {'OP_ERR_MIS_1PER_EXC', '주문수량이 총발행주수의 1% 초과오류'},
        -306: {'OP_ERR_MIS_3PER_EXC', '주문수량은 총발행주수의 3% 초과오류'},
        -307: {'OP_ERR_SEND_FAIL', '주문전송 실패'},
        -308: {'OP_ERR_ORD_OVERFLOW', '주문전송 과부하'},
        -309: {'OP_ERR_MIS_300CNT_EXC', '주문수량 300계약 초과'},
        -310: {'OP_ERR_MIS_500CNT_EXC', '주문수량 500계약 초과'},
        -311: {'OP_ERR_MIS_OVERFLOW', '주문전송제한 과부하'},

        -340: {'OP_ERR_ORD_MRONG_ACCTINFO', '계좌정보 없음'},
        -500: {'OP_ERR_ORD_SYMCODE_EMPTY', '종목코드 없음'}
    }

    result = ""
    if type(err_code) is not int:
        err_code = int(err_code)

    if err_code in err_dic:
        result = err_dic[err_code]
    else:
        result = "unknown error !! code : " + str(err_code)
    return result


class market:
    _market_dict = {
        0: '코스피',
        10: '코스닥',
        3: 'ELW',
        8: 'ETF',
        50: 'KONEX',
        4: '무쥬얼펀드',
        5: '신주인수권',
        6: '리츠',
        9: '하일럴펀드',
        30: 'K-OTC'
    }

    @classmethod
    def string(self, k):
        if type(k) is not int:
            k = int(k)
        return self._market_dict[k] if k in self._market_dict else 'unknown'


def market_string(key):
    k = market
    return k.string(key)

    # def key(self, name):
    #    s = [x for x in self._market_dict]


def make_stock_info(code, name, market, state, listing_day):
    """
    stock_info 의 구조체
    """
    stock_info = {'name': name,
                  'code': code,
                  'market_type': market,
                  'state': state,
                  'listing-day': listing_day
                  }
    return stock_info

