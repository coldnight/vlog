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

from config import STATIC_PATH as STATIC_ROOT, UPLOAD_PATH, THEME, DEBUG
from core.web import BaseHandler
from core.util import md5

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
                self.admin_login(username, admin_id.get("data"))
            handle_sitemap(Logic, self.request)
            handle_rss(Logic, self.request)
            self.write(admin_id)


class WebHandler(BaseHandler):
    """ web前台handler基类 """
    #TODO 可配置的主题
    template_path = os.path.join(BaseHandler.template_path, THEME)
    option = Logic.option

    def initialize(self):
        self.pagesize = self.cache.get("pagesize")
        if not self.pagesize:
            pagesize = self.option.pagesize
            self.pagesize = pagesize if pagesize else 10
            self.cache.set("pagesize", self.pagesize)

    def get_error_html(self, status_code = 500, **kwargs):
        kwargs['status_code'] = status_code
        errpath = os.path.join(self.template_path,
                               "{0}.jinja".format(status_code))
        if not DEBUG and kwargs.has_key("exception"):
            kwargs["exception"] = None
        if os.path.exists(errpath):
            self.render("{0}.jinja".format(status_code), **kwargs)
        else:
            self.render("error.jinja", **kwargs)

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
        kwargs['comments'] = Logic.comment.get_last_comments()
        kwargs['tags'] = tags.get('data')
        kwargs['new'] = pl.get_new()
        kwargs['months'] = pl.get_months()
        kwargs['categories'] = categories.get('data')
        kwargs['SITE_TITLE'] = self.option.site_title
        kwargs['SITE_SUB_TITLE'] = self.option.sub_title
        kwargs["links"] = Logic.link.get_all_links()
        if not kwargs.has_key("description"):
            kwargs['description'] = self.option.description
        if not kwargs.has_key("keywords"):
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
        if not posts.get("data"):
            self.send_error(404, info = u"页面不存在")
        self.render('index.jinja', posts=posts.get('data'),
                    pageinfo=posts.get('pageinfo'),
                    base_path = "/")

class PostHandler(WebHandler):
    _url = r"/post/(\d+)/?(\d*)"
    def get(self, pid, index):
        index = index if index else 1
        post = Logic.post.get_post_by_id(pid).get("data")
        if not post:
            self.send_error(404, info = u"文章不存在")
        comments = Logic.comment.get_post_comments(pid, index, self.pagesize)
        user = {}
        if self.uid and self.username:
            user = Logic.user.get_user_by_id(self.uid)
        self.render("page.jinja", post = post,
                    post_comments = comments.get("data"), user = user,
                    title=post.get("title"), pageinfo = comments.get("pageinfo"),
                    description = post.get("short_content"),
                    keywords = post.get("keywords"))

    def post(self, pid, index):
        name = self.get_argument("name")
        email = self.get_argument("email")
        url = self.get_argument("url")
        content = self.get_argument("content")
        parent = self.get_argument("parent", None)
        comment_dict = {}
        comment_dict['name'] = name
        comment_dict['email'] = email
        comment_dict['url'] = url
        comment_dict['content'] = content
        comment_dict['ip'] = self.request.remote_ip
        if parent: comment_dict['parent'] = parent
        cid = Logic.comment.add_comment(pid, comment_dict, self.request)
        if self.uid and self.username:
            Logic.comment.allow_comment(cid)
        self.write({"status":True, "msg":u"评论提交成功,等待管理员审核"})


class TitlePostHandler(WebHandler):
    #XXX (.+?) 捕捉中文如不以/结尾则会传入一个%值 奇怪
    _url = r"/\d{4}/\d{1,2}/\d{1,2}/(.+?)/(?:comment-page)*-*(\d*)"
    def get(self, link_title, index):
        index = index if index else 1
        post = Logic.post.get_post_by_link(link_title).get("data")
        pid = post.get("id")
        if not post:
            self.send_error(404, info = u"文章不存在")
        comments = Logic.comment.get_post_comments(pid, index, self.pagesize)
        user = {}
        if self.uid and self.username:
            user = Logic.user.get_user_by_id(self.uid)
        self.render("page.jinja", post = post,
                    post_comments = comments.get("data"), user = user,
                    title=post.get("title"), pageinfo = comments.get("pageinfo"),
                    description = post.get("short_content"),
                    keywords = post.get("keywords"))


