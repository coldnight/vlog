#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/10 13:08:52
#   Desc    :   生成站点地图
#
import os
from urllib import quote
from jinja2 import Environment, FileSystemLoader

from config import TEMPLATE_PATH, STATIC_PATH
from core.web import BaseHandler
from core.util import now

def handle_sitemap(logic, request):
    def make_url(path, lastmod, changefre='monthly', priority='0.3'):
        info = {}
        info['path'] = path
        info['lastmod'] = lastmod.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        info['changefreq'] = changefre
        info['priority'] = priority
        return info

    urls = []
    urls.append(make_url('/', now(), 'weekly', '0.8'))
    pages = logic.page.get_all_pages()
    for p in pages:
        path = "/page/{0}/".format(quote(p.get('link_title').encode("utf-8")))
        urls.append(make_url(path, p.get('pubdate')))

    posts = logic.post.get_all_posts()
    for p in posts:
        date = p.get("pubdate")
        path = "/{0}/{1}/{2}/{3}/".format(date.year, date.month, date.day,
                                         quote(p.get('link_title').encode("utf-8")))
        urls.append(make_url(path, p.get('pubdate')))

    cates = logic.category.get_categories().get("data")
    for c in cates:
        path = "/category/{0}/".format(quote(c.get('name').encode("utf-8")))
        urls.append(make_url(path, now(), 'weekly', '0.5'))

    tags = logic.tag.get_tags().get("data")
    for t in tags:
        path = "/tag/{0}/".format(quote(t.get("name").encode("utf-8")))
        urls.append(make_url(path, now(), 'weekly', '0.1'))

    months = logic.post.get_months()
    for m in months:
        path = "/date/{0}/{1}".format(m.get('year'), m.get('month'))
        urls.append(make_url(path, now(), 'monthly', '0.2'))

    template_path = 'sitemap.jinja'
    env = BaseHandler._path_to_evn.get(TEMPLATE_PATH)
    if not env:
        __loader = FileSystemLoader(TEMPLATE_PATH)
        env = Environment(loader = __loader)
        BaseHandler._path_to_evn[TEMPLATE_PATH] = env
    template = env.get_template(template_path)
    current = now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    content = template.render(urls = urls, request = request, now = current)
    static_path = os.path.join(STATIC_PATH, 'sitemap.xml')
    static_file = open(static_path, 'w')
    static_file.write(content)
    static_file.close()
