业务逻辑编写指南
================
# 介绍
业务逻辑顾名思义就是网站的逻辑,主要存放在web/logic/目录下

# 实现
所有涉及数据库操作的业务逻辑必须继承`core.logic.Logic`基类,默认的会将当前去除Logic结尾后的类名作为当前表名,
如需指定只需覆盖_t属性使用_t属性显示的指定表名,`Logic`基类封装了生成pageinfo和limit的类,和输出成功(success),
输出错误(error)的方法函数, 不需要数据库操作的逻辑不应继承`Logic`基类

## 初始化
需要覆盖init方法函数完成初始化

## 操作数据库
只需使用with语句调用 基类的_mc方法,获得一个数据库操作
下面例子将演示如何操作数据库和初始化
```python
from core.logic import Logic

class DemoLogic(Logic):
    """ 将默认操作 demo数据库 """
    def init(self):
        """ 初始化 """
        pass

    def demo_select(self):
        with self._mc() as op:
            where = "`id`='{0}'".format(op.escape('1'))
            return op.select(where = where)
```
更多数据操作参见[数据库操作指南](./MySQL.md)

## 建议
所有不依赖业务请求的逻辑都应在web.logic.Logic(web/loigc/__init__中的Logic类)中的类属性进行初始化

业务请求只需引入web.logic.Logic即可对整个业务逻辑进行操作

# 基类主要方法函数
## handle_page
生成分页信息
### 参数
* total 总条目           int 
* index 当前页面索引值   int
* size 每页显示条数      int

### 返回
dict
{
    totalpage: // 总页面
    pageindex: // 当前页面索引
    prevpage : // 前一页索引
    nextpage : // 后一页索引
    pagesize : // 每页显示条数
}

## handle_limit
生成MySQLlimit信息

### 参数
* index  当前索引             int
* size   每页显示条数(可省略) int

### 返回
tuple (skip, limit)

## success

### 参数
* data    返回的数据
* pageinfo  分页信息(可省略)    dict

## 返回
dict
{
    status : True  // 表示成功
    data : data    // 返回数据
    pageinfo : pageinfo // 分页信息(如果参数传的话)
}
