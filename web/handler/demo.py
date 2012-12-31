#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wh
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/18 11:24:24
#   Desc    :   示例
#

from core.web import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html', title = 'Pythoner Club')

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', title = 'Pythoner Club -- login')

class RenderHandler(BaseHandler):
    def get(self):
        self.render('index.html', title = '')

class QuestionHandler(BaseHandler):
    def get(self):
        self.write('deving')

class AnswerHandler(BaseHandler):
    def get(self):
        self.write('deving')

class SessionHandler(BaseHandler):
    def get(self):
        i = self.session.i
        i = 0 if not i else i
        self.session.i = i + 1
        self.write(str(i))


