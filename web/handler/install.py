#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/22 14:53:59
#   Desc    :   安装
#
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
                self.admin_login(username, admin_id.get("data"))
            handle_sitemap(Logic, self.request)
            handle_rss(Logic, self.request)
            self.write(admin_id)


