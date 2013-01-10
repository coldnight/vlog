#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 18:38:13
#   Desc    :   评论逻辑
#
from core.logic import Logic
from core.util import md5, utf8sub

#TODO 邮件通知
class CommentLogic(Logic):
    def add_comment(self, pid, comment_dict):
        fields = []
        values = []
        comment_dict['pid'] = pid
        for k in comment_dict:
            fields.append(k)
            values.append(comment_dict[k])

        with self._mc() as op:
            return op.insert(fields, values)

    def allow_comment(self, cid):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(cid))
            set_dict = {"allowed":1}
            op.update(set_dict, where)

    def count_post_comments(self, pid):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.count(where)

    def get_post_comments(self, pid, index = 1, size = 10):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            limit = self.handle_limit(index, size)
            order = {"id":-1}
            count = self.count_post_comments(pid)
            pageinfo = self.handle_page(count, index, size)
            r = op.select(where = where, order = order, limit = limit)
            r = self.insert_info(r)
        return self.success(r, pageinfo)

    def insert_info(self, comments):
        if isinstance(comments, (list, tuple)):
            return [self._insert_info(c) for c in comments]
        if isinstance(comments, dict):
            return self._insert_info(comments)
        return comments

    def _insert_info(self, comment):
        email = comment.get('email', '')
        comment['gravatar'] = md5(email)
        content = comment.get('content')
        comment['short_content'] =  utf8sub(content, 0, 20)
        return comment

    def _insert_post_title(self, comments, titles):
        for comment in comments:
            comment['post_title'] = titles.get(comment.get("pid"))

        return comments

    def remove_comment(self, cid):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(cid))
            op.remove(where = where)

    def get_last_comments(self, postlogic, size = 5):
        with self._mc() as op:
            order = {"id":-1}
            limit = self.handle_limit(size = size)
            r = op.select(order = order, limit = limit)
        pids = [c.get('pid') for c in r]
        titles = postlogic.get_titles(pids)
        comments = self._insert_post_title(r, titles)
        comments = self.insert_info(comments)
        return comments
