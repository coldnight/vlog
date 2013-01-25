#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/18 13:59:52
#   Desc    :   接口
#
from datetime import datetime
from core.web import BaseHandler
from web.logic import Logic
from web.logic.sitemap import handle_sitemap
from web.logic.rss import handle_rss


class InterfaceHandler(BaseHandler):
    username = property(lambda self: self.get_argument("username", None))
    password = property(lambda self: self.get_argument("password", None))
    pageindex = property(lambda self: self.get_argument("pageindex", 1))
    pagesize = property(lambda self:self.get_argument("pagesize", 10))
    def prepare(self):
        super(InterfaceHandler, self).prepare()
        if self.username and self.password:
            r = Logic.user.login(self.username, self.password)
            if not r.get("status"):
                self.finish({"status":False, "errmsg":u"用户名密码错误"})
            self.user_info = r.get("data")
        else:
            self.finish({"status":False, "errmsg":u"没有用户名和密码"})

    def escape(self, value):
        if isinstance(value, dict):
            return {k : self.escape(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.escape(v) for v in value]
        if isinstance(value, str):
            return value.decode("utf-8")
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value

    def write(self, chunk):
        chunk = self.escape(chunk)
        super(InterfaceHandler, self).write(chunk)

class Note(InterfaceHandler):
    _url = r'/i/note/'
    def get(self):
        r = Logic.note.get_notes(self.pageindex, self.pagesize)
        self.write(r)

    def post(self):
        content = self.get_argument("content")
        email = self.user_info.get("email")
        url = self.user_info.get("url")
        name = self.user_info.get("name")
        note_dict = {"email":email, "name":name, "url": url, "content":content}
        Logic.note.add_note(note_dict)
        self.write({"status":True})


class Post(InterfaceHandler):
    _url = r'/i/post/'
    def get(self):
        pid = self.get_argument("id", None)
        action = self.get_argument("action", "posts")
        if pid:
            if action == "remove":
                Logic.post.disable(pid)
                result = ""
            elif action == "edit":
                post = Logic.post.get_post_by_id(pid)
                draft = Logic.post.get_last_post_draft(pid)
                result = {"post":post, "draft":draft}
        else:
            if action == "posts":
                result = Logic.post.get_posts(self.pageindex, self.pagesize)
            elif action== "drafts":
                result = Logic.post.get_drafts(self.pageindex, self.pagesize)
        self.write(result)

    def post(self):
        _id = self.get_argument("id", None)
        title = self.get_argument("title")
        source = self.get_argument("source")
        content = self.get_argument("content")
        tags = self.get_argument("tags")
        category = self.get_argument("category")
        isdraft = self.get_argument("isdraft", 0)

        post_dict = {"title":title, "source":source, "content":content,
                     "tags":tags, "category":category,
                     "isdraft":int(isdraft)}

        if _id:
            Logic.post.edit(_id, post_dict)
            pid = _id
        else:
            post_dict.update(author = self.user_info.get("id"))
            pid = Logic.post.post(post_dict).get("data")

        post = Logic.post.get_post_by_id(pid).get("data")
        handle_sitemap(Logic, self.request)
        handle_rss(Logic, self.request)
        self.write(post)

class CategoryHandler(InterfaceHandler):
    _url = r"/i/category/"
    def get(self):
        category = Logic.category.get_categories()
        self.write(category)
