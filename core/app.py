#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#
import os
from os.path import join
from inspect import isclass
from tornado.web import RequestHandler as BaseHandler
from config import ROOT_PATH, STATIC_PATH, HANDLER, DEBUG

def get_modules(pkg_name, pkg_path, filter_func):
    modules = [m.split('.')[0] for m in os.listdir(pkg_path)
               if filter_func(m)]
    modules = list(set(modules))
    pkgs = pkg_name.split('.')
    result = []
    for m in modules:
        tmp = __import__('{0}.{1}'.format(pkg_name, m))
        for p in pkgs:
            try:
                tmp = tmp.__dict__[p]
            except KeyError:
                continue
        result.append(tmp.__dict__[m])
    return result

def load_apps():
    pkg_name = HANDLER
    pkg_path = join(ROOT_PATH, pkg_name.replace('.', '/'))
    modules = get_modules(pkg_name, pkg_path,
                          lambda x: all((
                              not x.startswith('_'),
                              not x.startswith('.'),
                               ))
                          )
    result = dict()
    for module in modules:
        name = module.__name__.split('.')[-1]
        for n, cls in module.__dict__.items():
            if isclass(cls) and issubclass(cls,BaseHandler) \
               and cls is not BaseHandler:

                if hasattr(cls, '_url'):
                    result.update({cls._url:cls})
                else:
                    key = '/{0}/{1}'.format(name.lower().replace("index",""),
                                        n.lower().replace('handler', '')\
                                            .replace("index", ""))
                    result.update({key: cls})
    tmp = dict()
    for key in result:
        nkey = key.replace('//', '/')
        if nkey == '': nkey = '/'
        tmp[nkey] = result[key]
        # tmp[key] = result[key]
    return tmp


settings = {
    "static_path": STATIC_PATH,
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "xsrf_cookies": False,
    "debug": DEBUG,
    "gzip":True,
}


__all__ = ['load_apps', 'settings']
