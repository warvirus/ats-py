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

import sys
from eventhandler import EventHandler
from .events import event_list_single
from .tools import *

DEFAULT_NOWAIT = 0
DEFAULT_WAIT = 0.5


class transaction:
    def __init__(self, _req_comm, tr_name: str, seq: int, event_slot: event_list_single = None,
                 callback: callable = None, func_name: str = '', stream_output=sys.stdout,
                 wait: float = DEFAULT_NOWAIT):
        self._tr_name: str = tr_name
        self._req_comm = _req_comm
        self._seq: int = seq
        self._event_slot: event_list_single = event_slot
        self._callback: callable = callback
        self._pop: bool = True
        self._wait: float = wait
        self._push: bool = True
        self._seq_sub: int = 0
        self._seq_time = time.time_ns()
        self._start = self._seq_time
        self._result: bool = False
        self._stream_output = stream_output
        self._func_name = func_name
        self._result_data = None
        self._msg = ''

    @property
    def tr_name(self):
        return self._tr_name

    @property
    def func_name(self):
        return self._func_name

    @property
    def seq(self):
        return self._seq

    @property
    def pop(self):
        return self._pop

    @pop.setter
    def pop(self, value: bool):
        self._pop = value

    @property
    def wait(self):
        return self._wait

    @wait.setter
    def wait(self, value):
        self._wait = value

    @property
    def push(self):
        return self._push

    @push.setter
    def push(self, value: bool):
        self._push = value

    @property
    def seq_sub(self):
        return self._seq_sub

    @seq_sub.setter
    def seq_sub(self, value: int):
        self._seq_sub = value
        self._seq_time = time.time_ns()

    @property
    def diff_tran_ns(self):
        return time.time_ns() - self._start

    @property
    def diff_tran(self):
        return self.diff_tran_ns / 1000000000.0

    @property
    def diff_task_ns(self):
        return time.time_ns() - self._seq_time

    @property
    def diff_task(self):
        return self.diff_task_ns / 1000000000.0

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    @property
    def result(self) -> bool:
        return self._result

    @result.setter
    def result(self, value: bool):
        self._result = value

    @property
    def result_data(self):
        return self._result_data

    @result_data.setter
    def result_data(self, value):
        self._result_data = value

    @property
    def message(self) -> str:
        return self._msg

    @message.setter
    def message(self, value: str):
        self._msg = value

    """
    def callback(self, *args, **kwargs) -> bool:
        ok: bool = True
        if self._callback is not None:
            DEBUG = True
            if DEBUG:
                ok = self._callback(*args, **kwargs)
            else:
                try:
                    ok = self._callback(*args, **kwargs)
                except Exception as e:
                    ok = False
                    print(f'WARNING: {str(self._callback.__name__)} produces an exception error.',
                          file=self._stream_output)
                    print('Arguments', args, file=self._stream_output)
                    print(e, file=self._stream_output)
            # endif
        # endif
        return ok
    """

    def event_handler_push(self):
        if self._event_slot is not None:
            self._event_slot.push()

    def event_handler_pop(self):
        if self._event_slot is not None:
            self._event_slot.pop()

    def set_next(self, wait=None, push: bool = False, pop: bool = False, result: bool = False):
        if wait is not None:
            self._wait = wait
        self._push = push
        self._pop = pop
        self._result = result

    def set_terminate(self, push: bool = False, pop: bool = True, result: bool = True):
        self._wait = DEFAULT_NOWAIT
        self._push = push
        self._pop = pop
        self._result = result

    def set_req_next(self, b: bool, wait=None) -> bool:
        if b:
            self.set_next(wait=wait)
        else:
            self.set_terminate()
        return b


class req_comm:
    def __init__(self, api, tr_name, tr_info: transaction = None, func_name: str = '', stream_output=sys.stdout):
        self._api = api
        self._input_value = []
        self._callback: callable = None  # public callback
        self._stream_output = stream_output
        self._func_name = func_name
        self._tr_name = tr_name
        self._tr_info = tr_info

        # 트랜잭션 정보를 만든다.
        self._tr_info = self._api.comm_make_rq(tr_name, opt=self)

    @property
    def tr_info(self) -> transaction:
        return self._tr_info

    def set_callback(self, callback: callable):
        if EventHandler.is_callable(callback):
            self._tr_info.callback = callback
        else:
            print(f'Can not link callback, not registered.', file=self._stream_output)
            self._tr_info.callback = None

    def wait(self):
        if self._tr_info is not None and self._tr_info.wait > DEFAULT_NOWAIT:
            sleep_ms(self._tr_info.wait * 1000.0)

    def make_transaction(self, tr_name: str, seq: int, event_slot: event_list_single, wait: float = DEFAULT_WAIT) \
            -> transaction:
        if self._tr_info is None:
            return transaction(self, tr_name, seq, event_slot, self._callback, func_name=self._func_name,
                               stream_output=self._stream_output)
        else:
            self._tr_info.seq_sub += 1  # seq - self._tr_info.seq
            self._tr_info.wait = wait
            return self._tr_info

    # def set_callback(self, callback: callable):
    #    self._callback = callback

    def set_input_value(self, id, value):
        v = [id, value]
        self._input_value.append(v)

    def comm_make_rq(self, rq_name, tr_code):
        self._api.com_make_rq(rq_name, tr_code, opt=self)

    def comm_rq_data(self, rq_name, tr_code, b_next, screen_no, error: int = None, timeout_ms: int = -1):
        # waiting...
        self.wait()

        for iv in self._input_value:
            self._api.set_input_value(iv[0], iv[1])
        return self._api.comm_rq_data(rq_name, tr_code, b_next, screen_no, opt=self,
                                      error=error, timeout_ms=timeout_ms)
