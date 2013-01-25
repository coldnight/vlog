#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 17:12:41
#   Desc    :   标签
#
from core.logic import Logic

class post_to_tag(Logic):
    def get_post_tags(self, pid):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.select(where = where)

    def get_post_tids(self, pid):
        tags = self.get_post_tags(pid)
        return [t.get('tid') for t in tags]

    def get_tag_pids(self, tid):
        with self._mc() as op:
            where = "`tid`='{0}' and `enabled`='0'".format(op.escape(tid))
            r = op.select(where = where)
            return [p.get('pid') for p in r]


    def remove(self, pid, tids):
        with self._mc() as op:
            wids = "','".join(op.escape(list(set(tids))))
            where = "`pid`='{0}' and `tid` NOT IN('{1}')".format(op.escape(pid),
                                                                 wids)
            op.remove(where = where)

    def add_post_tags(self, pid, tids):
        self.remove(pid, tids)
        return [self.add_post_tag(pid, tid) for tid in tids]

    def add_post_tag(self, pid, tid):
        exists = self.check_exists(pid, tid)
        if exists:
            return exists.get('id')

        with self._mc() as op:
            fields = ['pid', 'tid']
            values = [pid, tid]
            return op.insert(fields, values)

    def count_posts(self, tid):
        with self._mc() as op:
            where = "`tid`='{0}' and `enabled`='1'".format(op.escape(tid))
            return op.count(where)


    def check_exists(self, pid, tid):
        with self._mc() as op:
            where = "`pid`='{0}' and `tid`='{1}'"\
                    .format(op.escape(pid), op.escape(tid))
            return op.select_one(where=where)

    def remove_tag_post(self, pid):
        """ 删除文章后删除文章到标签的映射 """
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            return op.remove(where = where)

    def disable(self, pid):
        """ 禁用文章时禁用标签 """
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            set_dic = {"enabled":0}
            return op.update(set_dic, where)

    def enable(self, pid):
        with self._mc() as op:
            where = "`pid`='{0}'".format(op.escape(pid))
            set_dict = {"enabled":1}
            return op.update(set_dict, where = where)

class CategoryLogic(Logic):
    def init(self):
        self.ptc = post_to_category()

    def add_category(self, name):
        nostr = [' ', '+', '&', '#', '/', '?', '%', '=']
        if [n for n  in nostr if n in name]:
            return self.error(u"不允许的特殊字符")
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

class TagLogic(Logic):
    def init(self):
        self.ptt = post_to_tag()

    def add_post_tags(self, pid, tags, pub = True):
        tids = []
        with self._mc() as op:
            for name in tags:
                tid = self.check_exists(name)
                if tid:
                    tids.append(tid)
                    continue
                fields = ['name']
                values = [name]
                tid = op.insert(fields, values)
                tids.append(tid)
        self.ptt.add_post_tags(pid, tids)
        if not pub: self.disable(pid)
        return tids

    def get_tags(self):
        with self._mc() as op:
            r = op.select()
        tags = self.insert_info(r)
        return self.success(tags)

    def get_tag(self, tid):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(tid))
            r = op.select_one(where = where)

        return r

    def insert_info(self, tags):
        if isinstance(tags, dict):
            return self._insert_info(tags)
        if isinstance(tags, (list, tuple)):
            return [self._insert_info(t) for t in tags]
        return tags

    def _insert_info(self, tag):
        _id = tag.get('id')
        posts_num = self.ptt.count_posts(_id)
        tag['post_num'] = posts_num
        return tag

    def check_exists(self, name):
        with self._mc() as op:
            where = "`name`='{0}'".format(op.escape(name))
            return op.select_one(where = where).get('id')

    def get_post_tags(self, pid):
        tids = self.ptt.get_post_tids(pid)
        result = []
        with self._mc() as op:
            for tid in tids:
                where = "`id`='{0}'".format(op.escape(tid))
                r = op.select_one(where = where)
                result.append(r)
        return result

    def get_post_ids(self, tid):
        return self.ptt.get_tag_pids(tid)

    def remove(self, tid):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(tid))
            return op.remove(where=where)

    def remove_tag_post(self, pid):
        """ 移除文章后删除对应的标签 """
        tids = self.ptt.get_post_tids(pid)
        r = self.ptt.remove_tag_post(pid)
        # 如果标签文章数为0则移除标签
        for tid in tids:
            post_num = self.ptt.count_posts(tid)
            if int(post_num) == 0:
                self.remove(tid)
        return r

    def disable(self, pid):
        """ 禁用文章到标签的映射 """
        self.ptt.disable(pid)

    def enable(self, pid):
        self.ptt.enable(pid)
