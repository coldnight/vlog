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

from core.web import BaseHandler
from web.logic.code import insert_code, get_code
from web.logic.code import get_option_tag
from web.logic.install import install
from web.logic.post import PostLogic
from web.logic.tag import TagLogic
from web.logic.category import CategoryLogic
from web.logic.user import UserLogic
from web.logic.options import GlobalOption
from web.logic.page import PageLogic
from web.logic.comment import CommentLogic

class Install(BaseHandler):
    """ 安装 """
    _url = r"/install/?(\d*)"
    def prepare(self):
        super(BaseHandler, self).prepare()
        try:
            admin = UserLogic().check_has_admin()
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
            option = GlobalOption()
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
            admin_id = UserLogic().add_admin(user_dict)
            if admin_id.get("status"):
                cate = CategoryLogic().add_category(u"未分类")
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
                PostLogic().post(init_post)
                self.login(username, admin_id.get("data"))
            self.write(admin_id)


class WebHandler(BaseHandler):
    """ web前台handler基类 """
    #TODO 可配置的主题
    template_path = os.path.join(BaseHandler.template_path, 'octopress')

    def prepare(self):
        super(BaseHandler, self).prepare()
        try:
            admin = UserLogic().check_has_admin()
            if not admin:
                self.redirect('/install/')
        except OperationalError:
            self.redirect('/install/')
        self.option = GlobalOption()
        pagesize = self.option.pagesize
        self.pagesize = pagesize if pagesize else 10



    def render(self, template_path, **kwargs):
        tags = TagLogic().get_tags()
        categories = CategoryLogic().get_categories()
        kwargs['comments'] = []
        kwargs['tags'] = tags.get('data')
        kwargs['categories'] = categories.get('data')
        kwargs['SITE_TITLE'] = self.option.site_title
        kwargs['SITE_SUB_TITLE'] = self.option.sub_title
        kwargs['description'] = self.option.description
        kwargs['keywords'] = self.option.keywords
        kwargs['page'] = PageLogic().get_all_pages()
        kwargs['uid'] = self.uid
        kwargs['username'] = self.username
        print kwargs

        BaseHandler.render(self, template_path, **kwargs)

class IndexHandler(WebHandler):
    _url = r"/(\d*)"
    def get(self, index = 1):
        index = index if index else 1
        posts = PostLogic().get_posts(int(index), self.pagesize)
        self.render('index.jinja', posts=posts.get('data'),
                    pageinfo=posts.get('pageinfo'))

class PostHandler(WebHandler):
    _url = r"/post/(\d+)/?(\d*)"
    def get(self, pid, index):
        index = index if index else 1
        post = PostLogic().get_post_by_id(pid).get("data")
        comments = CommentLogic().get_post_comments(pid, index, self.pagesize)
        user = {}
        if self.uid and self.username:
            user = UserLogic().get_user_by_id(self.uid)
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
        cid = CommentLogic().add_comment(pid, comment_dict)
        if self.uid and self.username:
            CommentLogic().allow_comment(cid)
        self.redirect("/post/{0}#comments".format(pid))

class CategoryHandler(WebHandler):
    _url = r"/category/(\d+)/(\d*)"
    def get(self, cid, index):
        index = index if index else 1
        cate = CategoryLogic().get_category(cid).get("name")
        title = cate
        posts = PostLogic().get_post_by_category(cid, int(index), self.pagesize)
        self.render("index.jinja", posts = posts.get("data"),
                    pageinfo = posts.get("pageinfo"), title = title)

class TagHandler(WebHandler):
    _url = r"/tag/(\d+)/(\d*)"
    def get(self, tid, index):
        index = index if index else 1
        tag = TagLogic().get_tag(tid).get("name")
        posts = PostLogic().get_post_by_tag(tid, int(index), self.pagesize)
        self.render("index.jinja", posts = posts.get("data"),
                    pageinfo = posts.get("pageinfo"), title  = tag)

class PageHandler(WebHandler):
    _url = r"/page/(\d+)"
    def get(self, pid):
        if self.uid and self.username:
            user = UserLogic().get_user_by_id(self.uid)
        page = PageLogic().get_page(pid).get("data")
        self.render("page.jinja", post = page, title=page.get("title"),
                    ispage = True, user = user)

class PasteHandler(BaseHandler):
    def get(self, rid = None):
        html = ''
        html += """<br /> <br />
        <form action="/paste" method="POST">
        <input name="poster" type="text" />
        <select name="class">
          %s
        </select>
        <br />
        <textarea cols="110" rows="20" name="code"></textarea />
        <input type="submit" />
        </form>
        """ % get_option_tag()
        self.write(html)


    def post(self):
        poster = self.get_argument('poster', 'Anonymous')
        typ = self.get_argument('class', 'text')
        code = self.get_argument('code')

        lid = insert_code(poster, code, typ)

        self.redirect('/show/%d'%lid)


class ShowHandler(BaseHandler):
    _url = r'/show/(?P<rid>\d+)'
    def get(self, rid):
        html = ''
        text = self.get_argument('text', None)
        if rid:
            r = get_code(rid, text)
            html += """<html><head>
            <title>Pythoner Club Paste</title>
            <style type="text/css">%s</style></head><body><div class="hll">""" % r.get('css')
            html += r.get('code')
            html += "</div></body></html>"
            self.set_header("Content-Type", "text/html")
            if text:
                html = r.get('code')
                self.set_header("Content-Type", "text/plain")
            self.write(html)


