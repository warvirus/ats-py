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

from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # for UI and user lib
from PyQt5 import QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer

import logging
import os
import datetime as dt
import sys


# ----------------- logging ----------------- #


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


def setLogging(widget, prev_hdr='', logfolder='logs'):
    # log to file
    folder = os.path.join(os.getcwd(), logfolder)
    if os.path.isdir(folder) is not True:
        os.mkdir(folder)

    now = dt.datetime.now()
    filename = '{}{}.log'.format(prev_hdr, now.strftime('%Y%m%d'))
    log_file = os.path.join(folder, filename)
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s: %(levelname)s %(module)s %(funcName)s: %(message)s'))
    logging.getLogger().addHandler(fh)

    # log to messagebox
    # You can format what is printed to text box
    widget.logTextBox = QTextEditLogger(widget)
    widget.logTextBox.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(widget.logTextBox)
    logging.getLogger().setLevel(logging.DEBUG)

    widget.__layoutLogMsg_xx = QVBoxLayout()
    widget.__layoutLogMsg_xx.addWidget(widget.logTextBox.widget)  # layout 설정

    return widget.__layoutLogMsg_xx


# 조건검색 선택 체크 box
# 참고 : https://curioso365.tistory.com/90
class caseTableWidgetItemCheckBox(QTableWidgetItem):
    """ checkbox widget 과 같은 cell 에 item 으로 들어감.
    checkbox 값 변화에 따라, 사용자정의 data를 기준으로 정렬 기능 구현함.
    """

    def __init__(self):
        super().__init__()
        self.setData(Qt.UserRole, 0)

    def __lt__(self, other):
        # print(type(self.data(Qt.UserRole)))
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)

    def my_setdata(self, value):
        # print("my setdata ", value)
        self.setData(Qt.UserRole, value)
        # print("row ", self.row())

class caseCheckBox(QCheckBox):
    def __init__(self, tbl : QTableWidget, row, col, align=Qt.AlignCenter):
        """
        :param item: QTableWidgetItem instance
        """
        super().__init__()

        item = caseTableWidgetItemCheckBox()

        self.item = item
        self.mycheckvalue = 0  # 0 --> unchecked, 2 --> checked
        self.stateChanged.connect(self.__checkbox_change)
        self.stateChanged.connect(self.item.my_setdata)  # checked 여부로 정렬을 하기위한 data 저장
        tbl.setItem(row, col, item)

        # align
        # cell_widget = QWidget()
        # lay_out = QHBoxLayout(cell_widget)
        # lay_out.addWidget(self)
        # lay_out.setAlignment(align)
        # lay_out.setContentsMargins(0, 0, 0, 0)
        # cell_widget.setLayout(lay_out)
        # tbl.setCellWidget(row, col, cell_widget)

        self.setStyleSheet("margin-left:50%; margin-right:50%;")
        tbl.setCellWidget(row, col, self)

    def __checkbox_change(self, checkvalue):
        # print("myclass...check change... ", checkvalue)
        self.mycheckvalue = checkvalue
        # print( "checkbox row= ", self.get_row() )

    def get_row(self):
        return self.item.row()

class caseRadioBox(QRadioButton):
    def __init__(self, item):
        """
        :param item: QTableWidgetItem instance
        """
        super().__init__()
        self.item = item
        self.mycheckvalue = 0  # 0 --> unchecked, 2 --> checked
        # self.stateChanged.connect(self.__checkbox_change)
        # self.stateChanged.connect(self.item.my_setdata)  # checked 여부로 정렬을 하기위한 data 저장

    def __checkbox_change(self, checkvalue):
        # print("myclass...check change... ", checkvalue)
        self.mycheckvalue = checkvalue
        # print( "checkbox row= ", self.get_row() )

    def get_row(self):
        return self.item.row()


