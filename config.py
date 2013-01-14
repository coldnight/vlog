#-*- coding:utf-8 -*-
import os
import sys

PORT = 18888

MONGO_DB_HOST = 'localhost:27017'
MONGO_DB_NAME = 'pec'

MYSQL_DB_HOST = 'localhost'
MYSQL_DB_PORT = 3306
MYSQL_DB_NAME = 'pec'
MYSQL_DB_USER = 'root'
#MYSQL_PRE = 'vlog_'
MYSQL_PRE = ''
MYSQL_DB_PWD = ''

CACHED = True

CACHE_HOST = ["localhost:11211"]

CACHE_USER = ''

CACHE_PWD = ''

CACHE_TIMEOUT = 0   # 缓存过期时间,单位为秒, 0不过期

DEBUG = True

ROOT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))

STATIC_PATH = os.path.join(ROOT_PATH, 'web/static')

TEMPLATE_PATH = os.path.join(ROOT_PATH, 'web/template')

UPLOAD_PATH = os.path.join(STATIC_PATH, 'upload')

sys.path.insert(0, ROOT_PATH)

HANDLER = 'web.handler'

UTEST = 'utest'

CODERUN = "http://1.pyec.sinaapp.com/"

LOG_PATH = os.path.join(ROOT_PATH, 'logs/default.log')

