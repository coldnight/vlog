#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wh
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 17:12:41
#   Desc    :   标签
#
from core.logic import Logic

class post_to_tag(Logic):
    def get_post_tag(self, pid):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.select(where = where)

    def add_post_tag(self, pid, tid):
        if self.check_exists(self, pid, tid):
            return

        with self._mc() as op:
            fields = ['pid', 'tid']
            values = [pid, tid]
            return op.insert(fields, values)

    def check_exists(self, pid, tid):
        with self._mc() as op:
            where = "`pid`='{0}' and `tid`='{1}'".format(op.escape(pid),
                                                         op.escape(tid))
            return op.select_one(where=where)

class TagLogic(Logic):
    def __init__(self):
        super(TagLogic, self).__init__()
        self.ptt = post_to_tag()

    def add_tag(self, pid, name):
        with self._mc() as op:
            fields = ['name']
            values = [name]
            tid = op.insert(fields, values)
            self.ptt.add_post_tag(pid, tid)
            return tid

    def get_tag(self):
        with self._mc() as op:
            return op.select()

    def get_post_tag(self, pid):
        tids = self.ptt.get_post_tag(pid)
        result = []
        with self._mc() as op:
            for tid in tids:
                where = "`id`='{0}'".format(op.escape(tid))
                r = op.select(where = where)
                result.append(r)
        return result
