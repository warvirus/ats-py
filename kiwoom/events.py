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


from PyQt5.QtCore import QEventLoop, QTimer
import threading


class event_list_single:
    """
    """

    def __init__(self, name: str = None, timeout_ms=-1, callback: callable = None):
        self.event_loop = QEventLoop()
        self.cnt = 0
        self._name = name if name is not None else threading.currentThread().getName()
        self._timeout_ms = timeout_ms
        self._callback = callback

    def __del__(self):
        self.cnt = 0

    @property
    def timeout(self):
        return self._timeout_ms

    @timeout.setter
    def timeout(self, value):
        self._timeout_ms = value

    def push(self, timeout_ms: int = -1):
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, self.timeout_slot2)  # self.event_loop.quit)
        elif self._timeout_ms > 0:
            QTimer.singleShot(self._timeout_ms, self.timeout_slot1)  # self.event_loop.quit)
        self.cnt += 1
        self.event_loop.exec_()

    def pop(self):
        self.event_loop.exit(1)
        self.cnt -= 1

    def timeout_slot1(self):
        if self.cnt > 0:
            if self._callback is None:
                print("{} : 시간초과".format(self._name))
            else:
                callable(self._callback(self._name))
            self.pop()

    def timeout_slot2(self):
        if self.cnt > 0:
            if self._callback is None:
                print("{} : 시간초과".format(self._name))
            else:
                callable(self._callback(self._name))
            self.pop()
