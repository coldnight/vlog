#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 10:04:12
#   Desc    :   文章逻辑
#
import re
from core.logic import Logic
from core.util import NOW
from .tag import TagLogic
from .category import CategoryLogic
from .user import UserLogic
from .comment import CommentLogic

class PostLogic(Logic):
    short = re.compile(r"<p>(.*?)</p>", re.S)
    def init(self):
        self.tl = TagLogic()
        self.cl = CategoryLogic()
        self.ul = UserLogic()
        self.comment = CommentLogic(self)

    def count_posts(self, where =  None):
        """ 根据条件统计文章 """
        with self._mc() as op:
            return self.success(op.count(where = where))

    def get_posts(self, index = 1, size = 10):
        """ 分页获取发布文章 """
        with self._mc() as op:
            order = {"id":-1}
            limit = self.handle_limit(index, size)
            where = "`enabled`='1' and `type`='1' and `isdraft`='0'"
            r = op.select(where = where, order = order, limit = limit)
        if r:  r= self.insert_info(r)
        total = self.count_posts(where = where).get('data')
        page_info = self.handle_page(total, index, size)
        return self.success(r, page_info)

    def get_all_posts(self):
        """ 获取发布的全部文章 """
        with self._mc() as op:
            where = "`enabled`='1' and `type`='1' and `isdraft`='0'"
            return op.select(where = where)

    def get_post_by_id(self, _id):
        """ 根据文章id获取文章 """
        with self._mc() as op:
            where = "`id`='{0}' and `enabled`='1' and `isdraft`='0'"\
                    " and `type`='1'".format(op.escape(_id))
            r = op.select_one(where = where)
        if r:
            r = self.insert_info(r)
        return self.success(r)

    def get_post_by_link(self, link_title, typ = 1):
        """ 根据链接标题获取文章 """
        with self._mc() as op:
            where = "`link_title`='{0}' and `enabled`='1'"\
                    " and `isdraft`='0' and `type`='{1}'"\
                    .format(op.escape(link_title), op.escape(typ))
            r = op.select_one(where = where)
        if r:
            r = self.insert_info(r)
        return self.success(r)

    def get_titles(self, ids = None, size = 5):
        """ 根据id获取文章标题或者后去最新10篇文章的标题 """
        with self._mc() as op:
            if ids:
                ids = list(set(ids))
                wids = "','".join(op.escape(ids))
                where = "`id` in ('{0}')".format(wids)
                posts = op.select(where = where)
            else:
                where = "`type`='1' and `enabled`='1' and `isdraft`='0'"
                limit = self.handle_limit(size = size)
                order = {"id":-1}
                posts = op.select(where = where, order = order, limit = limit )
        result = {
            p.get("id") : {
                "title":p.get("title"),
                "link_title":p.get("link_title"),
                "date":p.get("pubdate")
            } for p in posts }
        return result

    def get_new(self, size = 5):
        """ 获取最新的5篇文章 """
        with self._mc() as op:
            where = "`type`='1' and `enabled`='1' and `isdraft`='0'"
            limit = self.handle_limit(size = size)
            order = {"id":-1}
            return op.select(where = where, order = order, limit = limit)

    def get_months(self):
        """ 获取所有文章归档年月 """
        with self._mc() as op:
            order = {"pubdate":-1}
            all_post = op.select(order = order)
        result = []
        for p in all_post:
            date = p.get("pubdate")
            year = date.year
            month = date.month
            info = {"year":year, "month":month}
            if info not in result:
                result.append(info)
        return result

    def get_by_month(self, year, month, index = 1, size = 10):
        """ 获取某一月份的全部文章 """
        year, month = int(year), int(month)
        nmonth, nyear = (month + 1, year) if month + 1 <= 12 else (1, year + 1)
        with self._mc() as op:
            where = "`pubdate` >= '{0}-{1}-1' and `type`='1' and enabled='1' and "\
                    "`pubdate` < '{2}-{3}-1' and `isdraft`='0'"\
                    .format(year, month, nyear, nmonth)
            order = {"id":-1}
            limit = self.handle_limit(index, size)
            posts = op.select(where = where, order = order, limit = limit)
            total = op.count(where = where)
        pageinfo = self.handle_page(total, index, size)
        if posts:
            posts = self.insert_info(posts)
        return self.success(posts, pageinfo)

    def get_archives(self):
        """ 获取文章归档 """
        with self._mc() as op:
            order = {"pubdate":-1}
            where = "`enabled`='1' and `type`='1' and `isdraft`='0'"
            posts = op.select(where = where, order =order)
        info = {}
        for p in posts:
            p = self._insert_info(p)
            date = p.get("pubdate")
            year = date.year
            month = date.month
            key = "{0}-{1}".format(year, month)
            if info.has_key(key):
                info[key]["posts"].append(p)
            else:
                info[key] = {}
                info[key]["year"] = year
                info[key]["month"] = month
                info[key]["posts"] = [p]
                info[key]["date"] = date

        result = [value for key, value in info.items()]
        result = sorted(result, key=lambda x:x["date"], reverse=True)
        return result

    def get_post_by_ids(self, ids, index = 1, size = 10):
        """ 根据所指定的id来获取相应的文章 """
        limit = self.handle_limit(index, size)
        with self._mc() as op:
            wids = "','".join(op.escape(ids))
            where = "`id` in ('{0}') and `enabled`='1' "\
                    "and `type`='1' and `isdraft`='0'".format(wids)
            order = {"id":-1}
            posts = op.select(where = where, order = order, limit = limit)
        total = self.count_posts(where).get("data")
        if posts:
            posts = self.insert_info(posts)
        page_info = self.handle_page(total, index, size)
        return self.success(posts, page_info)

    def get_post_by_category(self, cid, index = 1, size = 10):
        """ 根据分类id获取文章 """
        pids = self.cl.get_post_ids(cid)
        return self.get_post_by_ids(pids, index, size)

    def get_post_by_tag(self, tid, index = 1, size = 10):
        """ 根据标签id获取文章 """
        pids = self.tl.get_post_ids(tid)
        return self.get_post_by_ids(pids, index, size)

    def post(self, post_dict):
        """ 提交文章 """
        if not post_dict.has_key("isdraft"):
            post_dict['isdraft'] = 0
        pub = False if post_dict['isdraft'] == 0 else True
        tags = post_dict.pop('tags', None)
        category = post_dict.pop('category', None)
        fields ,values = [], []
        if not post_dict.has_key("pubdate"):
            post_dict['pubdate'] = NOW()
        if not post_dict.has_key("link_title") and pub:
            post_dict['link_title'] = self.get_link_title(post_dict.get("title"))
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
            self.tl.add_post_tags(pid, tags, pub)
        if category:
            self.cl.add_post_categories(pid, category, pub)
        return self.success(pid)

    def insert_info(self, posts):
        if isinstance(posts, (list, tuple)):
            return [self._insert_info(p) for p in posts]
        if isinstance(posts, dict):
            return self._insert_info(posts)
        return posts

    def _insert_info(self, post):
        """ 插入文章的附加信息:分类,标签,作者 """
        _id = post.get('id')
        tags = self.tl.get_post_tags(_id)
        category = self.cl.get_post_category(_id)
        author_id = post.get('author')
        post['author'] = self.ul.get_user_by_id(author_id)
        post['date'] = post.get("pubdate")
        post['tags'] = tags
        post["ttags"] = ','.join([t.get('name') for t in tags])
        keywords = ','.join([c.get('name') for c in category])
        post["keywords"] = keywords + "," + post.get("ttags")
        post['category'] = category
        post['cids'] = [c.get('id') for c in category]
        post['comment_num'] = self.comment.count_post_comments(_id)
        post['short_content'] = self.get_short_content(post.get("content"))
        return post

    def edit(self, pid, post_dict):
        """ 编辑文章 """
        if not post_dict.has_key("isdraft"):
            post_dict['isdraft'] = 0
        if post_dict['isdraft'] == 1:
            post_dict["post_parent"] = pid
            return self.post(post_dict)
        post_dict["update"] = NOW()
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
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(pid))
            op.update(post_dict, where = where)
        return self.success(pid)

    def disable(self, pid):
        """ 禁用文章 """
        self.tl.disable(pid)
        self.cl.disable(pid)
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(pid))
            set_dict = {"enabled":0}
            return op.update(set_dict, where)

    def enable(self, pid):
        self.tl.enable(pid)
        self.cl.enable(pid)
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(pid))
            set_dict = {"enabled":1}
            return op.update(set_dict, where)

    def remove(self, pid):
        """ 根据文章id移除文章 """
        self.tl.remove_tag_post(pid)
        self.cl.remove_cate_post(pid)
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(pid))
            return op.remove(where=where)

    def get_drafts(self, index = 1, size = 10):
        """ 获取草稿, 给定pid则获取改pid的草稿 """
        with self._mc() as op:
            order = {"id":-1}
            where = "`isdraft`='1'"
            limit = self.handle_limit(index, size)
            r = op.select(where = where, order = order, limit = limit)
            total = self.count_posts(where = where)
        posts = self.insert_info(r)
        pageinfo = self.handle_page(total, index, size)
        return self.success(posts, pageinfo)

    def get_last_post_draft(self, pid):
        """ 获取文章的最新一条草稿 """
        with self._mc() as op:
            order = {"id":-1}
            where = "`isdraft`='1' and `post_parent`='{0}'".format(op.escape(pid))
            r = op.select_one(where = where, order = order)
        if r:
            return self.insert_info(r)

    def get_post_drafts(self, pid):
        """ 获取文章的所有草稿 """
        with self._mc() as op:
            order = {"id":-1}
            where = "`isdraft`='1' and `post_parent`='{0}'".format(op.escape(pid))
            r = op.select(where = where, order = order)
        if r:
            return self.insert_info(r)

    def get_short_content(self, content):
        r = self.short.findall(content)
        return r[0] if len(r) >= 1 else content

    def get_link_title(self, title, num = None, edit = False, pid = None):
        num = num if num else 0
        if num:
            title += '-' + str(num+1)
        title = title.replace(' ', '-').replace('+', '-').replace('/', '-').\
                replace('=', '-').replace('%', '-').replace('?', '-').\
                replace('&', '-').replace('#', '-')
        exists = self.check_link_title_exists(title)
        if exists:
            return self.get_link_title(title, num + 1)
        return title

    def check_link_title_exists(self, title):
        with self._mc() as op:
            where = "`link_title`='{0}'".format(title.encode('utf-8'))
            return op.select_one(where = where)
