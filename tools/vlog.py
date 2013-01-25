#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/24 09:24:19
#   Desc    :   vLog 终端脚本
#   History :
#               0.0.1 可以发布,修改,列出文章,可以发布便签
#
import os
import sys
import time
import hashlib
import argparse
import urllib, urllib2, json
import cookielib
import mimetools
import mimetypes
import itertools

from datetime import datetime

import markdown

from jinja2 import Template

DEBUG = True
__HOST__ = "http://localhost:18888"
__USER__ = ""
__PWD__ = ""

MD5 = lambda s: hashlib.md5(s.encode("utf-8")
                            if isinstance(s, unicode) else s).hexdigest()
FDATE = lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

########### HTTP Helper ####################################
class UploadForm(object):
    """ 表单类,用于post表单和上传文件 """
    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        self.content_type = 'multipart/form-data; boundary=%s' % self.boundary
        return

    def get_content_type(self):
        """ 获取表单类型 """
        return self.content_type

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """ 添加文件 """
        body = fileHandle.read()
        if mimetype is None:
            mimetype = ( mimetypes.guess_type(filename)[0]
                         or
                         'applicatioin/octet-stream')
        self.files.append((fieldname, filename, mimetype, body))

        return

    def __str__(self):
        parts = []
        part_boundary = '--' + self.boundary

        parts.extend(
            [ part_boundary,
             'Content-Disposition: form-data; name="%s"' % name,
             '',
             value,
             ]
            for name, value in self.form_fields)
        if self.files:
            parts.extend([
                part_boundary,
                'Content-Disposition: form-data; name="%s"; filename="%s"' %\
                (field_name, filename),
                'Content-Type: %s' % content_type,
                '',
                body,
            ] for field_name, filename, content_type, body in self.files)

        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class PostForm(object):
    def __init__(self):
        self.params = {}

    def add_field(self, key, value):
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        self.params.update({key:value})

    def as_string(self):
        return str(self)

    def __str__(self):
        return urllib.urlencode(self.params)

class HttpHelper(object):
    """ HTTP 请求助手 """
    def __init__(self, url = None, params = {}):
        self._url = url
        self._params = params
        self._cookiejar = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookiejar))
        self._realurl = None
        if url:
            self.make_request()

    def make_request(self):
        """ 构造请求 """
        url = self._url
        if not self._url.startswith('http://'):
            url = 'http://' + self._url
        if isinstance(self._params, (tuple, list, dict)):
            params = self._params
            if isinstance(params, (tuple, list)):
                params = list(params)
                params.append(("username", __USER__))
                params.append(("password", __PWD__))
                params = tuple(params)

            if isinstance(params, dict):
                params.update(username = __USER__, password = __PWD__)
            params = urllib.urlencode(params)
            self.request = urllib2.Request(url + "?" + params)
        elif isinstance(self._params, PostForm):
            self._params.add_field("username", __USER__)
            self._params.add_field("password", __PWD__)
            self.request = urllib2.Request(url, str(self._params))
        elif isinstance(self._params, UploadForm):
            self._params.add_field("username", __USER__)
            self._params.add_field("password", __PWD__)
            body = str(self._params)
            self.request = urllib2.Request(url)
            self.add_header("Content-Type", self._params.get_content_type())
            self.add_header("Content-Length", len(body))
            self.request.add_data(body)
        else:
            raise ValueError, "params must is instance of tuple, dict Form"

    def add_header(self, key, val):
        """ 为请求添加头部信息 """
        self.request.add_header(key, val)

    def change(self, url, params = {}):
        """ 改变请求 """
        self._url = url
        self._params = params
        self.make_request()

    def change_params(self, params):
        """ 改变参数 """
        self._params = params
        self.make_request()

    def get_url(self):
        return self._realurl

    def open(self):
        """ 打开请求 """
        response = self._opener.open(self.request)
        self._realurl = response.geturl()
        content = response.read()
        try:
            return json.loads(content)
        except:
            return content

