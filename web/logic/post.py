#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 10:04:12
#   Desc    :   文章逻辑
#
import datetime
from core.logic import Logic
from core.util import NOW, utf8sub
from .tag import TagLogic
from .category import CategoryLogic
from .user import UserLogic
from .comment import CommentLogic

class PostLogic(Logic):
    def init(self):
        self.tl = TagLogic()
        self.cl = CategoryLogic()
        self.ul = UserLogic()
        self.comment = CommentLogic(self)

    def get_new_id(self):
        with self._mc() as op:
            order = {'id':-1}
            _id = op.select_one(order = order).get('id')
            _id = _id if _id else 0
        return self.sucess(_id + 1)

    def count_posts(self, where =  None):
        with self._mc() as op:
            return self.success(op.count(where = where))

    def get_posts(self, index = 1, size = 10):
        with self._mc() as op:
            order = {"id":-1}
            limit = self.handle_limit(index, size)
            where = "`enabled`='1' and `type`='1'"
            r = op.select(where = where, order = order, limit = limit)
        if r:  r= self.insert_info(r)
        total = self.count_posts().get('data')
        page_info = self.handle_page(total, index, size)
        return self.success(r, page_info)

    def get_all_posts(self):
        with self._mc() as op:
            where = "`enabled`='1' and `type`='1'"
            return op.select(where = where)

    def get_post_by_id(self, _id):
        with self._mc() as op:
            where = "`id`='{0}' and `enabled`='1'"\
                    " and `type`='1'".format(op.escape(_id))
            r = op.select_one(where = where)

        if r:
            r = self.insert_info(r)
        return self.success(r)

    def get_titles(self, ids = None, size = 5):
        """ 根据id获取文章标题或者后去最新10篇文章的标题 """
        with self._mc() as op:
            if ids:
                wids = "','".join(op.escape(ids))
                where = "`id` in ('{0}')".format(wids)
                posts = op.select(where = where)
            else:
                where = "`type`='1' and `enabled`='1'"
                limit = self.handle_limit(size = size)
                order = {"id":-1}
                posts = op.select(where = where, order = order, limit = limit )
        result = {}
        [result.update({p.get('id'):p.get('title')}) for p in posts]
        return result

    def get_new(self):
        posts = self.get_titles()
        posts = [{'id':key, 'title':value} for key, value in posts.items()]
        posts = sorted(posts, key = lambda x:x['id'], reverse = True)
        return posts

    def get_months(self):
        """ 获取所有文章归档年月 """
        with self._mc() as op:
            all_post = op.select()
        result = []
        for p in all_post:
            date = p.get("date")
            year = date.year
            month = date.month
            dst = datetime.datetime(year, month, 1)
            info = {"year":year, "month":month, "date":dst}
            if info not in result:
                result.append(info)
        result = sorted(result, key = lambda r: r['date'], reverse = True)
        return result

    def get_by_month(self, year, month, index = 1, size = 10):
        year, month = int(year), int(month)
        nmonth, nyear = (month + 1, year) if month + 1 <= 12 else (1, year + 1)
        with self._mc() as op:
            where = "`date` >= '{0}-{1}-1' and `type`='1' and enabled='1' and "\
                    "`date` < '{2}-{3}-1'".format(year, month, nyear, nmonth)
            order = {"id":-1}
            limit = self.handle_limit(index, size)
            posts = op.select(where = where, order = order, limit = limit)
            total = op.count(where = where)
        pageinfo = self.handle_page(total, index, size)
        if posts:
            posts = self.insert_info(posts)
        return self.success(posts, pageinfo)

    def get_post_by_ids(self, ids, index = 1, size = 10):
        limit = self.handle_limit(index, size)
        with self._mc() as op:
            wids = "','".join(op.escape(ids))
            where = "`id` in ('{0}') and `enabled`='1' "\
                    "and `type`='1'".format(wids)
            order = {"id":-1}
            posts = op.select(where = where, order = order, limit = limit)
        total = self.count_posts(where).get("data")
        if posts:
            posts = self.insert_info(posts)
        page_info = self.handle_page(total, index, size)
        return self.success(posts, page_info)

    def get_post_by_category(self, cid, index = 1, size = 10):
        pids = self.cl.get_post_ids(cid)
        return self.get_post_by_ids(pids, index, size)

    def get_post_by_tag(self, tid, index = 1, size = 10):
        pids = self.tl.get_post_ids(tid)
        return self.get_post_by_ids(pids, index, size)

    def post(self, post_dict):
        tags = post_dict.pop('tags', None)
        category = post_dict.pop('category', None)
        fields = []
        values = []
        post_dict['update'] = NOW()
        for p in post_dict:
            fields.append(p)
            values.append(post_dict[p])

        with self._mc() as op:
            pid = op.insert(fields, values)

        if isinstance(tags, (str, unicode)):
            tags = tags.split(',')
        if isinstance(category, (str, unicode)):
            category = category.split(',')

        if tags:
            self.tl.add_post_tags(pid, tags)
        if category:
            self.cl.add_post_categories(pid, category)
        return self.success(pid)

    def insert_info(self, posts):
        if isinstance(posts, (list, tuple)):
            return [self._insert_info(p) for p in posts]
        if isinstance(posts, dict):
            return self._insert_info(posts)
        return posts

    def _insert_info(self, post):
        _id = post.get('id')
        tags = self.tl.get_post_tags(_id)
        category = self.cl.get_post_category(_id)
        author_id = post.get('author')
        post['author'] = self.ul.get_user_by_id(author_id)
        post['tags'] = tags
        post["ttags"] = ','.join([t.get('name') for t in tags])
        post['category'] = category
        post['cids'] = [c.get('id') for c in category]
        post['comment_num'] = self.comment.count_post_comments(_id)
        post['short_content'] = utf8sub(post.get('content'), 0, 200)
        return post

    def edit(self, pid, post_dict):
        tags = post_dict.pop('tags', None)
        category = post_dict.pop('category', None)
        if isinstance(tags, (str, unicode)):
            tags = tags.split(',')
        if isinstance(category, (str, unicode)):
            category = category.split(',')

        if tags:
            self.tl.add_post_tags(pid, tags)
        if category:
            self.cl.add_post_categories(pid, category)
        post_dict['update'] = NOW()
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(pid))
            op.update(post_dict, where = where)

        return self.success(pid)

    def remove(self, pid):
        #TODO 改成禁用
        self.tl.remove_tag_post(pid)
        self.cl.remove_cate_post(pid)
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(pid))
            return op.remove(where=where)
