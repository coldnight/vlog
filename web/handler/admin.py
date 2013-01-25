#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/07 13:10:55
#   Desc    :   后台管理
#
import os
import functools

from core.web import BaseHandler
from core.util import encrypt_md5

from web.logic import Logic
from web.logic.sitemap import handle_sitemap
from web.logic.rss import handle_rss
from web.logic.fwp import FromWPLogic


class AdminHandler(BaseHandler):
    template_path = os.path.join(BaseHandler.template_path, 'admin')
    option = Logic.option

    def prepare(self):
        super(AdminHandler, self).prepare()
        if not self.username and not self.uid and self.request.path not in ['/admin/login']:
            self.redirect('/admin/login')
        self.handle_sitemap = functools.partial(handle_sitemap, Logic,
                                                self.request)
        self.handle_rss = functools.partial(handle_rss, Logic,
                                                self.request)

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
        user_info = Logic.user.admin_login(username, password)
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
        categories = Logic.category.get_categories()
        tags = Logic.tag.get_tags()
        self.render('admin_post.jinja', categories = categories.get('data'),
                    tags = tags.get('data'), isedit=False, ispage=False)

    def post(self):
        title = self.get_argument('title')
        link_title = self.get_argument("link_title")
        source = self.get_argument("source")
        content = self.get_argument('content')
        tags = self.get_argument('tags')
        category = self.get_argument('category')
        post_dict = {"title":title, "content":content, "source":source,
                     "category":category, "tags":tags, "author":self.uid,
                     'link_title': link_title}
        r = Logic.post.post(post_dict)
        self.handle_sitemap()
        self.handle_rss()
        self.write(r)

class AddPage(AdminHandler):
    def get(self):
        self.render("admin_post.jinja", isedit = False, ispage = True)

    def post(self):
        title = self.get_argument('title')
        link_title = self.get_argument("link_title")
        source = self.get_argument("source")
        content = self.get_argument('content')
        page_dict = {"title":title, "content":content, "source":source,
                     "author":self.uid, 'link_title':link_title}
        self.handle_sitemap()
        self.handle_rss()
        self.write(Logic.page.add_page(page_dict))

class EditPage(AdminHandler):
    _url = r"/admin/editpage/?(\d*)"
    def get(self, pid):
        page = Logic.page.get_page(pid)
        if not page:
            self.redirect('/admin/addpage')
        self.render("admin_post.jinja", post = page.get("data"),
                    isedit = True, ispage = True)

    def post(self, pid):
        title = self.get_argument('title')
        source = self.get_argument("source")
        content = self.get_argument('content')
        pid = self.get_argument("id")
        page_dict = {"title":title, "content":content, "source":source,
                     "author":self.uid}
        r = Logic.page.edit_page(pid, page_dict)
        self.handle_sitemap()
        self.handle_rss()
        self.write(r)

class EditPost(AdminHandler):
    _url = r"/admin/editpost/?(\d*)"
    def get(self, pid):
        post = Logic.post.get_post_by_id(pid)
        categories = Logic.category.get_categories()
        if not post:
            self.redirect('/admin/addpost')
        self.render("admin_post.jinja", post = post.get("data"),
                    categories = categories.get("data"), isedit = True,
                    ispage = False)

    def post(self, pid):
        title = self.get_argument('title')
        source = self.get_argument("source")
        content = self.get_argument('content')
        tags = self.get_argument('tags')
        category = self.get_argument('category')
        pid = self.get_argument("id")
        post_dict = {"title":title, "content":content, "source":source,
                     "category":category, "tags":tags}
        r = Logic.post.edit(pid, post_dict)
        self.handle_sitemap()
        self.handle_rss()
        self.write(r)

class LinksHandler(AdminHandler):
    def get(self):
        _id = self.get_argument("id", None)
        link = None
        title = u"链接表"
        if _id:
            link = Logic.link.get_link_by_id(_id)
            title = u"编辑链接 | {0}".format(link.get("text"))
        links = Logic.link.get_all_links()

        self.render("admin_link.jinja", links = links, link = link, title=title)

    def post(self):
        text = self.get_argument("text")
        url = self.get_argument("url")
        order = self.get_argument("order")
        act = self.get_argument("act")
        if act == "add":
            lid = Logic.link.add_new_link(text, url, order)
        if act == "edit":
            lid = self.get_argument("id")
            Logic.link.update_link_edit(lid,
                                        {"text":text, "url":url, "order":order})

        self.redirect("/admin/links?id={0}".format(lid))

class UserHandler(AdminHandler):
    def get(self):
        _id = self.get_argument("uid", None)
        user = None
        title = u"用户管理"
        if _id:
            user = Logic.user.get_user_by_id(_id)
        users = Logic.user.get_all_user()

        self.render("admin_user.jinja", user = user, users = users, title=title)

    def post(self):
        username = self.get_argument("username", None)
        email = self.get_argument("email", None)
        name = self.get_argument("name", None)
        url = self.get_argument("url", None)
        pwd = self.get_argument("pwd", None)
        pwd2 = self.get_argument('pwd2', None)
        _id = self.get_argument("uid", None)
        action = self.get_argument("act")
        if action == "add":
            if not (username and email and pwd and pwd2):
                return self.write({"status":False, 'errmsg':u"必填"})
            if pwd != pwd2:
                return self.write({"status":False, "errmsg":u"两次密码不一致"})
            user_dict = {"username":username, "password":pwd,
                         "email":email, "name":name}
            url and user_dict.update({"url":url})
            r = Logic.user.add_user(user_dict)
            if r.get("status"):
                self.redirect("/admin/user?uid={0}".format(r.get("data")))
            self.write(r)
        #TODO
        if action == "edit":pass

