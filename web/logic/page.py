#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/09 11:15:56
#   Desc    :   页面逻辑
#
from .post import PostLogic

class PageLogic(PostLogic):
    _t = 'post'
    def get_page(self, pid):
        with self._mc() as op:
            where = "`id`='{0}' and `type`='2'"\
                    " and `enabled`='1'".format(op.escape(pid))
            r = op.select_one(where = where)
            if r:
                r = self.insert_info(r)

        return self.success(r)

    def get_page_by_link(self, link_title):
        return self.get_post_by_link(link_title, 2)

    def get_all_pages(self):
        with self._mc() as op:
            where="`type`='2' and `enabled`='1'"
            return op.select(where = where)

    def add_page(self, page_dict):
        page_dict['type'] = '2'
        title = page_dict.get('title')
        if not title:
            return self.error("必须提供页面标题")
        if self.check_exists(title):
            return self.error("页面已存在")

        return self.post(page_dict)

    def edit_page(self, pid, page_dict):
        return self.edit(pid, page_dict)

    def check_exists(self, title):
        with self._mc() as op:
            where = "`title`='{0}' and `type`='2'".format(op.escape(title))
            return op.select_one(where=where)