############## Request #############################################
class BaseRequest(object):
    """ 所有请求vLog的基类 """
    _path = None
    def __init__(self, host = None):
        self.host = host if host else __HOST__
        self._http_helper = HttpHelper(self.host + self._path)

    def get(self, index = 1, size = 10, **kwargs):
        """ get 方法 """
        kwargs.update(pageindex = index, pagesize = size)
        self._http_helper.change_params(kwargs)
        return self._http_helper.open()

    def post(self, **kwargs):
        """ post 方法 """
        form = PostForm()
        [form.add_field(key, value) for key, value in kwargs.items()]
        self._http_helper.change_params(form)
        return self._http_helper.open()

    def upload(self, fieldname, path):
        """ 上传文件
        - `path`      文件路径
        """
        form = UploadForm()
        filename = os.path.split(path)[-1]
        form.add_file(fieldname=fieldname, filename=filename,
                      fileHandle=open(path))
        self._http_helper.change_params(form)
        return self._http_helper.open()

    def get_url(self):
        return self._http_helper.get_url()


class NoteRequest(BaseRequest):
    _path = "/i/note/"

class PostRequest(BaseRequest):
    _path = "/i/post/"

    def get_one(self, pid):
        return self.get(id = pid)

class CategoryRequest(BaseRequest):
    _path = "/i/category/"

################ Action #######################################
class Note(object):
    def __init__(self):
        self.request = NoteRequest()

    def add_note(self, content):
        return self.request.post(content = content)

    def get_note(self, index = 1, size = 10):
        return self.request.get(index, size)


new_temp = """Title is here  ::: (标题前面加*可保存为草稿)
====================
Content is here
====================
{% for c in categories %}# {{c}}
{% endfor %}
====================
Tags:用,号隔开"""

edit_temp = """{{post.title}}  ::: (标题前面加*可保存为草稿)
====================
{{post.source}}
====================
{% for c in categories %}{% if c in post_category %}{{c}}{% else %}# {{c}}{% endif %}
{% endfor %}
====================
Tags: {{ post.ttags }}"""