def getTableWidgetItem(tbl : QTableWidget, row, col):
    """
    caseCheckBox 으로 생성된 checkBox 의 핸들값
    """
    chbox = tbl.cellWidget(row, col)
    # chbox = cell_widget.layout.itemAt(0)
    # chbox = QHBoxLayout(tbl.cellWidget(row, col)) # .getCheckBox()

    return chbox

# ----------------- Widget ----------------- #


def center(obj):
    qr = obj.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    obj.move(qr.topLeft())


def closeEvent(wnd, event):
    reply = QMessageBox.question(wnd, 'Quit?',
                                 'Are you sure you want to quit?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        if not type(event) == bool:
            event.accept()
        else:
            sys.exit()
    else:
        if not type(event) == bool:
            event.ignore()


def qsleep_ms(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


# ----------------- gui for stocks ----------------- #

def black():
    return QColor(0, 0, 0)


def red():
    return QColor(255, 0, 0)


def pale_pink():
    return QColor(255, 225, 225)


def blue():
    return QColor(0, 0, 255)


def white():
    return QColor(255, 255, 255)


def green():
    return QColor(0, 128, 0)


def deep_pink():
    return QColor(255, 192, 203)


def _get_disp_value(v):
    if isinstance(v, int):
        value = format(v, ',')
    elif isinstance(v, float):
        value = '{:,.02f}'.format(v)
    else:
        value = v

    return value


def _get_disp_color(v, u=None, f=None):
    """
    stock 색상
    :param v: 값
    :param u: 칼라
    :param f: 파라미터
    :return:
    """
    color = black()  # default

    if u is not None:
        color = u
    elif f is not None:
        color = f
    else:
        if isinstance(v, str):
            if v[:1] == '+':
                color = red()
            elif v[:1] == '-':
                color = blue()
        else:
            if v != 0:
                if v > 0:
                    color = red()
                else:
                    color = blue()

    return color


def get_disp_value(v):
    if isinstance(v, list):
        return _get_disp_value(v[0])
    else:
        return _get_disp_value(v)


def get_disp_color(v, u=None, f=None):
    if isinstance(v, list):
        return _get_disp_color(v[0], u=u, f=f)
    else:
        return _get_disp_color(v, u=u, f=f)


def get_disp_align(v, d=None):
    align = Qt.AlignLeft | Qt.AlignVCenter

    if d is not None:
        align = d
    else:
        if isinstance(v, list):
            if len(v) >= 5:
                align = v[4]  # 사용자 align 가 설정되어 있는지 확인
            else:
                align = Qt.AlignRight | Qt.AlignVCenter if isinstance(v[0], int) else Qt.AlignCenter | Qt.AlignVCenter
        else:
            align = Qt.AlignRight | Qt.AlignVCenter if isinstance(v, int) else Qt.AlignCenter | Qt.AlignVCenter

    return align


def chk_fcolor(v):
    """
    forecolor 값이 있는지 확인
    :param v:
    :return:
    """
    # 0 : title
    # 1 : fid
    # 2 : screen id
    # 3 : fore color
    # 4 : back color
    # 5 : users
    if isinstance(v, list) and len(v) >= 4:
        return v[3]  # forecolor 가 설정되어 있는지 확인
    else:
        return None


def extra_str(v):
    """
    문자열에 추가로 표시되어야할 문자가 있을때 추가한다.
    :param v:  v[1] 에서 fid 다음에 있는 문자열에 따라 정해짐
    :return:
    """
    if (isinstance(v, list) and len(v) >= 2) and (isinstance(v[1], list) and len(v[1]) >= 3):
        return v[1][2]
    else:
        return ''


def get_disp_date(v):
    if isinstance(v, list) and len(v) >= 1:
        return '{}/{}/{}'.format(v[0][:4], v[0][4:6], v[0][6:])
    else:
        return '{}/{}/{}'.format(v[:4], v[4:6], v[6:])


def get_disp_time(v):
    if isinstance(v, list) and len(v) >= 1:
        return '{}:{}:{}'.format(v[0][:2], v[0][2:4], v[0][4:])
    else:
        return '{}:{}:{}'.format(v[:2], v[2:4], v[4:])


def get_disp_date_simple(v):
    if isinstance(v, list) and len(v) >= 1:
        return '{}/{}/{}'.format(v[0][2:4], v[0][4:6], v[0][6:])
    else:
        return '{}/{}/{}'.format(v[2:4], v[4:6], v[6:])


def get_disp_percent(v):
    if isinstance(v, list) and len(v) >= 1:
        return '{:,.02f}%'.format(v[0])
    else:
        return '{:,.02f}%'.format(v)


def setTableHeader(tobj, headers=None, row=0, col=None, selectionMode=QAbstractItemView.ContiguousSelection,
                   sectionResizeMode=QHeaderView.Stretch):
    """
    tbl_account_info 의 헤더를 설정한다.
    :param tobj:
    :param headers:
    :param row:
    :param col:
    :param selectionMode:
    :param sectionResizeMode:
    :return:
    """
    tobj.setRowCount(row)
    tobj.setAlternatingRowColors(False)
    tobj.setSelectionMode(selectionMode)
    tobj.horizontalHeader().setSectionResizeMode(sectionResizeMode)
    tobj.setFocusPolicy(Qt.StrongFocus)
    tobj.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit mode
    if headers is not None:
        tobj.setColumnCount(len(headers) if col is None else col)
        tobj.setHorizontalHeaderLabels(headers)
    else:
        tobj.setColumnCount(col if col is not None else 0)


def setTableWidgetItem(t_obj, row, col, v, f_color=None, b_color=None, extra_s=None,
                       align=Qt.AlignCenter | Qt.AlignVCenter, sort=False):
    """
    특정 QTableWidget 에 문자/숫자를 입력하는 함수
    :param t_obj:
    :param row:
    :param col:
    :param v:
    :param f_color:
    :param b_color:
    :param extra_s:
    :param align:
    :param sort:
    :return:
    """

    # 문자열로 변경
    if isinstance(v, int) or isinstance(v, float):
        v = str(v)

    itemX = QTableWidgetItem(v + (extra_s if extra_s is not None else ''))
    if sort:  # sort 지원
        itemX.setData(Qt.DisplayRole, v)
        # itemX.setData(Qt.UserRole, v)

    itemX.setTextAlignment(align)
    if f_color is not None:
        itemX.setForeground(QBrush(f_color))

    if b_color is not None:
        itemX.setBackground(QBrush(b_color))
    t_obj.setItem(row, col, itemX)


def setTableWidgetItemEx(t_obj, row, col, v, f_color=None, b_color=None, extra_s=None,
                         align=Qt.AlignCenter | Qt.AlignVCenter, sort=False):
    """
    특정 QTableWidget 에 문자/숫자를 입력하는 함수2
    :param t_obj:
    :param row:
    :param col:
    :param v:
    :param f_color:
    :param b_color:
    :param extra_s:
    :param align:
    :param sort:
    :return:
    """

    itemX = QTableWidgetItem(get_disp_value(v) + (extra_s if extra_s is not None else ''))
    if sort: #  and (isinstance(v, int) or isinstance(v, float)):  # sort 지원
        itemX.setData(Qt.DisplayRole, v)
        # itemX.setData(Qt.UserRole, v)

    itemX.setTextAlignment(align)
    itemX.setForeground(QBrush(get_disp_color(v, f_color)))
    if b_color is not None:
        itemX.setBackground(QBrush(b_color))
    t_obj.setItem(row, col, itemX)


def is_trading_time(h, m, s, wday):
    """
    자동매매 가능한 시간인지 확인
    :param h:
    :param m:
    :param s:
    :return:
    """

    result = False

    # 평일 (9 ~ 3:29) 만 거래가 가능하다.
    # wday_list = ['월', '화', '수', '목', '금', '토', '일']
    if 0 <= wday <= 4:  # 평일인지?
        hh = (h * 100) + m
        if 900 <= hh < 1530:
            result = True

    return result

# ------------------