class CategoryHandler(WebHandler):
    _url = r"/category/(.+?)/(\d*)"
    def get(self, cate, index):
        index = index if index else 1
        title = cate
        cid = Logic.category.check_exists(cate).get("id")
        if not cid:
            self.send_error(404, info=u"没有 {0} 这个类别".format(cate))
        posts = Logic.post.get_post_by_category(cid, int(index), self.pagesize)
        self.render("index.jinja", posts = posts.get("data"),
                    pageinfo = posts.get("pageinfo"), title = title,
                    base_path = u"/category/{0}/".format(cate))

class TagHandler(WebHandler):
    _url = r"/tag/(.+?)/(\d*)"
    def get(self, tag, index):
        index = index if index else 1
        tid = Logic.tag.check_exists(tag)
        if not tid:
            self.send_error(404, info=u"没有 {0} 这个标签".format(tag))
        posts = Logic.post.get_post_by_tag(tid, int(index), self.pagesize)
        self.render("index.jinja", posts = posts.get("data"),
                    pageinfo = posts.get("pageinfo"), title  = tag,
                    base_path = u"/tag/{0}/".format(tag))

class PageHandler(WebHandler):
    #XXX 如不传(.+?)后面的/会传进一个很奇特的%字符导致解码失败
    _url = r"/page/(.+?)/(?:comment-page-)*(\d*)"
    def get(self, link_title, index):
        index = index if index.strip() else 1
        if self.uid and self.username:
            user = Logic.user.get_user_by_id(self.uid)
        else:
            user = None
        page = Logic.page.get_page_by_link(link_title).get("data")
        if not page:
            self.send_error(404, info = u"页面不存在")
        comments = Logic.comment.get_post_comments(page.get("id"), index,
                                                    self.pagesize)
        post_comments = comments.get("data")
        pageinfo = comments.get("pageinfo")
        self.render("page.jinja", post = page, title=page.get("title"),
                    ispage = True, user = user, pageinfo = pageinfo,
                    post_comments = post_comments)

class DateHandler(WebHandler):
    _url = r"/date/(\d+)/(\d+)/(\d*)"
    def get(self, year, month, index):
        index = index if index else 1
        data = Logic.post.get_by_month(year, month, index, self.pagesize)
        pageinfo = data.get("pageinfo")
        posts = data.get("data")
        self.render("index.jinja", posts = posts, pageinfo = pageinfo,
                    title = u"{0}年 {1} 月".format(year, month),
                    base_path = "/date/{0}/{1}/".format(year, month))

class NotesHandler(WebHandler):
    _url = r"/notes/(?:p)*/?(\d*)/?"
    def get(self, index):
        index = index if index else 1
        data = Logic.note.get_notes(index)
        notes = data.get("data")
        pageinfo = data.get("pageinfo")
        gravatar = None
        if self.uid and self.username:
            admin = Logic.user.check_has_admin().get("email")
            gravatar = md5(admin)
        self.render("notes.jinja", notes = notes, title = u"便签",
                    gravatar = gravatar, pageinfo = pageinfo,
                    basepath = r'/notes/p/')

class VlAjaxHandler(WebHandler):
    _url = r"/vl-ajax"
    def post(self):
        action = self.get_argument("action")
        if action == "add_post_view":
            pid = self.get_argument("pid")
            Logic.post.add_post_view(pid)

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

class ErrorHandler(WebHandler):
    def get(self, path):
        self.send_error(404, info=u"您当前访问的页面不存在(可能由于博客迁移,您访问的还是旧链接)")
