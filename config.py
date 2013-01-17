#-*- coding:utf-8 -*-
import os
import sys

PORT = 18888

DEBUG = True

CACHED = True

CACHE_HOST = ["localhost:11211"]

CACHE_USER = ''

CACHE_PWD = ''

CACHE_TIMEOUT = 0   # 缓存过期时间,单位为秒, 0不过期

ROOT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))

STATIC_PATH = os.path.join(ROOT_PATH, 'web/static')

TEMPLATE_PATH = os.path.join(ROOT_PATH, 'web/template')

UPLOAD_PATH = os.path.join(STATIC_PATH, 'upload')

sys.path.insert(0, ROOT_PATH)

HANDLER = 'web.handler'

UTEST = 'utest'

THEME = 'octopress'          # 主题

LOG_PATH = os.path.join(ROOT_PATH, 'logs/default.log')

EMAIL_ACCOUNT = "blog.linuxzen@gmail.com"

EMAIL_PASSWORD = ""

__version__ = (0, 1, 2)
