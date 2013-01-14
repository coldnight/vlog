#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/14 17:19:47
#   Desc    :
#
import os

from MySQLdb import OperationalError
from tornado.web import StaticFileHandler

from config import STATIC_PATH as STATIC_ROOT, UPLOAD_PATH
from core.web import BaseHandler

from web.logic import Logic
from web.logic.install import install
from web.logic.sitemap import handle_sitemap
from web.logic.rss import handle_rss

class Install(BaseHandler):
    """ 安装 """
    _url = r"/install/?(\d*)"
    def prepare(self):
        super(BaseHandler, self).prepare()
        try:
            admin = Logic.user.check_has_admin()
            if admin:
                self.redirect('/')
        except:
            pass

    def get(self, step=1):
        step = int(step) if step else  1
        title = u"vLogs 安装"
        self.render("install.jinja", step=step, title = title)

    def post(self, s):
        step = self.get_argument("step")
        step = int(step)
        if step == 1:
            host = self.get_argument("mysql_host")
            port = self.get_argument("mysql_port")
            user = self.get_argument("mysql_user")
            name = self.get_argument("mysql_name")
            pwd = self.get_argument("mysql_pwd", '')
            prev = self.get_argument("mysql_prev")
            r = install(host, port, user, pwd, name, prev)
            self.write(r)

        if step == 2:
            site_title = self.get_argument("site_title")
            sub_title = self.get_argument("sub_title")
            desc = self.get_argument("desc")
            keywords = self.get_argument("keywords")
            option = Logic.option
            option.site_title = site_title
            option.sub_title = sub_title
            option.description = desc
            option.keywords = keywords
            self.write({"status":True})

        if step == 3:
            username = self.get_argument("username")
            password = self.get_argument("password")
            password2 = self.get_argument("password2")
            email = self.get_argument("email")
            user_dict = {"username":username, "email":email,
                         "password":password, "password2":password2}
            admin_id = Logic.user.add_admin(user_dict)
            if admin_id.get("status"):
                cate = Logic.category.add_category(u"未分类")
                cid = cate.get("data").get("id")
                content = u"欢迎选择vLogs创作,你可以到后台删除这篇文章,"\
                            u"写下一篇新文章来开始你的写作之旅"
                init_post = {"title":u"欢迎使用vLogs",
                            "content": content,
                             "source": content,
                            "tags": u"欢迎",
                            "category":str(cid),
                            "author":admin_id.get("data"),
                            }
                Logic.post.post(init_post)
                self.login(username, admin_id.get("data"))
            handle_sitemap(Logic, self.request)
            handle_rss(Logic, self.request)
            self.write(admin_id)


class WebHandler(BaseHandler):
    """ web前台handler基类 """
    #TODO 可配置的主题
    template_path = os.path.join(BaseHandler.template_path, 'octopress')

    def initialize(self):
        self.pagesize = self.cache.get("pagesize")
        if not self.pagesize:
            self.option = Logic.option
            pagesize = self.option.pagesize
            self.pagesize = pagesize if pagesize else 10
            self.cache.set("pagesize", self.pagesize)

    def prepare(self):
        super(WebHandler, self).prepare()
        try:
            admin = Logic.user.check_has_admin()
            if not admin:
                self.redirect('/install/')
        except OperationalError:
            self.redirect('/install/')



    def render(self, template_path, **kwargs):
        tags = Logic.tag.get_tags()
        categories = Logic.category.get_categories()
        pl = Logic.post
        kwargs['comments'] = Logic.comment.get_last_comments(pl)
        kwargs['tags'] = tags.get('data')
        kwargs['new'] = pl.get_new()
        kwargs['months'] = pl.get_months()
        kwargs['categories'] = categories.get('data')
        kwargs['SITE_TITLE'] = self.option.site_title
        kwargs['SITE_SUB_TITLE'] = self.option.sub_title
        kwargs['description'] = self.option.description
        kwargs['keywords'] = self.option.keywords
        kwargs['page'] = Logic.page.get_all_pages()
        kwargs['uid'] = self.uid
        kwargs['username'] = self.username
        self.logger.debug("%r", kwargs)
        BaseHandler.render(self, template_path, **kwargs)

