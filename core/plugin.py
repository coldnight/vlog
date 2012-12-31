#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/31 11:28:56
#   Desc    :   插件
#

class PluginBus(object):
    """ 插件总线
        提供插件注册
    """
    registed = {}

    @classmethod
    def register(cls, location, action):
        actions = cls.registed.get(location, [])
        if action not in actions:
            actions.append(action)
        cls.registed[location] = actions