class AddNoteHandler(AdminHandler):
    def post(self):
        content = self.get_argument("content")
        email = self.get_argument("email", None)
        url = self.get_argument("url", None)
        name = self.get_argument("name", None)
        if not name or not email:
            user = Logic.user.check_has_admin()
            if not name:
                name = user.get("name")
            if not email:
                email = user.get("email")

        if not url:
            url = "http://{0}".format(self.request.host)

        note_dict = {"content":content, "email":email, "url":url, "name":name}
        Logic.note.add_note(note_dict)
        self.write({"status":True})



class RemoveHandler(AdminHandler):
    _url = r"/admin/del/(\w+)/(\d+)/?"
    def get(self, item, _id):
        if item == 'post' or item == 'page':
            Logic.post.disable(_id)
            redirect = "/admin/add"+item

        if item == "comment":
            Logic.comment.remove_comment(_id)
            redirect = self.request.headers.get("Referer")

        if item == "link":
            Logic.link.del_link_by_id(_id)
            redirect = "/admin/links"

        if item == "note":
            Logic.note.remove_comment(_id)
            redirect = "/notes/"

        self.handle_sitemap()
        self.handle_rss()
        self.cache.flush()
        self.redirect(redirect)

class SiteHandler(AdminHandler):
    def get(self):
        self.render("admin_site.jinja", option = self.option)

    def post(self):
        site_title = self.get_argument("site_title")
        sub_title = self.get_argument("sub_title")
        desc = self.get_argument("desc")
        keywords = self.get_argument("keywords")
        pagesize = self.get_argument("pagesize")
        self.option = Logic.option
        self.option.site_title = site_title
        self.option.sub_title = sub_title
        self.option.description = desc
        self.option.keywords = keywords
        self.option.pagesize = pagesize
        self.handle_sitemap()
        self.write({"status":True})

class Secure(AdminHandler):
    def get(self):
        user = Logic.user.check_has_admin()
        self.render("admin_secure.jinja", user = user)

    def post(self):
        name = self.get_argument("name")
        oldp = self.get_argument("oldpwd", None)
        pwd = self.get_argument("pwd", None)
        pwd2 = self.get_argument("pwd2", None)
        user_dict = {"name":name}
        if oldp:
            user = Logic.user.get_user_by_id(self.uid)
            if encrypt_md5(oldp) == user.get("password"):
                if pwd and pwd2:
                    if pwd == pwd2:
                        user_dict.update(password = encrypt_md5(pwd))
                        r = {"status":True}
                    else:
                        r = {"status": False, "errmsg":"两次密码不一致"}
                else:
                    r = {"status":False, "errmsg":"请输入新密码"}
            else:
                r = {"status":False, "errmsg":"旧密码错误"}
        else:
            r = {"status":True}

        if r.get("status"):
            Logic.user.update(self.uid, user_dict)
        self.write(r)

class CommentHandler(AdminHandler):
    _url = r"/admin/allow/comment/(\d+)/(\d+)/(\w+)"
    def get(self, pid, cid, item):
        Logic.comment.allow_comment(cid, pid, item, self.request)
        self.cache.flush()
        self.redirect("/{0}/{1}#comments".format(item, pid))


class AddCategory(AdminHandler):
    def post(self):
        name = self.get_argument('name')
        r = Logic.category.add_category(name)
        self.handle_sitemap()
        self.write(r)

class UploadHandler(AdminHandler):
    def post(self):
        if self.request.files:
            request = self.request.files["uploadfile"][0]
            filename = request["filename"]
            body = request["body"]
            url_path = Logic.upload.upload(body, filename)
            result = {"status":True, "path":url_path}
        else:
            result = {"status":False}

        self.write(result)

class ImportHandler(AdminHandler):
    def get(self):
        self.render("admin_import.jinja")

    def post(self):
        if self.request.files:
            request = self.request.files["wpexport"][0]
            filename = request["filename"]
            body = request["body"]
            path = Logic.upload.upload(body, filename, True)
            fromwp = FromWPLogic(Logic, path)
            fromwp.start()
            result = {"status":True}
        else:
            result = {"status":False}

        self.write(result)

class CleanHandler(AdminHandler):
    def get(self):
        self.cache.flush()
        self.redirect("/admin/")


class AjaxHandler(AdminHandler):
    def post(self):
        result = {"status":True}
        action = self.get_argument("action")
        if action == "get_link_title":
            title = self.get_argument("title")
            r = Logic.post.get_link_title(title)
            result["data"] = r

        self.write(result)
