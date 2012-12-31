#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 16:58:49
#   Desc    :   类别操作
#
from core.logic import Logic

class post_to_category(Logic):

    def get_post_category(self, pid):
        with self._mc as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.select(where = where)

    def add_post_category(self, pid, cid):
        if self.check_exists(pid, cid):
            return
        with self._mc() as op:
            fields = ['pid', 'cid']
            values = [pid, cid]
            return op.insert(fields, values)

    def check_exists(self, pid, cid):
        with self._mc() as op:
            where = "`pid`='{0}' and `cid`='{1}'".format(op.escape(pid),
                                                         op.escape(cid))
            return op.select_one(where=where)

class CategoryLogic(Logic):
    def add_category(self, pid, name):
        ex = self.check_exists()
        if ex:
            cid = ex.get('id')
        else:
            with self._mc() as op:
                fields = ['name']
                values = [name]
                cid = op.insert(fields, values)

        ptc = post_to_category()
        ptc.add_post_category(pid, cid)
        return cid


    def get_post_category(self, pid):
        ptc = post_to_category()
        cids = ptc.get_post_category(pid)
        result = []
        with self._mc() as op:
            for cid in cids:
                where = "`id`='{0}'".format(op.escape(cid))
                r = op.select_one(where=where)
                result.append(r)
        return result

    def get_category(self, cid = None):
        with self._mc() as op:
            if cid:
                where = "`id`='{0}'".format(op.escape(cid))
                return op.select_one(where=where)
            else:
                return op.select()

    def check_exists(self, name):
        with self._mc() as op:
            where = "`name`='{0}'".format(op.escape(name))
            return op.select_one(where=where)
