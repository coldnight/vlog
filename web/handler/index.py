#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/14 17:19:47
#   Desc    :
#

from core.web import BaseHandler
from web.logic.code import insert_code, get_code
from web.logic.code import get_option_tag

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

