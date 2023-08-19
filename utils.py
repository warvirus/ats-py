#!/usr/bin/env python
# coding: utf-8

from kiwoom.tools import *

import pandas as pd
import numpy as np
from tabulate import tabulate
import os, glob
import json
import datetime as dt
from dateutil.parser import parse
import pickle
import talib.abstract as ta
# from talib import MA_Type


import numexpr

# from numexpr.interpreter import _set_num_threads, _get_num_threads, MAX_THREADS
# from numexpr import use_vml

# if use_vml:
#    from numexpr.interpreter import (
#        _get_vml_version, _set_vml_accuracy_mode, _set_vml_num_threads,
#        _get_vml_num_threads)
# 2021-03-24 12:30:15,432: INFO utils _init_num_threads: Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS"
# not set, so enforcing safe limit of 8.
# 2021-03-24 12:30:15,432: INFO utils _init_num_threads: NumExpr defaulting to 8 threads.
# cores = numexpr.detect_number_of_cores()
# threads = numexpr.detect_number_of_threads()
# numexpr.set_num_threads(threads)

numexpr._init_num_threads()
# print('NUMEXPR_MAX_THREADS : ', numexpr.interpreter.MAX_THREADS)


# from sklearn.externals import joblib

# ----------------- database io  ----------------- #

info = {'ver': '0.0.1', 'created': dt.datetime.now().strftime('%Y%m%d %H:%M:%S')}


# reserved = {}
def write_stock_contents_file(f_name, contents):
    header = {'info': info, }

    with open(f_name, 'wb') as file:
        pickle.dump(header, file)  # { 'info': info, contents: contennts} [code...][code...]
        codes = [code for code in contents]
        pickle.dump(codes, file)
        for value in contents.values():
            pickle.dump(value, file)


def read_stock_contents_file(f_name):
    header = {}
    codes = []
    stock_list = {}

    with open(f_name, 'rb') as file:
        header = pickle.load(file)  # header
        codes = pickle.load(file)
        for code in codes:
            stock_list[code] = pickle.load(file)
    return stock_list
    # contents = load_from_disk(fname)


def make_stock_contents(code, name, stocks_contents, market_type):
    if len(stocks_contents) <= 0:
        return None

    # 시간 문자열로 변환
    db = pd.DataFrame()
    db['일자'] = np.array([date2stringf(str(x).replace("-", "")) for x in stocks_contents['일자']])
    db['현재가'] = stocks_contents['현재가']
    db['거래량'] = stocks_contents['거래량']
    db['거래대금'] = stocks_contents['거래대금']
    db['시가'] = stocks_contents['시가']
    db['고가'] = stocks_contents['고가']
    db['저가'] = stocks_contents['저가']
    db.set_index(stocks_contents['일자'])

    end_date = db.loc[db.index[0]]['일자']
    start_date = db.loc[db.index[-1]]['일자']

    db_contents = {'name': name,
                   'daily': {
                       'start': start_date,
                       'end': end_date,
                       'market-type': market_type,
                       'data': db
                   }
                   }
    return db_contents.copy()


def load_from_daily_stocks(filename):
    db = read_stock_contents_file(filename)
    return db


def find_stock(contents, name):
    # 코드에서 찾기
    for code in contents:
        if code == name:
            return contents[code]

    # 이름으로 찾기
    for code in contents:
        if contents[code]['name'] == name:
            return contents[code]
    return None


def find_code(stock_list, name):
    for code in stock_list:
        if stock_list[code]['name'] == name:
            return code
    return None

    # return (code for code in stock_list if stock_list[code]['name'] == name), None


# ----------------- database io  ----------------- #

default_config_file = 'config.json'
default_favorite_file = 'favorites.json'
default_config_folder = 'conf'
default_config = {
    'general': {
        'trading': {
            'start': '0900',
            'end': '1530',
            'auto-finish': '2358',
            'use-auto-finish': False            
        },
        'account': {
            "passwd": "0000"
        },

        'debug': {
            'macd': []
        },
        "기본정보": {
            "목표": 500000000,
            "투자금": 100000000
        }
    },

    'sell': {
        'half': -4.0,
        'full': -6.0
    },

    'buy': {
        'max-amount': 1000000,
        'close-tradetime': '1518',
        'max-stocks': 50,
        'use max-stocks': True
    },
    'case search': {},
    'favorites': {
        'macd': {}
    }
}
default_favorites = {
    'macd': {}
}


