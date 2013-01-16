#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/16 11:59:24
#   Desc    :   更新逻辑
#
from config import __version__
from core.util import get_logger
from .post import PostLogic
from .category import CategoryLogic
from .options import GlobalOption
from .page import PageLogic

class UpdateLogic(object):
    pl = PostLogic()
    cl = CategoryLogic()
    pal = PageLogic()
    option = GlobalOption()
    __version__ = float(''.join([str(v) for v in __version__]))

    def __init__(self):
        self.logger = get_logger()
        version = self.option.version
        version = float(version) if version else 0
        if version < self.__version__:
            self.update()
            self.option.version = self.__version__

    def update(self):
        self.logger.info("UPDATE to version %s",
                         '.'.join([str(v) for v in __version__]))
        self.update_table()
        self.update_post()
        self.update_page()

    def update_table(self):
        table = self.pl.get_table()
        sql = "alter table {0} add link_title VARCHAR(255) NULL;".format(table)
        self.logger.debug("UPDATE execute sql: %s", sql)
        self.pl.execute_sql(sql, commit = True)

        table = self.cl.get_table()
        sql = "alter table {0} add description VARCHAR(255) NULL;".format(table)
        self.logger.debug("UPDATE execute sql: %s", sql)
        self.pl.execute_sql(sql, commit = True)

    def update_post(self):
        posts = self.pl.get_all_posts()
        for post in posts:
            title = post.get("title")
            pid = post.get("id")
            link_title = self.pl.get_link_title(title)
            post['link_title'] = link_title
            post['isdraft'] = 0
            self.pl.edit(pid, post)

    def update_page(self):
        pages = self.pal.get_all_pages()
        for p in pages:
            title = p.get("title")
            pid = p.get("id")
            link_title = self.pal.get_link_title(title)
            p['link_title'] = link_title
            p['isdraft'] = 0
            self.pal.edit_page(pid, p)
