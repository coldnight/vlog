#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   12/12/25 15:27:57
#   Desc    :   MySQL数据库操作
#
#
#
#
import mycnf as config
import MySQLdb as mysqldb
from MySQLdb import escape_string

from core.util import get_logger



class Field(object):
    def __init__(self, fields):
        self.field = {}
        for field in fields:
            n, t, nu, k, d, e = field
            self.field[n] = {}
            self.field[n]['field'] = n
            self.field[n]['type'] = t
            self.field[n]['null'] = nu
            self.field[n]['key'] = k
            self.field[n]['default'] = d
            self.field[n]['extra'] = e

    def get_field_list(self):
        return self.field.keys()

    def __getattr__(self, key):
        return self.field.get(key, None)

    def __str__(self):
        return '`{0}`'.format('`, `'.join(self.field.keys()))


class DatabaseOp(object):
    """ 操作MySQL """
    def __init__(self, conn, table = None):
        self.conn = conn
        self.cursor = conn.cursor()
        self.table = table if table.startswith(config.MYSQL_PRE) else \
                config.MYSQL_PRE + table
        self.commit = False
        self.fields = self.get_table_fields()
        self.logger = get_logger()

    def insert(self, fields, values):
        """ 插入操作,返回id """
        if len(fields) != len(values):
            raise Exception, "fields and values's length not same"
        sql = "INSERT INTO %s" % self.table
        sql += "(`%s`)" % '`,`'.join(fields)
        sv = len(fields) * "%s,"
        sv = sv.strip(',')
        sql += " VALUES(%s)" % sv
        self.commit = True
        self.logger.debug(u'query mysql : {0}'.format(sql % tuple(values)))
        self.cursor.execute(sql, values)

        return self.cursor.lastrowid

    def count(self, where = None):
        """ 统计 """
        sql = 'select count(*) from ' + self.table
        if where:
            sql += ' where ' + where

        self.logger.debug(sql)
        self.cursor.execute(sql)
        r = self.cursor.fetchall()
        return r[0][0] if len(r) == 1 else 0

    def max(self, field):
        sql = 'select max(`{0}`) from ' + self.table
        self.cursor.execute(sql)
        r = self.cursor.fetchall()
        return r[0][0] if len(r) == 1 else 0

    def select_one(self, fields = None, order = None, where = None):
        r = self.select(fields, 1, order, where)
        return r[0] if len(r) == 1 else {}

    def select(self, fields=None, limit = None,
               order = None, where = None):
        """ 查询操作 """
        if not fields:
            fields = self.fields.get_field_list()   # 供后面格式化结果使用
            sf = str(self.fields)                   # 创建sql语句使用
        else:
            sf = '`{0}`'.format('`,`'.join(fields))
        sql = 'select {0} from {1} '.format(sf, self.table)
        if where:
            sql += 'where {0}'.format(where)
        if order and isinstance(order, (dict, tuple)):
            if isinstance(order, dict):
                order = order.items()[0]
            orderby = ' DESC' if order[1] == -1 else 'ESC'
            sql += ' order by {0} {1} '.format(order[0], orderby)
        if limit:
            if isinstance(limit, int):
                sql += ' limit {0} '.format(limit)
            elif isinstance(limit, (tuple, list)):
                sql += ' limit {0}, {1} '.format(*limit)
        self.logger.debug('query mysql : {0}'.format(sql))
        self.cursor.execute(sql)
        tmp = self.cursor.fetchall()
        result = self.get_dict_result(tmp, fields)
        return result

    def update(self, set_dict, where):
        """ 更新操作, 返回id """
        if not isinstance(set_dict, dict) and isinstance(where, dict): return
        sql = 'update {0} set '.format(self.table) + self._format_set(set_dict)
        sql += ' where ' + where
        self.logger.debug('query mysql : {0}'.format(sql))
        self.commit = True
        self.cursor.execute(sql)
        return self.cursor.lastrowid

    def remove(self, where = None):
        """ where 为None则清空表 """
        sql = 'delete from {0}'.format(self.table)
        if where:
            sql += ' where ' + where
        self.commit = True
        self.logger.debug('query mysql : {0}'.format(sql))
        return self.cursor.execute(sql)

    def execute(self, sql, commit = False, *args, **kwargs):
        self.cursor.execute(sql, *args, **kwargs)
        self.commit = commit
        return self.cursor

    def _format_set(self, set_dict):
        result = ''
        for k, v in set_dict.items():
            result += "`{0}`='{1}',".format(k, self.escape(v))
        result = result.rstrip(',')
        return result

    def get_dict_result(self, lst, fields):
        result = []
        for l in lst:
            tmp = dict(((key, l[i]) for i, key in enumerate(fields)))
            result.append(tmp)
        return result

    def get_table(self):
        return self.table

    def get_table_fields(self):
        if self.table:
            self.cursor.execute('describe ' + self.table)
            fields = self.cursor.fetchall()
            return Field(fields)

    def escape(self, value):
        """ 转义MySQL """
        if isinstance(value, (tuple, list)):
            return [self.escape(v) for v in value]
        elif isinstance(value, str):
            return escape_string(value)
        elif isinstance(value, unicode):
            return escape_string(value.encode('utf-8'))
        elif isinstance(value, (int, long, float)):
            return str(value)
        else:
            return value

class MySQLContext:
    def __init__(self, table = None):
        self.conn = mysqldb.Connection(host=config.MYSQL_DB_HOST,
                                    port = config.MYSQL_DB_PORT,
                                    user = config.MYSQL_DB_USER,
                                    passwd = config.MYSQL_DB_PWD,
                                    db = config.MYSQL_DB_NAME,
                                       charset = 'utf8')
        self._table = table
        self._op = DatabaseOp(self.conn, table)

    def __enter__(self):
        return self._op

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._op.commit:
            self.conn.commit()
        self._op.cursor.close()
        self.conn.close()

    @classmethod
    def get_op(cls, table):
        return MySQLContext(table)._op

    def get_cursor(self):
        return self.conn.cursor