# 즐겨찾기
def load_favorite_file(fav_file=default_favorite_file, config_folder=default_config_folder):
    """
    즐겨찾기을 설정 파일에서 읽어 들인다.
    """
    config_dir = os.path.join(os.getcwd(), config_folder)
    filename = '{}/{}'.format(config_dir, fav_file)
    if os.path.isdir(config_dir) is not True:
        os.mkdir(config_dir)
        favorites = default_favorites.copy()
        save_json_file(filename, favorites)
        return favorites

    favorites = load_json_file(filename)

    if 'macd' not in favorites:
        favorites['macd'] = default_favorites['macd']

    return favorites


def save_favorite_file(favorites, fav_file=default_favorite_file, config_folder=default_config_folder):
    """
    즐겨찾기 파일을 저장한다.
    """
    config_dir = os.path.join(os.getcwd(), config_folder)
    if os.path.isdir(config_dir) is not True:
        os.mkdir(config_dir)

    filename = '{}/{}'.format(config_dir, fav_file)
    save_json_file(filename, favorites)


def load_config_file(config_file=default_config_file, config_folder=default_config_folder):
    """
    환정설정 파일을 읽어 들인다.
    """
    config_dir = os.path.join(os.getcwd(), config_folder)
    filename = '{}/{}'.format(config_dir, config_file)
    if os.path.isdir(config_dir) is not True:
        os.mkdir(config_dir)
        _config = default_config.copy()
        save_json_file(filename, _config)
        return _config

    if not os.path.isfile(filename):
        _config = default_config.copy()
        save_json_file(filename, _config)
        return _config

    _config = load_json_file(filename)

    # 기본값 설정
    if 'general' not in _config:
        _config['general'] = default_config['general'].copy()
    if 'trading' not in _config['general']:
        _config['general']['trading'] = default_config['general']['trading'].copy()
    if 'account' not in _config['general']:
        _config['general']['account'] = default_config['general']['account'].copy()
    if 'passwd' not in _config['general']['account']:
        _config['general']['account']['passwd'] = default_config['general']['account']['passwd'] # .copy()
    if '기본정보' not in _config['general']:
        _config['general']['기본정보'] = default_config['general']['기본정보'].copy

    if 'debug' not in _config['general']:
        _config['general']['debug'] = default_config['general']['debug'].copy()
    elif 'macd' not in _config['general']['debug']:
        _config['general']['debug']['macd'] = default_config['general']['debug']['macd'].copy()

    # 매도
    if 'sell' not in _config:
        _config['sell'] = default_config['sell'].copy()

    # 매수
    if 'buy' not in _config:
        _config['buy'] = default_config['buy'].copy()
    if 'amount' not in _config['buy']:
        _config['buy']['amount'] = 1000000
    if 'close-tradetime' not in _config['buy']:
        _config['buy']['close-tradetime'] = '1518'
    if 'max-stocks' not in _config['buy']:
        _config['buy']['max-stocks'] = 50
    if 'use max-stocks' not in _config['buy']:
        _config['buy']['use max-stocks'] = True

    # 조건별 검색
    if 'case search' not in _config:
        _config['case search'] = default_config['case search'].copy()

    # 즐겨찾기
    if 'favorites' not in _config:
        _config['favorites'] = {} # load_favorite_file(config_folder=config_folder)

    return _config


def save_config_file(config, config_file=default_config_file, config_folder=default_config_folder):
    """
    환경 설정파일을 저장한다.
    """
    config_dir = os.path.join(os.getcwd(), config_folder)
    if os.path.isdir(config_dir) is not True:
        os.mkdir(config_dir)

    filename = '{}/{}'.format(config_dir, config_file)
    save_json_file(filename, config)


# ----------------- functions  ----------------- #

# 5일선데이터 합성
def mean_m(gs, nday):
    m = gs.close.rolling(window=nday).mean()
    return m


