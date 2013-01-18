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


class InterfaceHandler(BaseHandler):
    username = property(lambda self: self.get_argument("username", None))
    password = property(lambda self: self.get_argument("password", None))
    pageindex = property(lambda self: self.get_argument("index", 1))
    pagesize = property(lambda self:self.get_argument("pagesize", 10))
    def prepare(self):
        super(InterfaceHandler, self).prepare()
        if self.username and self.password:
            r = Logic.user.login(self.username, self.password)
            if not r.get("status"):
                self.finish({"status":False})
            self.user_info = r.get("data")
        else:
            self.finish({"status":False})

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
