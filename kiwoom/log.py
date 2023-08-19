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

import logging

class log():
    def info(self, *args, **kwargs):
        logging.info(*args, **kwargs)

    def log(self, *args, **kwargs):
        logging.log(*args, **kwargs)

    def debug(self, *args, **kwargs):
        logging.debug(*args, **kwargs)

    def warning(self, *args, **kwargs):
        logging.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        logging.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        logging.critical(*args, **kwargs)


