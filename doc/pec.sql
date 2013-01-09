-- database: pec;
create database if not exists pec;
use pec;
-- table:code
create table if not exists code(
    id INT AUTO_INCREMENT NOT NULL,
    poster VARCHAR(255) NULL,
    class VARCHAR(100) NULL,
    code   TEXT NOT NULL,
    date TIMESTAMP NULL,
    PRIMARY KEY(id)
)character set utf8;


create table if not exists user(
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

create table if not exists options(
    id INT AUTO_INCREMENT NOT NULL,
    `key` VARCHAR(255) NOT NULL,
    `value` TEXT NULL,
    `owner` VARCHAR(255) NOT NULL default 'global',
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    INDEX(`key`)
    )character set utf8;

create table if not exists post(
    id INT AUTO_INCREMENT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source TEXT NULL,
    author INT NOT NULL,
    tags INT NOT NULL,
    `md5` VARCHAR(32) NOT NULL,
    isdraft INT NOT NULL default 1,
    allowcomment INT NOT NULL DEFAULT 1,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    INDEX(`title`)
    )character set utf8;

create table if not exists post_to_tag(
    id INT AUTO_INCREMENT NOT NULL,
    pid INT NOT NULL,
    tid INT NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`pid`)
    )character set utf8;


create table if not exists tag(
    id INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`name`)
)character set utf8;


create table if not exists post_to_category(
    id INT AUTO_INCREMENT NOT NULL,
    pid INT NOT NULL,
    cid INT NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`pid`)
    )character set utf8;

create table if not exists category(
    id INT AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`name`)
    )character set utf8;

create table if not exists `comment` (
    id INT AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `email` VARCHAR(50) NOT NULL,
    `url` VARCHAR(50) NOT NULL,
    `content` VARCHAR(50) NOT NULL,
    `parent` INT NOT NULL default 0,
    `pid` INT NOT NULL default 0,
    allowed INT NOT NULL default 0,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(`id`),
    INDEX(`pid`)
)character set utf8;


