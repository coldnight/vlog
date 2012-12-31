#!/usr/bin/env python
#-*- coding:utf8 -*-
#
#
#
import config as config
from pymongo import Connection
from gridfs import GridFS

class MongoContext:
    def __init__(self, host = None, name = None):
        self.host = host if host else config.MONGO_DB_HOST
        self.port = None
        if ':' in self.host:
            self.host, self.port = self.host.split(':')
        self.port = int(self.port) if self.port else 27017
        self.name = name if name else config.MONGO_DB_NAME
        self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, ex_typ, ex_value, trace):
        self.close()

    @property
    def db(self, name = None):
        self.conn = Connection(host = self.host, port = self.port)
        name = name if name else self.name
        return self.conn[name]

    def close(self):
        if self.conn:
            self.conn.disconnect()

    def gfs(self, name = None):
        return GridFS(self.db(name))

    def gfs_put(self, data, filename, **kwargs):
        return self.gfs.put(data, filename = filename, **kwargs)

    def gfs_get(self, fid):
        with self.gfs.get(fid) as out:
            return out.read(), out._file
