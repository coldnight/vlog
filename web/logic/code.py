#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/18 10:47:19
#   Desc    :   贴代码逻辑
#
#
#
#
from core.db import MySQLContext as LogicContext
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight

def insert_code(poster, code, typ):
    with LogicContext('code') as op:
        lid = op.insert(['poster', 'code', 'class'], [poster, code, typ])
        return lid


def get_code(_id, text = False):
    with LogicContext('code') as op:
        r= op.select(('poster', 'class', 'code', 'date'),
                     where="id="+"'"+_id+"'")
        result = r[0]
        print result
        if not text:
            lexer = get_lexer_by_name(result.get('class', 'text'))
            formatter = HtmlFormatter(
                encoding='utf-8', style="friendly", linenos= True,
                linenostart = 1, linenospecial = 5 )
            code = highlight(result.get('code', ''), lexer, formatter)
            css = formatter.get_style_defs()
            result['code'] = code
            result['css'] = css
        return result



all_lexers = ['actionscript', 'ada', 'apache', 'bash', 'c', 'c#', 'cpp',
              'css', 'django', 'erlang', 'go', 'html', 'java', 'javascript',
              'jsp', 'lighttpd', 'lua', 'matlab', 'mysql', 'nginx',
              'objectivec', 'perl', 'php', 'python', 'python3', 'ruby',
              'scheme', 'smalltalk', 'smarty', 'sql', 'sqlite3', 'squid',
              'tcl', 'text', 'vb.net', 'vim', 'xml', 'yaml']


def get_option_tag():
    r = ''
    for t in all_lexers:
        t = '<option value="%s">%s</option>\n' % (t, t.capitalize())
        r+= t
    return r
