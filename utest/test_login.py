#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/04 14:58:48
#   Desc    :   登录单元测试
#
from unittest import TestCase
from config import PORT
from core.util import HttpHelper


class TestLogin(TestCase):

    def setUp(self):
        self.url = 'http://localhost:{0}/'.format(PORT)

    def test_login(self):
        params = {"username":"admin", "password":"123456"}
        helper = HttpHelper(self.url + 'i/login', params)
        print helper.open()
