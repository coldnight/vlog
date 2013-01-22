#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 18:38:13
#   Desc    :   评论逻辑
#
from core.logic import Logic
from core.util import md5, utf8sub, send_mail

from .options import GlobalOption
from .user import UserLogic

class CommentLogic(Logic):
    go = GlobalOption()
    ul = UserLogic()

    def init(self, pl):
        self.pl = pl

    def get_comment_by_id(self, _id):
        """ """
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(_id))
            return op.select_one(where = where)

    def add_comment(self, pid, comment_dict, request = None):
        fields = []
        values = []
        comment_dict['pid'] = pid
        for k in comment_dict:
            fields.append(k)
            values.append(comment_dict[k])

        with self._mc() as op:
            r = op.insert(fields, values)
        if not request: return r
        post_title = self.pl.get_post_by_id(pid).get("data", {}).get("title")
        if comment_dict.has_key("parent"):
            parent = comment_dict.get("parent")
            par_comm = self.get_comment_by_id(parent)
            email = par_comm.get("email")
            content = u"有人在<a href='http://{0}'>{1}</a>上的" \
                    u"<a href='http://{0}{2}'>{3}</a>文章回复" \
                    u"了你的评论,点击<a href='http://{0}{2}#comments'>链接</a>"\
                    u"查看".format(request.host, self.go.site_title, request.uri,
                                   post_title)
            send_mail([email], self.go.site_title + u" >> 收到新的回复", content)

        admin_email = self.ul.check_has_admin().get("email")
        sub = self.go.site_title + u" >> 有新的评论,请审核"
        content = u"文章<a href='http://{0}{1}'>{2}</a> 有新的评论"\
                u"".format(request.host, request.uri, post_title)
        send_mail([admin_email], sub, content)

    def allow_comment(self, cid, pid = None, item = None, request = None):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(cid))
            set_dict = {"allowed":1}
            r = op.update(set_dict, where)
            if not pid or not request:
                return r
        comm = self.get_comment_by_id(cid)
        email = comm.get("email")
        post_title = self.pl.get_post_by_id(pid).get("data", {}).get("title")
        sub = self.go.site_title + u" >> 评论通过审核"
        content = u"您对<a href='http://{0}'>{4}</a> 上的 "\
                u"<a href='http://{0}/{1}/{2}'>{3}</a> 文章的评论通过了审核,"\
                u"点击<a href='http://{0}/{1}/{2}#comments'>链接</a>"\
                u"查看".format(request.host, item, pid, post_title, self.go.site_title)
        send_mail([email], sub, content)

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
        titles = self.pl.get_titles([pid])
        r = self._insert_post_title(r, titles)
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
            post = titles.get(comment.get("pid"), {})
            comment['post_title'] = post.get("title")
            comment['link_title'] = post.get("link_title")
            comment['post_date'] = post.get("pubdate")

        return comments

    def remove_comment(self, cid):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(cid))
            op.remove(where = where)

    def get_last_comments(self,  size = 5):
        with self._mc() as op:
            where ="`allowed`='1'"
            order = {"id":-1}
            limit = self.handle_limit(size = size)
            r = op.select(where = where, order = order, limit = limit)
        pids = [c.get('pid') for c in r]
        titles = self.pl.get_titles(pids)
        comments = self._insert_post_title(r, titles)
        comments = self.insert_info(comments)
        return comments
