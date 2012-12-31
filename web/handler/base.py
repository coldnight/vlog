#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 09:56:59
#   Desc    :   自定义处理基类
#
from os.path import join as path_join
from web.logic.info import InfoLogic
from core.web import BaseHandler


class WebHandler(BaseHandler):
    def render(self, template_path, **kwargs):
            il = InfoLogic()
            theme = il.get_theme()
            super(WebHandler, self).render(path_join(theme, template_path),
                                           **kwargs)
