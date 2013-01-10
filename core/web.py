#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/17 12:43:23
#   Desc    :   Handler 基类和Session
#   History :
#               + 2012/12/17 增加Session类使框架支持Session
#
import time
import threading
from uuid import uuid1
from tornado.web import RequestHandler
from jinja2 import Environment, FileSystemLoader
from config import TEMPLATE_PATH
from .util import get_logger

class Session(object):
    """
        Session 类
        使用类方法和类属性作为Session
        并开启定时器线程定时清理session
        example:
            >>> session = Session(get_cookie, set_cookie)
            >>> session.i = 3
            >>> session.i
            3
            >>> session.set(key = 'i', value= 3, expirse = 600)
            >>> session.get('i')
            3
    """
    _sessions = dict()
    __SID_COOKIE = "__SID__"
    _get_cookie = None
    _set_cookie = None
    _lock = threading.RLock()

    @classmethod
    def timer(cls, interval = 10):
        """ 定时器
            interval - 执行间隔 单位为秒
        """
        while True:
            with cls._lock:
                sdroplist = []
                for sid in cls._sessions:
                    vdroplist = []
                    value = cls._sessions[sid]
                    for k in value:
                        v = value[k]
                        ctime = v.get('ctime')
                        expirse = v.get('expirse')
                        if (time.time() - ctime) > expirse:
                            vdroplist.append((sid, k))
                    [cls._sessions[s].pop(v, None) for s, v in vdroplist]
                    value = cls._sessions[sid]
                    if not value:
                        sdroplist.append(sid)
                [cls._sessions.pop(s, None) for s in sdroplist]
            time.sleep(interval)

        return

    @classmethod
    def set_session(cls, key, value, expirse=600):
        """ 设置session
            `key` - session键
            `value` - session值
            `expirse` - 过期时间 单位为秒
        """
        assert cls._get_cookie and cls._set_cookie \
                and callable(cls._get_cookie) and callable(cls._set_cookie)
        sid = cls._get_cookie(cls.__SID_COOKIE)
        if not sid:
            sid = str(uuid1())
            cls._set_cookie(cls.__SID_COOKIE, sid)
        with cls._lock:
            cls._sessions[sid] = {key : dict(value = value,
                                             ctime = time.time(),
                                             expirse = expirse)}

    @classmethod
    def get_session(cls, key):
        """ 获取session """
        assert cls._get_cookie and cls._set_cookie \
                and callable(cls._get_cookie) and callable(cls._set_cookie)
        sid = cls._get_cookie(cls.__SID_COOKIE)
        with cls._lock:
            tmp = cls._sessions.get(sid,{}).get(key)
            if not tmp:
                return None
            ctime = tmp.get('ctime')
            expirse = tmp.get('expirse')
            value = tmp.get('value')
            if time.time() - ctime > expirse:
                cls._sessions[sid].pop(key)
                return None
            cls._sessions[sid][key]['ctime'] = time.time()
        return value

    @classmethod
    def session(cls, get_cookie, set_cookie):
        """ 初始化Session,并启动定时器 """
        assert get_cookie and set_cookie \
                and callable(get_cookie) and callable(set_cookie)
        cls._get_cookie = get_cookie
        cls._set_cookie = set_cookie
        threadnames = [th.name for th in threading.enumerate()]
        if 'timer' not in threadnames:
            t = threading.Thread(name='timer', target=cls.timer)
            t.setDaemon(True)
            t.start()
        return cls

    def __init__(self, get_cookie, set_cookie):
        Session.session(get_cookie, set_cookie)

    def __getattr__(self, key):
        return Session.get_session(key)

    def __setattr__(self, key, value):
        Session.set_session(key, value)

    def set(self, key, value, expirse=600):
        Session.set_session(key, value, expirse)

    def get(self, key):
        return Session.get_session(key)


class BaseHandler(RequestHandler):
    template_path = TEMPLATE_PATH
    _path_to_evn = {}
    _USER_ = '__CURRNET_USER__'
    _USER_ID_ = "__CURRENT_USER_ID__"
    username = property(lambda self: self.get_secure_cookie(self._USER_))
    uid = property(lambda self: self.get_secure_cookie(self._USER_ID_))
    logger = get_logger()

    def login(self, username, uid, redirect = None):
        self.set_secure_cookie(self._USER_, username, expires_days=None)
        self.set_secure_cookie(self._USER_ID_, str(uid), expires_days = None)
        if redirect:
            self.redirect(redirect)

    def logout(self, redirect = None):
        self.clear_cookie(self._USER_)
        self.clear_cookie(self._USER_ID_)
        if redirect:
            self.redirect(redirect)


    def render(self, template_path, **kwargs):
        env = BaseHandler._path_to_evn.get(self.template_path)
        if not env:
            __loader = FileSystemLoader(self.template_path)
            env = Environment(loader = __loader)
            BaseHandler._path_to_evn[self.template_path] = env
        t = env.get_template(template_path)
        kwargs['request'] = self.request
        content = t.render(**kwargs)
        self.finish(content)

    @property
    def session(self):
        return Session(self.get_secure_cookie, self.set_secure_cookie)

    def prepare(self):
        super(BaseHandler, self).prepare()

__all__ = ['BaseHandler']
