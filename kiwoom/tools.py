# /usr//bin/python
# -*- coding: utf-8 -*-
from tabulate import tabulate
import os
import json
import datetime as dt
import asyncio
import time
import pickle

from .log import *


# DataFrame 출력을 위해 tabulate 패키지 활용
def print_df(df):
    print(tabulate(df, headers='keys', tablefmt='psql'))

async def __asleep_ms(ms):
    await asyncio.sleep(ms / 1000.0)

def _sleep_ms(ms):
    asyncio.run(__asleep_ms(ms))

def sleep_ms(ms):
    time.sleep(ms / 1000.0)
    # _sleep_ms(ms)

def INT(n):
    i = 0
    if n == "" or n is None:
        return i
    else:
        try:
            i = int(n)
        except ValueError as ex:
            if type(n) is str:
                if n[:2] == '--':       ## <-- 키움증권의 버그
                    i = int(n[1:])
                else:
                    logging.error("Integer ValueError {} : {}".format(ex, n))
            else:
                logging.error("Integer ValueError {} : {}".format(ex, n))
    return i


def STR(s):
    if s is None:
        s = ""
    else:
        try:
            s = str(s)
        except ValueError as ex:
            log.error("String ValueError {} : {}".format(ex, s))
    return s


def FLOAT(n):
    f = 0.0
    if n == "" or n is None:
        return f
    else:
        try:
            f = float(n)
        except ValueError as ex:
            log.error("Float ValueError {} : {}".format(ex, n))
    return f


def replace_spaces(string):
    return string.replace(" ", "_")


def remove_spaces(string):
    return string.replace(" ", "")


def recover_spaces(string):
    return string.replace("_", " ")


def load_json_file(filename):
    """
    json 파일을 읽어 들인다.
    :param filename:
    :return:
    """
    result = {}

    if os.path.isfile(filename):
        try:
            with open(filename, 'rt', encoding='utf-8') as json_file:
                result = json.load(json_file)
        except Exception as ex:
            log.error("File read Error ! : {},  {}".format(filename, ex))

    return result

def save_json_file(filename, json_obj, compress: bool = False):
    """
    json 파일을 저장한다.
    :param compress:
    :param filename:
    :param json_obj
    :return:
    """
    try:
        with open(filename, "w", encoding="utf-8", newline='\r\n') as json_file:
            if compress:
                json.dump(json_obj, json_file)
            else:
                json.dump(json_obj, json_file, indent=4, ensure_ascii=False)
    except Exception as ex:
        print("File write Error ! : %s,  %s" % (filename, str(ex)))


def time_diff(dt1, dt2):
    """
    :param dt1:
    :param dt2:
    :return:
    """
    delta = dt.datetime.strptime(dt2, '%Y-%m-%d %H:%M:%S') - dt.datetime.strptime(dt1, '%Y-%m-%d %H:%M:%S')
    return delta.days * 86400 + delta.seconds


def date_diff(dt1, dt2):
    """
    :param dt1:
    :param dt2:
    :return:
    """
    delta = dt.datetime.strptime(dt2, '%Y-%m-%d %H:%M:%S') - dt.datetime.strptime(dt1, '%Y-%m-%d %H:%M:%S')
    return delta.days

def save_to_disk(filename, obj):
    with open(filename, 'wb') as file:
        pickle.dump(obj, file, protocol=2)


def load_from_disk(filename):
    with open(filename, 'rb') as file:
        obj = pickle.load(file)
    return obj


def date2stringf(s):
    s = '{}-{}-{}'.format(s[:4], s[4:6], s[6:8])
    return s

def now2string() -> str:
    now = dt.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")