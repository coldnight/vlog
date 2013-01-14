#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/10 13:20:10
#   Desc    :   逻辑包
#
from .tag import TagLogic
from .category import CategoryLogic
from .post import PostLogic
from .comment import CommentLogic
from .page import PageLogic
from .options import GlobalOption, Options
from .user import UserLogic
from .upload import UploadLogic

class Logic(object):
    """ 使用类属性实例化各个逻辑类 """
    user = UserLogic()
    tag = TagLogic()
    category = CategoryLogic()
    post = PostLogic()
    page = PageLogic()
    comment = CommentLogic(post)
    option = GlobalOption()
    upload = UploadLogic()
    Options = Options
