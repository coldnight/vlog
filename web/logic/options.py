#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/08 12:55:37
#   Desc    :   提供一个Key-Value的选项
#
from core.logic import Logic

class Options(Logic):
    """ 提供一个Key-Value的选项
        `owner` --- 区分选项拥有者的标志 default: global
    """
    def init(self, owner="global"):
        self._owner = owner

    def get_option(self, key):
        owner = self._owner
        with self._mc() as op:
            where = "`key`='{0}' and `owner`='{1}'".format(op.escape(key),
                                                           op.escape(owner))
            return op.select_one(where = where).get('value')

    def set_option(self, key, value):
        owner = self._owner
        with self._mc() as op:
            if self.get_option(key):
                where = "`key`='{0}' and `owner`='{1}'".format(op.escape(key),
                                                           op.escape(owner))
                set_dict = {"value":value}
                op.update(set_dict, where=where)
            else:
                fields = ['key', 'value', 'owner']
                values = [key, value, owner]
                op.insert(fields, values)
        return

    def get_all_option(self):
        owner = self._owner
        with self._mc() as op:
            where = "`owner`='{0}'".format(op.escape(owner))
            r = op.select(where = where)
            return r

    def get_all_key(self):
        result = self.get_all_option()
        return [r.get("key") for r in result]

class BaseOption(object):
    option = None      # 子类覆盖option
    def __getattr__(self, key):
        return self.option.get_option(key)

    def __setattr__(self, key, value):
        self.option.set_option(key, value)


class GlobalOption(BaseOption):
    option = Options('global')
