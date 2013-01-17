#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 18:39:18
#   Desc    :   链接逻辑
#
from core.logic import Logic

class LinksLogic(Logic):
    def get_all_links(self):
        with self._mc() as op:
            order = {"order":-1}
            return op.select(order = order)

    def add_new_link(self, text, url, order):
        fields = ['text', 'url', 'order']
        values = [text, url, order]
        with self._mc() as op:
            return op.insert(fields, values)

    def update_link_edit(self, lid, set_dict):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(lid))
            return op.update(set_dict, where = where)

    def del_link_by_id(self, _id):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.remove(where = where)

    def get_link_by_id(self, _id):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.select_one(where = where)
