#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/16 11:59:24
#   Desc    :   更新逻辑
#
from core.util import get_version
from mycnf import MYSQL_PRE
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
    __version__ = get_version()

    def __init__(self):
        self.logger = get_logger()
        version = self.option.version
        version = float(version) if version else 0
        if version < self.__version__:
            self.update(version)
            self.option.version = self.__version__

    def update(self, version):
        self.logger.info("UPDATE to version %f", self.__version__)
        if version < 0.10:
            self.update_table()
            self.update_post()
            self.update_page()

        if version < 0.11:
            self.update_links_table()

        if version < 0.12:
            self.update_post_index()

    def update_post_index(self):
        sql = "create index link_title on {0}(`link_title`)".format(
            self.pl.get_table())
        self.pl.execute_sql(sql, commit = True)

    def update_links_table(self):
        table_sql = """create table if not exists `{0}links`(
            id INT AUTO_INCREMENT NOT NULL,
            `text` VARCHAR(255) NOT NULL,
            `url` VARCHAR(255) NOT NULL,
            `order` TINYINT NOT NULL default 0,
            date TIMESTAMP NOT NULL,
            PRIMARY KEY(`id`))character set utf8""".format(MYSQL_PRE)
        self.pl.execute_sql(table_sql, commit = True)

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
