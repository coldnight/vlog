#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 17:37:34
#   Desc    :   文章逻辑
#
from datetime import datetime, timedelta

from core.logic import Logic


class PostsLogic(Logic):
    def get_max_id(self):
        with self._mc() as op:
            return op.max('id')

    def get_last_post_add_time(self):
        order = {"id":-1}
        with self._mc() as op:
            r = op.select_one(order = order)
            add_time = r.get('add_time')
        if add_time:
            return datetime.fromtimestamp(add_time)
        else:
            return datetime.utcnow() + timedelta(hours =+ 8)

    def count_all_post(self):
        with self._mc() as op:
            return op.count()

    def get_all_article(self):
        with self._mc() as op:
            order = {"id":-1}
            return op.select(order = order)

    def get_post_for_homepage(self):
        with self._mc() as op:
            #TODO 改成可配置的
            return op.select(limit = 10)

    def get_page_posts(self, index = 1, size = 10):
        limit = size
        skip = (index - 1) * size
        with self._mc() as op:
            return op.select(limit = (skip, limit))

    def get_article_by_id_detail(self, _id):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.select_one(where = where)

    def get_article_by_id_simple(self, _id):
        fields = ['id', 'title', 'comment_num', "closecomment", "password"]
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.select_one(fields = fields, where = where)

    def get_article_by_id_edit(self, _id):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.select_one(where = where)

    def add_new_article(self, params):
        fields = []
        values = []
        for k in params:
            fields.append(k)
            values.append(params[k])

        with self._mc() as op:
            op.insert(fields, values)

    def update_post_edit(self, params):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(params.pop('id')))
            set_dict = params
            return op.update(where = where, set_dict = set_dict)

    def update_post_comment(self, num = 1,_id = ''):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            set_dict = {"comment_num":num}
            return op.update(set_dict = set_dict, where = where)

    def get_post_for_sitemap(self, ids=[]):
        where = "`id` in({0})".format(','.jion(ids))
        order = {"id":-1}
        limit = len(ids)
        with self._mc() as op:
            return op.select(where = where, order = order, limit = limit)

    def del_post_by_id(self, _id = ''):
        if id:
            obj = self.get_article_by_id_simple(_id)
            if obj:
                with self._mc() as op:
                    where = "`id`='{0}'".format(op.escape(_id))
                    #TODO 删除文章评论
                    op.remove(where = where)
