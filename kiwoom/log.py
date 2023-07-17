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


