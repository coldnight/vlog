#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/18 14:12:08
#   Desc    :   便签
#
import urllib, urllib2, json


__username__ = ""
__password__ = ""
__host__ = "http://www.linuxzen.com"

class HttpHelper(object):
    def __init__(self, url = None, params = {}, method = 'GET'):
        self._url = url
        self._params = params
        self._method = method
        self.cookies = []
        if url:
            self.make_request()

    def make_request(self):
        params = urllib.urlencode(self._params)
        method = self._method
        url = self._url
        if not self._url.startswith('http://'):
            url = 'http://' + self._url
        if method == 'GET':
            self.request = urllib2.Request(url + "?" + params)
        else:
            self.request = urllib2.Request(url, params)
        if self.cookies:
            self.add_header('Cookie', ';'.join(self.cookies))

    def add_header(self, key, val):
        self.request.add_header(key, val)

    def change(self, url, params = {}, method = 'GET'):
        self._url = url
        self._params = params
        self._method = method
        self.make_request()

    def open(self):
        response = urllib2.urlopen(self.request)
        cookies = response.headers.dict.get('set-cookie')
        if cookies:
            self.cookies.append(cookies)
        content = response.read()
        try:
            return json.loads(content)
        except:
            return content

class Note(object):
    url = "/i/note/"
    http = HttpHelper()
    base_params = {"username":__username__, "password":__password__}
    def add_note(self, content):
        params = {"content":content}
        params.update(self.base_params)
        self.http.change(__host__ + self.url, params, "POST")
        return self.http.open()

    def get_note(self, index = 1, size = 10):
        params = {"pageindex":index, "pagesize":size}
        params.update(self.base_params)
        self.http.change(__host__ + self.url, params, "GET")
        return self.http.open()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("notes.py")
    parser.add_argument(dest="content", nargs="?")
    args = parser.parse_args()

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

