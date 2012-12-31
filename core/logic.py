#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 09:36:32
#   Desc    :   逻辑基类
#
from .db import MySQLContext as MC
from functools import partial

class Logic(object):
    """ 逻辑基类 """
    def __init__(self):
        self._table = self.__class__.__name__.lower().rstrip('logic')
        self._mc = partial(MC, self._table)

    def handle_page(self, total, index, size):
        totalpage = total / size if total % size == 0 else total / size + 1
        pageindex = index
        pagesize = size
        nextpage = index + 1 if index + 1 <= totalpage else index
        prevpage = index - 1 if index -1 >= 1 else index
        return {'totalpage':totalpage, 'nextpage':nextpage,
                'prevpage':prevpage, 'pageindex': pageindex,
                'pagesize':pagesize}
