#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 17:50:46
#   Desc    :   接口首页
#
from core.web import BaseHandler

from web.logic.user import UserLogic

class LoginHandler(BaseHandler):
    """ 登录接口 """

    def get(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        info = UserLogic().check(username, password)
        if info.get("status"):
            self.session.key = info.get("key")
        self.write(info)

class IBaseHandler(BaseHandler):
    pagesize = property(lambda self:self.get_argument('pagesize'))
    pageindex = property(lambda self:self.get_argument('pageindex'))
    uid = property(lambda self:self.get_argument('uid'))

    def prepare(self):
        super(IBaseHandler, self).prepare()
        if self.request.path not in ['/i/login']:
            key = self.get_argument('key')
            if not key:
                self.finish({"status":False, "errmsg":"Access with Key"})
            dkey = UserLogic().get_key(self.uid)
            if self.session.key != key or key != dkey:
                self.finish({"status":False, "errmsg":"Bad Token"})
