#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 18:39:18
#   Desc    :   链接逻辑
#
from core.logic import Logic

#TODO
class Links(Logic):
    def get_all_links(self, limit = LINK_NUM):
        sdb._ensure_connected()
        return sdb.query('SELECT * FROM `sp_links` ORDER BY `displayorder` DESC LIMIT %s' % str(limit))

    def add_new_link(self, params):
        query = "INSERT INTO `sp_links` (`displayorder`,`name`,`url`) values(%s,%s,%s)"
        mdb._ensure_connected()
        return mdb.execute(query, params['displayorder'], params['name'], params['url'])

    def update_link_edit(self, params):
        query = "UPDATE `sp_links` SET `displayorder` = %s, `name` = %s, `url` = %s WHERE `id` = %s LIMIT 1"
        mdb._ensure_connected()
        mdb.execute(query, params['displayorder'], params['name'], params['url'], params['id'])

    def del_link_by_id(self, id):
        mdb._ensure_connected()
        mdb.execute("DELETE FROM `sp_links` WHERE `id` = %s LIMIT 1", id)

    def get_link_by_id(self, id):
        sdb._ensure_connected()
        return sdb.get('SELECT * FROM `sp_links` WHERE `id` = %s LIMIT 1' % str(id))


