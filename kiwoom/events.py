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
