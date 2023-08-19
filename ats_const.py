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
