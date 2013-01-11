#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/11 09:55:14
#   Desc    :   文件上传逻辑
#
import os
import urllib
from config import UPLOAD_PATH
from core.util import get_logger, md5
from .options import Options

class UploadLogic(object):
    """ 文件上传逻辑 """
    root = UPLOAD_PATH
    url_format = r"/upload/{0!r}"
    option = Options("upload")

    def __init__(self):
        self.logger = get_logger()
        self.logger.info("UPLOAD_PATH %s", UPLOAD_PATH)
        if not os.path.exists(self.root):
            self.logger.debug("create upload_dir %s", self.root)
            os.makedirs(self.root)

    def get_filename(self, filename, file_md5, num = None):
        newfilename = filename
        if num:
            split = filename.split('.')
            if len(split) >= 2:
                newfilename = '.'.join(split[0:-1]) + str(num) +'.'+ split[-1]
            else:
                newfilename = filename + str(num)
        path = os.path.join(self.root, newfilename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                old_md5 = md5(f.read())
            if old_md5 == file_md5:
                return path, newfilename, False
            num = num+1 if num else 1
            return self.get_filename(filename, num)
        return path, newfilename, True

    def upload(self, upload_file, filename, abspath = False):
        file_md5 = md5(upload_file)
        path, filename, create = self.get_filename(filename, file_md5)
        if create:
            with open(path, 'wb') as f:
                f.write(upload_file)
        url_path = self.url_format.format(filename)
        self.option.set_option(filename, url_path)
        if abspath:
            return path
        return urllib.quote(url_path)
