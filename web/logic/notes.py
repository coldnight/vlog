#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/17 18:00:49
#   Desc    :   便签
#
from .comment import CommentLogic

class NotesLogic(CommentLogic):
    _t = "comment"

    def init(self):pass

    def add_note(self, note_dict):
        note_dict['type'] = 1
        fields, values = self.handle_insert(note_dict)
        with self._mc() as op:
            return op.insert(fields, values)

    def get_all_nodes(self):
        with self._mc() as op:
            order = {"id":-1}
            return op.select(order = order)

    def get_notes(self, index = 1, size = 20):
        limit = self.handle_limit(index, size)
        with self._mc() as op:
            order = {"id":-1}
            where = "`type`='1'"
            notes = op.select(where = where, limit = limit, order = order)
            total = op.count(where = where)
        notes = self.insert_info(notes)
        pageinfo = self.handle_page(total, index, size)
        return self.success(notes, pageinfo)

    def add_note_comment(self, nid, comment_dict):
        comment_dict['parent'] = nid
        fields, values = self.handle_insert(comment_dict)
        with self._mc() as op:
            return op.insert(fields, values)

    def get_note_comments(self,nid, index = 1, size = 20):
        limit = self.handle_limit(index, size)
        with self._mc() as op:
            where = "`parent`='{0}'".format(op.escape(nid))
            order = {"id":-1}
            nc = op.select(where = where, order = order, limit = limit)

        return self.insert_info(nc)
