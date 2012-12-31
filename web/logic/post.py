#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 10:04:12
#   Desc    :   文章逻辑
#
from core.logic import Logic
from .tag import TagLogic
from .category import CategoryLogic

class PostLogic(Logic):
    def __init__(self):
        super(PostLogic, self).__init__()
        self.tl = TagLogic()
        self.cl = CategoryLogic()

    def handle_id(self):
        with self._mc() as op:
            order = {'id':-1}
            _id = op.select_one(order = order).get('id')
            _id = _id if _id else 0
            return _id + 1

    def post(self, post_dict):
        tags = post_dict.pop('tags')
        category = post_dict.pop('category')
        fields = []
        values = []
        for p in post_dict:
            fields.append(p)
            values.append(post_dict[p])

        with self._mc() as op:
            pid = op.insert(fields, values)

        if isinstance(tags, (str, unicode)):
            tags = tags.split(',')
        if isinstance(category, (str, unicode)):
            category = category.split(',')

        [self.tl.add_tag(pid, tag) for tag in tags]
        [self.cl.add_category(pid, cate) for cate in category]
        return pid

    def get_list(self, index = 1, size = 10):
        skip = (index -1) * size
        limit = size
        with self._mc() as op:
            r = op.select(limit = (skip, limit), order = {'date':-1})
            count = op.count()

        page_info = self.handle_page(count, index, size)
        r = [self._insert_info(p.get('id'), p) for p in r]
        return {'data':r, 'pageinfo':page_info}

    def _insert_info(self, _id, post):
        tags = self.tl.get_post_tag(_id)
        category = self.cl.get_post_category(_id)
        post['tags'] = tags
        post['category'] = category
        return post

    def get_post(self, _id):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            post = op.select_one(where)
        return self._insert_info(_id, post)

    def edit(self, _id, post_dict):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.update(post_dict, where = where)
