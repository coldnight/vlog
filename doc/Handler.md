业务请求开发指南
================
# 介绍
所有业务请求代码放置在web/handler 目录

# 实现
所有业务请求必须继承 core.web.BaseHandler, 并实现 get/post方法

# 加载
默认的 构成 业务请求的url是 /文件名替换掉index/类名去掉handler替换掉index,
也就是说下面代码构成 / 路径的业务请求
```python
# Filename : index.py
from core.web import BaseHandler
class IndexHandler(BaseHandler)
    def get(self):
        self.write("Hello, world")
```

也可显示指定当前业务请求的路径, 只需指定当前类的_url类属性, 下面的代码构成了一个到 /post/ 路径的业务请求
```python
# Filename : index.py

class TestHandler(BaseHandler):
    _url = r"/post/"
    def get(self):
        self.write("This is a post url")
```
