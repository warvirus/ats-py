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
