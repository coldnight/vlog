#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 16:58:49
#   Desc    :   分类操作
#
from core.logic import Logic

class post_to_category(Logic):

    def get_post_category(self, pid):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.select(where = where)

    def get_category_ids(self, pid):
        """ 根据文章id获取文章类别id """
        cate = self.get_post_category(pid)
        return [c.get('cid') for c in cate if c.get('cid') is not None]

    def get_post_ids(self, cid):
        """ 根据类别id获取所有文章id """
        with self._mc() as op:
            where = "`cid`='{0}'".format(op.escape(cid))
            r = op.select(where = where)

        return [c.get('pid') for c in r if c.get('pid') is not None]

    def remove(self,pid,  cids):
        with self._mc() as op:
            wids = "','".join(op.escape(cids))
            where = "`pid`='{0}' and `cid` NOT IN('{1}')".format(op.escape(pid),
                                                                 wids)
            op.remove(where = where)


    def add_post_categories(self, pid, cids):
        self.remove(pid, cids)
        return [self.add_post_category(pid, cid) for cid in cids]

    def add_post_category(self, pid, cid):
        exists = self.check_exists(pid, cid)
        if exists:
            return exists.get('id')
        with self._mc() as op:
            fields = ['pid', 'cid']
            values = [pid, cid]
            return op.insert(fields, values)

    def check_exists(self, pid, cid):
        with self._mc() as op:
            where = "`pid`='{0}' and `cid`='{1}'".format(op.escape(pid),
                                                         op.escape(cid))
            return op.select_one(where=where)

    def count_posts(self, cid):
        with self._mc() as op:
            where = "`cid`='{0}'".format(op.escape(cid))
            return op.count(where)

    def remove_cate_post(self, pid):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.remove(where = where)

class CategoryLogic(Logic):
    def init(self):
        self.ptc = post_to_category()

    def add_category(self, name):
        if not name:
            return self.error(u"需给出类别名")
        ex = self.check_exists(name)
        if ex:
            return self.error(u'已存在')

        with self._mc() as op:
            fields = ['name']
            values = [name]
            cid = op.insert(fields, values)
        return self.success({'id':cid, 'name':name})

    def get_categories(self):
        with self._mc() as op:
            r = op.select()

        cate = self.insert_info(r)
        return self.success(cate)

    def insert_info(self, cate):
        if isinstance(cate, dict):
            return self._insert_info(cate)
        if isinstance(cate, (list, tuple)):
            return [self._insert_info(c) for c in cate]
        return cate

    def _insert_info(self, cate):
        _id = cate.get('id')
        posts_num = self.ptc.count_posts(_id)
        cate['post_num'] = posts_num
        return cate

    def add_post_categories(self, pid, cids):
        self.ptc.add_post_categories(pid, cids)

    def get_post_category(self, pid):
        cids = self.ptc.get_category_ids(pid)
        with self._mc() as op:
            wids = "','".join(op.escape(cids))
            where = "`id` IN ('{0}')".format(wids)
            return op.select(where=where)

    def get_post_ids(self, cid):
        return self.ptc.get_post_ids(cid)

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

    def remove_cate_post(self, pid):
        """ 移除文章时移除文章所在类别的映射 """
        self.ptc.remove_cate_post(pid)
