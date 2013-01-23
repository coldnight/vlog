#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/04 09:37:22
#   Desc    :   用户逻辑
#

from core.logic import Logic
from core.util import encrypt_md5

class UserLogic(Logic):
    def add_admin(self, user_dict):
        if self.check_has_admin():
            return self.error("管理员已存在")
        if not (user_dict.has_key('username') and user_dict.get('username')):
            return self.error("请提供管理员用户名")
        if not (user_dict.has_key('email') and user_dict.get('email')):
            return self.error("请提供管理员邮箱")
        if not (user_dict.has_key("password") and user_dict.get("password")):
            return self.error("请提供管理员密码")
        if not (user_dict.has_key("password2") and user_dict.get("password2")):
            return self.error("请提供重复密码")
        if user_dict["password"] != user_dict["password2"]:
            return self.error("两次输入密码不一致")
        pwd = user_dict.pop("password2")
        user_dict['password'] = encrypt_md5(pwd)
        user_dict['name'] = user_dict.get("username")
        with self._mc() as op:
            fields, values = self.handle_insert(user_dict)
            uid = op.insert(fields, values)

        return self.success(uid)

    def check_has_admin(self):
        with self._mc() as op:
            where = "`role`='0'"
            return op.select_one(where=where)

    def admin_login(self, username, password):
        admin = self.check_has_admin()
        if not (username and password):
            return self.error(u"请使用用户名密码登录")
        if username == admin.get('username') and \
           encrypt_md5(password) == admin.get('password'):
            return self.success(admin)
        else:
            return self.error(u"登录失败")

    def login(self, username, password):
        """"""
        with self._mc() as op:
            where = "`username`='{0}' and `password`='{1}'".format(
                username, encrypt_md5(password))

            result = op.select_one(where = where)

        if result:
            return self.success(result)
        return self.error(u"登录失败")


    def update(self, uid, user_dict):
        user_dict.pop("role", None)       #  不允许更改角色
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(uid))
            return op.update(user_dict, where)

    def get_user_by_id(self, uid):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape(uid))
            return op.select_one(where = where)

    def check_has_user(self):
        with self._mc() as op:
            return op.select_one().get('id')

    def get_all_user(self):
        with self._mc() as op:
            return op.select()

    def get_user_by_name(self, name):
        with self._mc() as op:
            where = "`name`='{0}'".format(op.escape(name))
            return op.select_one(where = where)

    def add_user(self, user_dict):
        user_dict['role'] = 1
        user_dict['password'] = encrypt_md5(user_dict.get("password"))
        username = user_dict.get("username")
        if self.check_exists_username(username):
            return self.error(u"用户名已存在")
        email = user_dict.get("email")
        if self.check_exists_email(email):
            return self.error(u"邮箱已注册")
        name = user_dict.get("name")
        if self.check_exists_name(name):
            return self.error(u"显示名已存在")

        fields, values = self.handle_insert(user_dict)
        with self._mc() as op:
            return self.success(op.insert(fields, values))

    def check_exists_username(self, username):
        with self._mc() as op:
            where = "`username`='{0}'".format(op.escape(username))
            return op.select_one(where = where)

    def check_exists_name(self, name):
        with self._mc() as op:
            where = "`name`='{0}'".format(op.escape(name))
            return op.select_one(where = where)

    def check_exists_email(self, email):
        with self._mc() as op:
            where = "`email`='{0}'".format(op.escape(email))
            return op.select_one(where = where)

    def check_user(self, name, pw):
        if not name or pw:
            return False
        user = self.get_user_by_name(name)
        if user and user.get('name') == name and user.get('password') == pw:
            return True
        else:
            return False
