#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   code
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 17:31:53
#   Desc    :   任务
#
from config import *
from core.web import BaseHandler

class PingRPCTask(BaseHandler):
    def get(self):
        for n in range(len(XML_RPC_ENDPOINTS)):
            add_task('default', '%s/task/pingrpc/%d' % (BASE_URL, n))
        self.write(str(time()))

    post = get

class PingRPC(BaseHandler):
    _url = r"/task/pingrpc/(\d+)"
    def get(self, n = 0):
        import urllib2

        pingstr = self.render('rpc.xml', {'article_id':Article.get_max_id()})

        headers = {
            'User-Agent':'request',
            'Content-Type' : 'text/xml',
            'Content-length' : str(len(pingstr))
        }

        req = urllib2.Request(
            url = XML_RPC_ENDPOINTS[int(n)],
            headers = headers,
            data = pingstr,
        )
        try:
            content = urllib2.urlopen(req).read()
            tip = 'Ping ok' + content
        except:
            tip = 'ping erro'

        self.write(str(time()) + ": " + tip)
        #add_task('default', '%s/task/sendmail'%BASE_URL, urlencode({'subject': tip, 'content': tip + " " + str(n)}))

    post = get

class SendMail(BaseHandler):
    def post(self):
        subject = self.get_argument("subject",'')
        content = self.get_argument("content",'')

        if subject and content:
            sae.mail.send_mail(NOTICE_MAIL, subject, content,(MAIL_SMTP, int(MAIL_PORT), MAIL_FROM, MAIL_PASSWORD, True))


