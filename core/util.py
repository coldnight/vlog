#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#
#
import time
import json
import base64
import urllib
import urllib2
import logging
import hashlib

from config import DEBUG, LOG_PATH

md5 = lambda s: hashlib.md5(s + '3d2535f2ecf1dd3b7b').hexdigest()

def make_active_code(loginname, email):
    return base64.b64encode(md5(loginname + email + time.time()))

def send_active_email(email, activecode):
    pass

def page_bar(count, index, size):
    """ 生成页码 """
    totalpage = count / size if count % size == 0 else count / size + 1
    currentpage = index
    nextpage = index + 1 if (index + 1) <= totalpage else totalpage
    prevpage = index -1 if (index -1) >= 1 else 1

    return dict(totalpage = totalpage,
                currpage = currentpage,
                nextpage = nextpage,
                prevpage = prevpage)

def http_helpler(url, params, method = 'POST'):
    """ http请求辅助函数 """
    params = urllib.urlencode(params)
    if method.lower() == 'post':
        request = urllib2.Request(url, params)
    elif method.lower() == 'get':
        url += '?'+params
        request = urllib2.Request(url)
    else:
        raise ValueError('method error')

    response = urllib2.urlopen(request)
    tmp = response.read()
    result = json.loads(tmp)
    return result

def get_logger():
    logger = logging.getLogger()
    if DEBUG:
        hdl = logging.StreamHandler()
        level = logging.DEBUG
    else:
        level = logging.INFO
        hdl = logging.FileHandler(LOG_PATH)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    hdl.setFormatter(fmt)
    handler = hdl
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(level) # change to DEBUG for higher verbosity
    return logger