def get_macd(df, short=12, long=26, t=9, cci=9, rsi=14):
    """
    MACD 값을 구한다.
    """

    """
    # MACD 관련 수식
    ma_12 = df.close.ewm(span=short).mean()  # 단기(12) EMA(지수이동평균)
    ma_26 = df.close.ewm(span=long).mean()  # 장기(26) EMA
    macd = ma_12 - ma_26  # MACD
    macds = macd.ewm(span=t).mean()  # Signal
    macdo = macd - macds  # Oscillator

    df = df.assign(macd=macd, macds=macds, macdo=macdo)  # .dropna()
    """
    df['CCI'] = ta.CCI(df['high'], df['low'], df['close'], cci)
    df['RSI'] = ta.RSI(df['close'], rsi)
    macd, macdsignal, macdhist = ta.MACD(df['close'], fastperiod=short, slowperiod=long, signalperiod=t)
    df = df.assign(macd=macd, macds=macdsignal, macdo=macdhist)  # .dropna()

    return df


def get_mean20(df):
    """
    20일 지수 이동평균
    """
    ma20 = df.close.ewm(span=20).mean()  # 20일 (지수이동평균)
    df = df.assign(ma20=ma20)  # .dropna()
    return df


# https://m.blog.naver.com/PostView.nhn?blogId=anthouse28&logNo=221668106873&proxyReferer=https:%2F%2Fwww.google.com%2F
def OBV(close, volume):
    # obv 값이 저장될 리스트를 생성합니다.
    obv_value = [None] * len(close)
    obv_value[0] = volume.iloc[0]
    # 마지막에 사용할 인덱스를 저장해 둡니다.
    index = close.index

    # 연산에서 사용하기 위해 리스트 형태로 바꾸어 줍니다.
    close = list(close)
    volume = list(volume)

    # OBV 산출공식을 구현
    for i in range(1, len(close)):
        if close[i] > close[i - 1]:
            obv_value[i] = int(obv_value[i - 1]) + int(volume[i])

        elif close[i] < close[i - 1]:
            obv_value[i] = int(obv_value[i - 1]) - int(volume[i])

        else:
            obv_value[i] = int(obv_value[i - 1])

    # 계산된 리스트 결과물을 마지막에 Series 구조로 변환해 줍니다.
    obv = pd.Series(obv_value, index=index)

    return obv


def OBV_slow(close, volume):
    # obv가 저장될 pandas series를 생성
    obv = pd.Series(index=close.index)
    obv.iloc[0] = volume.iloc[0]

    # OBV 산출공식을 구현
    # pd.Series 구조를 연산에 직접 사용
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] + volume[i]

        elif close.iloc[i] < close.iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] - volume[i]

        else:
            obv.iloc[i] = obv.iloc[i - 1]

    return obv


from plotly import tools
import plotly.offline as offline
import plotly.graph_objs as go


# 출처: https://excelsior-cjh.tistory.com/110?category=975542 [EXCELSIOR]
def draw_chart(df):
    close = go.Scatter(x=df.date, y=df['close'], name="close")
    obv = go.Scatter(x=df.date, y=df['obv'], name="obv")
    macd = go.Scatter(x=df.date, y=df['macd'], name="MACD")
    signal = go.Scatter(x=df.date, y=df['macds'], name="Signal")
    oscillator = go.Bar(x=df.date, y=df['macdo'], name="oscillator")
    trade_volume = go.Bar(x=df.date, y=df['volume'], name="volume")

    data = [macd, signal, oscillator]

    layout = go.Layout(title='MACD 그래프')  # .format(code))
    fig = tools.make_subplots(rows=3, cols=1, shared_xaxes=True)

    fig.append_trace(close, 1, 1)

    for trace in data:
        fig.append_trace(trace, 2, 1)

    fig.append_trace(obv, 3, 1)
    # fig.append_trace(trade_volume, 3,1)
    # fig = go.Figure(data=data, layout=layout)

    offline.iplot(fig)


