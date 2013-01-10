#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 09:36:32
#   Desc    :   逻辑基类
#

from functools import partial
from .util import get_logger
from .db import MySQLContext as MC

class Logic(object):
    """ 逻辑基类 """
    _t = None
    def __init__(self, *args, **kwargs):
        if self._t:
            self._table = self._t
        else:
            self._table = self.__class__.__name__.lower().replace('logic', '')
        self._mc = partial(MC, self._table)
        self.logger = get_logger()
        self.logger.debug("%s init instance", self._table)
        self.init(*args, **kwargs)

    def init(self):
        pass

    def handle_page(self, total, index, size):
        index, size = int(index), int(size)
        totalpage = total / size if total % size == 0 else total / size + 1
        pageindex = index
        pagesize = size
        nextpage = index + 1 if index + 1 <= totalpage else index
        prevpage = index - 1 if index -1 >= 1 else index
        return {'totalpage':totalpage, 'nextpage':nextpage,
                'prevpage':prevpage, 'pageindex': pageindex,
                'pagesize':pagesize}

    def handle_limit(self, index = 1, size = None):
        index, size = int(index), int(size)
        if not size:
            return index
        limit = size
        skip = (index - 1) * size
        return skip, limit

    def handle_insert(self, dic):
        fields = []
        values = []
        for k in dic:
            fields.append(k)
            values.append(dic[k])
        return fields, values

    def error(self, errmsg):
        return {"status": False, "errmsg":errmsg}

    def success(self, data, pageinfo = None):
        result = {"status": True, "data": data}
        if pageinfo:
            result['pageinfo'] = pageinfo
        return result
