#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/10 15:45:22
#   Desc    :   RSS输出
#
import os
from urllib import quote

from config import TEMPLATE_PATH, STATIC_PATH
from core.web import BaseHandler
from core.util import now
from jinja2 import Environment, FileSystemLoader

timeformat = "%a, %d %b %Y %H:%M:%S +0000"

def handle_rss(logic, request):
    posts = logic.post.get_posts().get("data")
    for p in posts:
        p["link_title"] = quote(p.get("link_title").encode("utf-8"))
        p['rss_date'] = p.get('pubdate').strftime(timeformat)

    template_path = 'rss.jinja'
    env = BaseHandler._path_to_evn.get(TEMPLATE_PATH)
    if not env:
        __loader = FileSystemLoader(TEMPLATE_PATH)
        env = Environment(loader = __loader)
        BaseHandler._path_to_evn[TEMPLATE_PATH] = env
    template = env.get_template(template_path)
    content = template.render(posts = posts, request = request,
                              buildDate = now().strftime(timeformat),
                              SITE_TITLE = logic.option.site_title,
                              description = logic.option.description)
    static_path = os.path.join(STATIC_PATH, 'rss.xml')
    static_file = open(static_path, 'w')
    static_file.write(content.encode('utf-8'))
    static_file.close()