def linear_regression(y: list):
    a = 0
    b = 0

    if len(y) >= 2:
        # x 값과 y값
        x = [x for x in range(1, len(y))]

        # x와 y의 평균값
        mx = np.mean(x)
        my = np.mean(y)
        # print("x의 평균값:", mx)
        # print("y의 평균값:", my)

        # 기울기 공식의 분모
        divisor = sum([(mx - i) ** 2 for i in x])

        # 기울기 공식의 분자
        def top(x, mx, y, my):
            d = 0
            for i in range(len(x)):
                d += (x[i] - mx) * (y[i] - my)
            return d

        dividend = top(x, mx, y, my)

        # print("분모:", divisor)
        # print("분자:", dividend)

        # 기울기와 y 절편 구하기
        if divisor != 0:
            a = dividend / divisor
            b = my - (mx * a)

        # 출력으로 확인
        # print("기울기 a =", a)
        # print("y 절편 b =", b)

    return a, b


def load_macd_stocks(bAll: bool = False, bSave: bool = True, callback: callable = None):
    _daily_fname = './data/daily_stocks.pkl'
    file_name = 'data/stocks.json'

    stock_list = load_json_file(file_name)  # 주식 종목 리스트
    daily_stocks = load_from_daily_stocks(_daily_fname)  # 일별 주식시세 정보

    if bAll is False:
        new_stocks = {}
        idx = 0
        for code, stock in stock_list.items():
            text = '{code} - {name}'.format(code=code, name=stock['name'])
            # self.listwidget.addItem(text)

            # ------------------------------------------------- #
            stock = find_stock(daily_stocks, code)
            if stock is not None:
                market = int(stock['daily']['market-type'])
                if market == 0 or market == 10:  # 코스피 & 코스닥
                    df = stock['daily']['data']
                    df = df.rename(columns={'일자': 'date',
                                            '현재가': 'close',
                                            '거래량': 'volume',
                                            '시가': 'open',
                                            '고가': 'high',
                                            '저가': 'low',
                                            '거래대금': 'amount'
                                            })

                    now = dt.datetime.now() - dt.timedelta(days=120)  # 240 일전
                    s_date = now.strftime('%Y-%m-%d')
                    df = df[df.date > s_date]  # '2021-01-01']      # 2021년 이후
                    df = df[df.volume > 0]  # 공휴일 제거

                    # 최소 30일 거래된 주식
                    if len(df) > 30:
                        df = df.set_index('date')
                        df = df.sort_index(axis=0, ascending=True)

                        df = get_macd(df)
                        obv = OBV(df.close, df.volume)
                        df = df.assign(obv=obv).dropna()

                        """"
                        매수조건
                            1. obv 음수 : 매집단계
                            2. macd, signal : 모두 음수 (강한 매수)
                            3. macd가 signal 돌파
                            4. oscillator 가 음수에서 양수 돌파
                        """
                        obv = df.obv.values[-20:]
                        macd = df.macd.values[-20:]
                        macdo = df.macdo.values[-20:]
                        macds = df.macds.values[-20:]

                        if obv[-1] < 0 \
                                and macdo[-1] > 0 and macdo[-2] <= 0 \
                                and (macd[-1] < 0 and macds[-1] < 0) \
                                :  # 2
                            new_stocks[code] = stock.copy()  # add new ...
                            print('--------------->', text)
                            print_df(df.tail())
                            if callable(callback):
                                callback(idx, code, stock, df, True)
                        else:
                            if callable(callback):
                                callback(idx, code, stock, df, False)
                    # if len(df) > 30:
                    else:
                        if callable(callback):
                            callback(idx, code, stock, df, False)

                # if market == 0 or market == 10
            # if stock is not None:
            idx += 1
        # for code, stock in stock_list.items():

        # 재설정
        stock_list = new_stocks

        # 결과값 저장
        if bSave:
            favorite_macd = {code: {'name': stock['name']} for code, stock in stock_list.items()}

            favorites = load_favorite_file()
            if 'macd' in favorites:
                favorites['macd'] = favorite_macd.copy()
            else:
                favorites = {
                    'macd': favorite_macd.copy()
                }
            save_favorite_file(favorites)
    # bAll ?

    return stock_list, daily_stocks


# ----------------- functions  ----------------- #

if __name__ == '__main__':
    d1 = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for i in range(100000):
        print(i)
    d2 = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('time_diff = {}'.format(time_diff(d1, d2)))

    config = load_config_file()
    save_config_file(config)
    print(config)
