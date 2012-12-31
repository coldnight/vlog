#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 09:35:17
#   Desc    :   信息类
#
from core.logic import Logic

class InfoLogic(Logic):
    theme_key = 'theme'
    title_key = 'title'
    desc_key = 'desc'

    def get_info(self, key, owner='global', default=None):
        with self._mc() as op:
            where = "`key`='{0}' owner='{1}'".format(op.escape(key),
                                                     op.escape(owner))
            r = op.select_one(where = where).get('value')
            if default:
                r = r if r else default
            return r

    def add_info(self, key, value, owner='global'):
        with self._mc() as op:
            if self.get_info(key):
                where = "`key`='{0}' owner='{1}'".format(op.escape(key),
                                                        op.escape(owner))
                set_dict = {'value':value, 'owner':owner}
                return op.update(set_dict, where)
            else:
                fields = ('key', 'value', 'owner')
                values = (key, value, owner)
                return op.insert(fields, values)

    def set_theme(self, name):
        return self.add_info(self.theme_key, name)

    def get_theme(self):
        return self.get_info(self.theme_key, default='default')

    def set_title(self, title):
        return self.add_info(self.title_key, title)

    def get_title(self):
        return self.get_info(self.title_key)

    def set_desc(self, desc):
        return self.add_info(self.desc_key, desc)

    def get_desc(self):
        return self.get_info(self.desc_key)
