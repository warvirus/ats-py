# /usr//bin/python
# -*- coding: utf-8 -*-

# kiwoon api
from kiwoom import *
from kiwoom.tools import *
from gui import *
import ats_version as ats_info

# 환경설정 조건검색
# 'options -> conditions -> {}
OPTIONS = 'options'
OPTIONS_CONDITIONS = 'conditions'
OPTIONS_CONDITIONS_KEY = 'key'
OPTIONS_CONDITIONS_CHECK = 'use'
OPTIONS_CONDITIONS_NAME = 'name'
OPTIONS_CONDITIONS_AMOUNT = 'purchase-amount'
OPTIONS_CONDITIONS_START = 'start'
OPTIONS_CONDITIONS_END = 'end'
OPTIONS_CONDITIONS_METHOD = 'method'



### AUTU TRADING ###
NEW_STOCK = 'new'
REALTIME_STOCK = 'real-time'
CONDITON_STOCK = 'condition'
DESC_STOCK = 'stock'
DESC_FAV = 'fav'

OHLC_DAILY = 'daily_df'
OHLC_DAILY5 = 'daily5_df'
OHLC_DAILY10 = 'daily10_df'
OHLC_DAILY20 = 'daily20_df'
OHLC_DAILY60 = 'daily60_df'
OHLC_DAILY120 = 'daily120_df'

OHLC_MINUTE = 'minute_df'       # default OHLC_MINUTE1 = 'minute1_df'
OHLC_MINUTE3 = 'minute3_df'
OHLC_MINUTE5 = 'minute5_df'
OHLC_MINUTE10 = 'minute10_df'
OHLC_MINUTE20 = 'minute20_df'
OHLC_MINUTE30 = 'minute30_df'
OHLC_MINUTE60 = 'minute60_df'
