#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/01/05 18:12:35
#   Desc    :   安装逻辑
#
import os
import MySQLdb as mysqldb
from config import ROOT_PATH
sql = """
drop database if exists `{0}`;
create database if not exists `{0}`;
use `{0}`;
drop table if exists `{1}code`;
create table if not exists `{1}code`(
    id INT AUTO_INCREMENT NOT NULL,
    poster VARCHAR(255) NULL,
    class VARCHAR(100) NULL,
    code   TEXT NOT NULL,
    date TIMESTAMP NULL,
    PRIMARY KEY(id)
)character set utf8;


drop table if exists `{1}user`;
create table if not exists `{1}user`(
    id INT AUTO_INCREMENT NOT NULL,
    username VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    `key` VARCHAR(32) NULL,
    url VARCHAR(100) NULL,
    role INT NOT NULL DEFAULT 0,  -- 0 管理员
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(id)
)character set utf8;

drop table if exists `{1}options`;
create table if not exists `{1}options`(
    id INT AUTO_INCREMENT NOT NULL,
    `key` VARCHAR(255) NOT NULL,
    `value` TEXT NULL,
    `owner` VARCHAR(255) NOT NULL default 'global',
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    INDEX(`key`)
    )character set utf8;

drop table if exists `{1}post`;
create table if not exists `{1}post`(
    id INT AUTO_INCREMENT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source TEXT NULL,
    author INT NOT NULL,
    `md5` VARCHAR(32) NULL,
    isdraft INT NOT NULL default 1,
    allowcomment INT NOT NULL DEFAULT 1,
    date TIMESTAMP NOT NULL,
    `update` TIMESTAMP NULL,
    enabled TINYINT(1) NOT NULL DEFAULT 1,
    `type` TINYINT(1) NOT NULL DEFAULT 1,  -- 1:post 2:page
    PRIMARY KEY(id),
    INDEX(`title`)
    )character set utf8;

drop table if exists `{1}post_to_tag`;
create table if not exists `{1}post_to_tag`(
    id INT AUTO_INCREMENT NOT NULL,
    pid INT NOT NULL,
    tid INT NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`pid`)
    )character set utf8;


drop table if exists `{1}tag`;
create table if not exists `{1}tag`(
    id INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`name`)
)character set utf8;


drop table if exists `{1}post_to_category`;
create table if not exists `{1}post_to_category`(
    id INT AUTO_INCREMENT NOT NULL,
    pid INT NOT NULL,
    cid INT NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`pid`)
    )character set utf8;

drop table if exists `{1}category`;
create table if not exists `{1}category`(
    id INT AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`name`)
    )character set utf8;

drop table if exists `{1}comment`;
create table if not exists `{1}comment` (
    id INT AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `url` VARCHAR(100) NULL,
    `content` VARCHAR(50) NOT NULL,
    `parent` INT NOT NULL default 0,
    `pid` INT NOT NULL default 0,
    `ip` VARCHAR(128) NULL,
    allowed INT NOT NULL default 0,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`pid`)
)character set utf8;
"""

def install(mysql_host, mysql_port, mysql_user, mysql_pwd,
            mysql_name, mysql_prev):
    global sql
    try:
        conn = mysqldb.Connection(host = mysql_host, port = int(mysql_port),
                                  user = mysql_user, passwd = mysql_pwd)
        sql = sql.format(mysql_name, mysql_prev)
        cursor = conn.cursor()
        for s in sql.split(';'):
            if not s.strip(): continue
            cursor.execute(s + ';')
            conn.commit()
        mysql_cnf_path = os.path.join(ROOT_PATH, 'mycnf.py')
        mycnf = open(mysql_cnf_path, 'w')
        content = "MYSQL_DB_HOST = '{0}'\nMYSQL_DB_PORT = {1}\n"\
                "MYSQL_DB_USER = '{2}'\nMYSQL_DB_PWD='{3}'\n"\
                "MYSQL_DB_NAME= '{4}'\n"\
                "MYSQL_PRE = '{5}'".format(mysql_host, mysql_port, mysql_user,
                                         mysql_pwd, mysql_name,  mysql_prev)
        mycnf.write(content)
        mycnf.close()
        cursor.close()
        conn.close()
        return {"status":True}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status":False, "errmsg":str(e)}
