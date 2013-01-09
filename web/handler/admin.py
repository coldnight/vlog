#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/07 13:10:55
#   Desc    :   后台管理
#
import os

from core.web import BaseHandler
from core.util import md5

from web.logic.category import CategoryLogic
from web.logic.tag import TagLogic
from web.logic.post import PostLogic
from web.logic.options import GlobalOption
from web.logic.user import UserLogic
from web.logic.page import PageLogic
from web.logic.comment import CommentLogic


class AdminHandler(BaseHandler):
    template_path = os.path.join(BaseHandler.template_path, 'admin')
    option = GlobalOption()

    def prepare(self):
        super(AdminHandler, self).prepare()
        if not self.username and not self.uid and self.request.path not in ['/admin/login']:
            self.redirect('/admin/login')

    def render(self, template_path, **kwargs):
        kwargs['SITE_TITLE'] = self.option.site_title
        kwargs['SITE_SUB_TITLE'] = self.option.sub_title
        BaseHandler.render(self, template_path, **kwargs)

class Login(AdminHandler):
    def get(self):
        self.render("admin_login.jinja", title=u"登录")

    def post(self):
        username = self.get_argument("name")
        password = self.get_argument("password")
        user_info = UserLogic().login(username, password)
        if user_info.get("status"):
            user = user_info.get("data")
            self.login(user.get("username"), user.get("id"))
            self.write({"status":True})
        else:
            self.write(user_info)

class Logout(AdminHandler):
    def get(self):
        self.logout('/admin/login')

class Index(AdminHandler):
    def get(self):
        self.render("admin_index.jinja")

class AddPost(AdminHandler):
    def get(self):
        categories = CategoryLogic().get_categories()
        tags = TagLogic().get_tags()
        self.render('admin_addpost.jinja', categories = categories.get('data'),
                    tags = tags.get('data'))

    def post(self):
        title = self.get_argument('title')
        source = self.get_argument("source")
        content = self.get_argument('content')
        tags = self.get_argument('tags')
        category = self.get_argument('category')
        post_dict = {"title":title, "content":content, "source":source,
                     "category":category, "tags":tags, "author":self.uid}
        r = PostLogic().post(post_dict)
        self.write(r)

class AddPage(AdminHandler):
    def get(self):
        self.render("admin_addpage.jinja")

    def post(self):
        title = self.get_argument('title')
        source = self.get_argument("source")
        content = self.get_argument('content')
        page_dict = {"title":title, "content":content, "source":source,
                     "author":self.uid}
        self.write(PageLogic().add_page(page_dict))

class EditPage(AdminHandler):
    _url = r"/admin/editpage/?(\d*)"
    def get(self, pid):
        page = PageLogic().get_page(pid)
        if not page:
            self.redirect('/admin/addpage')
        self.render("admin_editpage.jinja", page = page.get("data"))

    def post(self, pid):
        title = self.get_argument('title')
        source = self.get_argument("source")
        content = self.get_argument('content')
        pid = self.get_argument("id")
        page_dict = {"title":title, "content":content, "source":source,
                     "author":self.uid}
        r = PageLogic().edit_page(pid, page_dict)
        print r
        self.write(r)

class EditPost(AdminHandler):
    _url = r"/admin/editpost/?(\d*)"
    def get(self, pid):
        post = PostLogic().get_post_by_id(pid)
        categories = CategoryLogic().get_categories()
        if not post:
            self.redirect('/admin/addpost')
        self.render("admin_editpost.jinja", post = post.get("data"),
                    categories = categories.get("data"))

    def post(self, pid):
        title = self.get_argument('title')
        source = self.get_argument("source")
        content = self.get_argument('content')
        tags = self.get_argument('tags')
        category = self.get_argument('category')
        pid = self.get_argument("id")
        post_dict = {"title":title, "content":content, "source":source,
                     "category":category, "tags":tags}
        r = PostLogic().edit(pid, post_dict)
        self.write(r)

class RemoveHandler(AdminHandler):
    _url = r"/admin/del/(\w+)/(\d+)"
    def get(self, item, _id):
        if item == 'post' or item == 'page':
            PostLogic().remove(_id)

        self.redirect("/admin/add"+item)

class SiteHandler(AdminHandler):
    def get(self):
        self.render("admin_site.jinja", option = self.option)

    def post(self):
        site_title = self.get_argument("site_title")
        sub_title = self.get_argument("sub_title")
        desc = self.get_argument("desc")
        keywords = self.get_argument("keywords")
        pagesize = self.get_argument("pagesize")
        self.option = GlobalOption()
        self.option.site_title = site_title
        self.option.sub_title = sub_title
        self.option.description = desc
        self.option.keywords = keywords
        self.option.pagesize = pagesize
        self.write({"status":True})

class Secure(AdminHandler):
    def get(self):
        user = UserLogic().check_has_admin()
        self.render("admin_secure.jinja", user = user)

    def post(self):
        name = self.get_argument("name")
        oldp = self.get_argument("oldpwd", None)
        pwd = self.get_argument("pwd", None)
        pwd2 = self.get_argument("pwd2", None)
        user_dict = {"name":name}
        if oldp:
            user = UserLogic().get_user_by_id(self.uid)
            if md5(oldp) == user.get("password"):
                if pwd and pwd2:
                    if pwd == pwd2:
                        user_dict.update(password = md5(pwd))
                        r = {"status":True}
                    else:
                        r = {"status": False, "errmsg":"两次密码不一致"}
                else:
                    r = {"status":False, "errmsg":"请输入新密码"}
            else:
                r = {"status":False, "errmsg":"旧密码错误"}

        if r.get("status"):
            UserLogic().update(self.uid, user_dict)
        self.write(r)

class CommentHandler(AdminHandler):
    _url = r"/admin/allow/comment/(\d+)/(\d+)"
    def get(self, pid, cid):
        CommentLogic().allow_comment(cid)
        self.redirect("/post/{0}#comments".format(pid))


class AddCategory(AdminHandler):
    def post(self):
        name = self.get_argument('name')
        r = CategoryLogic().add_category(name)
        self.write(r)