class Post(object):
    def __init__(self):
        self.request = PostRequest()
        self.crequest = CategoryRequest()
        editor = os.getenv("EDITOR")
        self._editor = editor if editor else 'vi'
        categories = self.crequest.get().get("data")
        self.categories = [v.get("name") for v in categories]

        return

    def parse_post(self, path):
        post_dict = {"source":''}
        categories = []
        with open(path, 'r') as f:
            step = 0
            for line in f.readlines():
                if line.strip() == '='* 20:
                    step += 1
                    continue
                if step == 0:
                    post_dict["isdraft"] = 0
                    title =  line.strip().split(":::")[0].strip()
                    post_dict["title"] = title
                    if title.startswith("*"):
                        post_dict["isdraft"] = 1
                if step == 1:
                    post_dict["source"] += line
                if step == 2:
                    if not line.startswith("#") and line.strip():
                        categories.append(line.strip())
                if step == 3:
                    post_dict["tags"] = ':'.join(line.strip().split(":")[1:]).strip()
        post_dict["category"] = ",".join(categories)
        source = post_dict.get("source").decode('utf-8')
        post_dict["content"] = markdown.markdown(source, ['fenced_code'])
        return post_dict

    def edit(self, pid):
        result = self.request.get(id = pid, action="edit")
        post = result.get("post", {}).get("data")
        draft = result.get("draft")
        yes = 'n'
        if draft:
            old_date = FDATE(post.get("update"))
            new_date = FDATE(draft.get("update"))
            if old_date <= new_date:
                while True:
                    yes = raw_input("有一篇草稿保存日期比当前文章要晚,"
                                    "是否操作草稿(Y/N): ")
                    if yes.lower() in ["y", "n"]: break
                if yes.lower() == "y":
                    post = draft
        post_category = [c.get("name") for c in post.get("category")]
        t = Template(edit_temp.decode("utf-8"))
        content = t.render(post = post, categories = self.categories,
                    post_category = post_category)
        oldmd5 = MD5(content)
        path = '/tmp/{0}.md'.format(pid)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(content.encode("utf-8"))
        last = os.system("{0} {1}".format(self._editor, path))
        with open(path, 'r') as f:
            if MD5(f.read()) == oldmd5:
                print "没有更改"
                sys.exit(2)
        if last == 0:
            post_dict = self.parse_post(path)
            p = self.request.post(id=pid, **post_dict)
            date = FDATE(p.get("pubdate"))
            url = u"{0}/{1}/{2}/{3}/{4}/".format(self.request.host,
                                                date.year, date.month,
                                                date.day, p.get("link_title"))
            if post_dict.get("isdraft") == 1:
                print "草稿已保存"
            else:
                print "已发布,文章链接:",
                print url
            os.remove(path)


    def new(self, path = None):
        path = path if path else  '/tmp/{0}.md'.format(time.time())
        t = Template(new_temp.decode("utf-8"))
        content = t.render(categories = self.categories)
        oldmd5 = MD5(content)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(content.encode("utf-8"))
        last = os.system("{0} {1}".format(self._editor, path))
        with open(path, 'r') as f:
            if MD5(f.read()) == oldmd5:
                print "没有更改"
                sys.exit(2)
        if last == 0:
            post_dict = self.parse_post(path)
            p  = self.request.post(**post_dict)
            date = datetime.strptime(p.get("pubdate"), "%Y-%m-%d %H:%M:%S")
            url = u"{0}/{1}/{2}/{3}/{4}/".format(self.request.host,
                                                date.year, date.month,
                                                date.day, p.get("link_title"))
            if post_dict.get("isdraft") == 1:
                print "草稿已保存"
            else:
                print "已发布,文章链接:",
                print url

    def list(self, index = None, size = None):
        index = index if index else 1
        size = size if size else 10
        r = self.request.get(index = index, size = size)
        posts = r.get("data")
        if not posts:
            print "文章列表为空"
            return
        pageinfo = r.get("pageinfo")
        for p in posts:
            print "文章id:", p.get("id")
            print "标题:", p.get("title")
            date = datetime.strptime(p.get("pubdate"), "%Y-%m-%d %H:%M:%S")
            url = u"{0}/{1}/{2}/{3}/{4}/".format(self.request.host,
                                                date.year, date.month,
                                                date.day, p.get("link_title"))
            print u"链接:", url
            print '-'* 40
        print "当前页", pageinfo.get("pageindex"),
        print "总页数", pageinfo.get("totalpage")

        return

    def remove(self, pid):
        self.request.get(id = pid, action="remove")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="items")
    note_parser = subparsers.add_parser("note", help="Notes")
    note_parser.add_argument(dest="content", default=None, nargs="?")

    post_parser = subparsers.add_parser("post", help="Post")
    post_parser.add_argument("-l", "--list", action="store_const",
                             dest="action", default="list", const="list",
                             help="List posts")

    post_parser.add_argument("-e", "--edit",action="store_const",
                             dest="action", default="list", const="edit",
                             help="Edit id [pid] post")

    post_parser.add_argument("-n", "--new", action="store_const",
                             dest="action", default="list", const="new",
                             help = "Add a new post")
    post_parser.add_argument("-r", "--remove", action="store_const",
                             dest="action", default="list", const="remove",
                             help = "Delete a post")
    post_parser.add_argument(dest="value", default=None, nargs="?")
    post_parser.add_argument(dest="value2", default=None, nargs="?")

    args = parser.parse_args()
    if hasattr(args, "content"):
        note = Note()
        if args.content:
            result = note.add_note(args.content)
            if not result.get("status"):
                print u"添加失败"
        else:
            result = note.get_note()
            if result.get("status"):
                data = result.get("data")
                for n in data:
                    print n.get("name"), ":"
                    print n.get("content")
                    print "=" * 10
            else:
                print result.get("errmsg")
    elif hasattr(args, "action"):
        if args.action == "edit":
            pid = args.value
            if not pid:
                print "没有指定文章的id"
                sys.exit(3)
            Post().edit(pid)
        elif args.action == "new":
            path = args.value
            Post().new(path)
        elif args.action == "list":
            Post().list(args.value, args.value2)
        elif args.action == "remove":
            Post().remove(args.value)
