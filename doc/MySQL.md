数据库操作指南
===============
# 介绍
数据库操作被放在`core.db.MySQLContext`中,建议使用with语法调用数据库,并传入当前表名
```python
from core.db import MySQLContext

with MySQLContext("table") as op:
    op.select(where = where)
```

使用with语法调用将会获得一个数据库操作实例
所有需要where参数的方法函数,所需要的只是where的条件部分("`id`='1' and `cid`='2'")

# 数据库操作实例方法函数
## 初始化
### 参数
* conn     数据库连接
* table    数据库名称 (可选)

## insert
插入数据到MySQL数据库

### 参数
* fields      插入的列名   list or tuple
* values      对应的值  list or tuple
` 传入的参数会自行编码,防止注入 `

### 返回
long 插入数据的id

## count
统计条数

### 参数
* where      条件(可选)   str

### 返回
long

## max
返回某列的最大值

### 参数
* field        列名  str

### 返回
long

## select_one
查询单条

### 参数
* fields     指定返回列数(可选) list  如不传则返回全部列
* order      执行排序(可选)  dict ({"id":-1} 按id倒序)
* where      条件(可选)      str

### 返回
dict
{列名:值,...}

## select
查询

### 参数
* fields     (同select_one)
* order      (同上)
* where      (同上)
* limit       限定查询的条数  tuple(skip, limit) or int (limit)

### 返回
[{列名:值,...},...]

## update
更新数据库

### 参数
* set_dict       设置的字典  dict ({列名:新值,...})
* where          条件   str

### 返回
影响的条数


## remove
删除条目

### 参数
* where        条件(可选) str 不传则清空表

## escape
转义字符串

### 参数
* value        要被转义的值  str | list | tuple | unicode | int| long| float

### 返回
str | list | unicode