class IndexHandler(WebHandler):
    _url = r"/(\d*)"
    def get(self, index = 1):
        index = index if index else 1
        posts = Logic.post.get_posts(int(index), self.pagesize)
        self.render('index.jinja', posts=posts.get('data'),
                    pageinfo=posts.get('pageinfo'))

class PostHandler(WebHandler):
    _url = r"/post/(\d+)/?(\d*)"
    def get(self, pid, index):
        index = index if index else 1
        post = Logic.post.get_post_by_id(pid).get("data")
        comments = Logic.comment.get_post_comments(pid, index, self.pagesize)
        user = {}
        if self.uid and self.username:
            user = Logic.user.get_user_by_id(self.uid)
        self.render("page.jinja", post = post, post_comments = comments.get("data"), user = user,
                    title=post.get("title"), pageinfo = comments.get("pageinfo"))

    def post(self, pid, index):
        name = self.get_argument("name")
        email = self.get_argument("email")
        url = self.get_argument("url")
        content = self.get_argument("content")
        comment_dict = {}
        comment_dict['name'] = name
        comment_dict['email'] = email
        comment_dict['url'] = url
        comment_dict['content'] = content
        comment_dict['ip'] = self.request.remote_ip
        cid = Logic.comment.add_comment(pid, comment_dict)
        if self.uid and self.username:
            Logic.comment.allow_comment(cid)
        self.redirect("/post/{0}#comments".format(pid))

class CategoryHandler(WebHandler):
    _url = r"/category/(\d+)/(\d*)"
    def get(self, cid, index):
        index = index if index else 1
        cate = Logic.category.get_category(cid).get("name")
        title = cate
        posts = Logic.post.get_post_by_category(cid, int(index), self.pagesize)
        self.render("index.jinja", posts = posts.get("data"),
                    pageinfo = posts.get("pageinfo"), title = title)

class TagHandler(WebHandler):
    _url = r"/tag/(\d+)/(\d*)"
    def get(self, tid, index):
        index = index if index else 1
        tag = Logic.tag.get_tag(tid).get("name")
        posts = Logic.post.get_post_by_tag(tid, int(index), self.pagesize)
        self.render("index.jinja", posts = posts.get("data"),
                    pageinfo = posts.get("pageinfo"), title  = tag)

class PageHandler(WebHandler):
    _url = r"/page/(\d+)/?(\d*)"
    def get(self, pid, index):
        index = index if index.strip() else 1
        if self.uid and self.username:
            user = Logic.user.get_user_by_id(self.uid)
        else:
            user = None
        page = Logic.page.get_page(pid).get("data")
        comments = Logic.comment.get_post_comments(page.get("id"), index,
                                                    self.pagesize)
        post_comments = comments.get("data")
        pageinfo = comments.get("pageinfo")
        self.render("page.jinja", post = page, title=page.get("title"),
                    ispage = True, user = user, pageinfo = pageinfo,
                    post_comments = post_comments)

class DateHandler(WebHandler):
    _url = r"/date/(\d+)/(\d+)/?(\d*)"
    def get(self, year, month, index):
        index = index if index else 1
        data = Logic.post.get_by_month(year, month, index, self.pagesize)
        pageinfo = data.get("pageinfo")
        posts = data.get("data")
        self.render("index.jinja", posts = posts, pageinfo = pageinfo,
                    title = u"{0}年 {1} 月".format(year, month))

class FeedHandler(StaticFileHandler):
    def initialize(self):
        StaticFileHandler.initialize(self, STATIC_ROOT)

    def get(self):
        StaticFileHandler.get(self, 'rss.xml')

class SitemapHandler(StaticFileHandler):
    _url = r'/sitemap.xml'
    def initialize(self):
        StaticFileHandler.initialize(self, STATIC_ROOT)

    def get(self):
        StaticFileHandler.get(self, 'sitemap.xml')

class UploadHandler(StaticFileHandler):
    _url = r"/upload/(.+)"
    def initialize(self):
        StaticFileHandler.initialize(self, UPLOAD_PATH)

    def get(self, filename):
        StaticFileHandler.get(self, filename)
