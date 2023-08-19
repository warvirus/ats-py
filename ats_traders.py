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
from baseATS import TraderBase

import numpy as np


class TraderMACD(TraderBase):
    def __init__(self, stock=None):
        super(TraderMACD, self).__init__(stock)

    def processing(self, df):
        """
        트레이딩 ...
        :param df: DataFrame
        :return: 없음
        """
        pass


__modules__ = ['TraderBase', 'TraderMACD']  # [x for x in dir() if x[:2] != '__']


def get_traders():
    return __modules__


def get_trader(class_name):
    if class_name == 'TraderBase':
        return TraderBase()
    elif class_name == 'TraderMACD':
        return TraderMACD()

    # 기본
    else:
        return TraderMACD()


if __name__ == '__main__':
    # while True:

    a = TraderMACD()

    a.stock = None
    print(get_traders())
