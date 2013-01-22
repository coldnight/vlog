#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/11 12:36:00
#   Desc    :   从WordPress导入
#
import os, urlparse
from xml.etree import cElementTree  as ET

class FromWPLogic(object):
    wp = "{http://wordpress.org/export/1.2/}"
    content = "{http://purl.org/rss/1.0/modules/content/}"

    def __init__(self, Logic, path):
        self.logic = Logic
        self.path = path
        self.uid = self.logic.user.check_has_admin().get('id')
        self.upload_links = []

    def load(self):
        with open(self.path, 'rt') as f:
            self.et = ET.parse(f)

    def parse(self):
        self.load()
        root = self.et.getroot()
        channel = root.getchildren()[0]
        result = {"posts":[]}
        titles = []
        for el in channel.findall(r'./item'):
            typ = el.find(self.wp + "post_type").text
            status = el.find( self.wp + "status")
            if typ == 'attachment':
                link = el.find(self.wp + "attachment_url")
                self.upload_links.append(link.text)
            if typ not in ['post', 'page'] or status.text != "publish":
                continue
            info = {'author':self.uid}
            info['type'] = '1' if typ == "post" else '2'
            for e in el.getchildren():
                if e.tag == 'title':
                    info['title'] = e.text
                    info['link_title'] = self.logic.post.get_link_title(e.text)
                if e.tag == 'link':
                    info['link'] = e.text
                if e.tag == self.content + "encoded":
                    info['content'] = e.text
                    info['source'] = e.text

                if e.tag == self.wp+"post_date":
                    info['pubdate'] = e.text
                if e.tag == self.wp+"post_date_gmt":
                    info['update'] = e.text

                if e.tag == self.wp + "post_id":
                    info['id'] = e.text

                if e.tag == 'category':
                    if e.attrib['domain'] == 'post_tag':
                        if info.has_key("tags"):
                            info['tags'].append(e.text)
                        else:
                            info['tags'] = [e.text]
                    elif e.attrib['domain'] == 'category':
                        if info.has_key("category"):
                            info["category"].append(e.text)
                        else:
                            info["category"] = [e.text]
                if e.tag == self.wp + "postmeta":
                    key = e.find(self.wp + "meta_key").text
                    value = e.find(self.wp + "meta_value").text
                    if info.has_key("options"):
                        info["options"].append((key,value))
                    else:
                        info["options"] = [(key,value)]


                if e.tag == self.wp + "comment":
                    #TODO comment_type pingback
                    ctyp = e.find(self.wp + "comment_type").text
                    if ctyp == 'pingback': continue
                    author_name = e.find(self.wp + "comment_author").text
                    author_email = e.find(self.wp + "comment_author_email").text
                    author_url = e.find(self.wp + "comment_author_url").text
                    author_ip = e.find(self.wp + "comment_author_IP").text
                    comment_date = e.find(self.wp + "comment_date").text
                    content = e.find(self.wp + "comment_content").text
                    author_email = author_email if author_email else ''
                    comment = {"name":author_name, "email":author_email,
                               "url":author_url, "ip":author_ip, 'allowed':'1',
                               "date":comment_date, "content":content}
                    if info.has_key("comments"):
                        info["comments"].append(comment)
                    else:
                        info["comments"] = [comment]

                if info.get("title") not in titles:
                    result["posts"].append(info)
                    titles.append(info.get("title"))
        return result

    def start(self):
        """ 导入数据 """
        posts = self.parse().get("posts")
        id_to_link = []
        for p in posts:
            comments = p.pop("comments", [])
            options = p.pop("options", [])
            link = p.pop("link", None)
            pid = self.logic.post.post(p).get("data")
            id_to_link.append((pid, link))
            op = self.logic.Options(pid)
            for key, value in options:
                op.set_option(key, value)
            for c in comments:
                self.logic.comment.add_comment(pid, c)
        self.replace_link(id_to_link)


    def _replace_post_link(self, id_to_link, content, source = None):
        for _id, link in id_to_link:
            content = content.replace(link, "/post/"+ str(_id))
            if source:
                source = source.replace(link, "/post/" + str(_id))

        for link in self.upload_links:
            filename = os.path.split(urlparse.urlparse(link).path)[-1]
            content = content.replace(link, "/upload/"+filename)
            if source:
                source = source.replace(link, "/upload/"+filename)

        return content, source

    def replace_link(self, id_to_link):
        """ 替换文章内原有的链接 """
        posts = self.logic.post.get_all_posts()
        for p in posts:
            pid = p.pop("id")
            content = p.get("content")
            source = p.get("source")
            p['content'], p['source'] = self._replace_post_link(id_to_link, content, source)
            self.logic.post.edit(pid, p)
