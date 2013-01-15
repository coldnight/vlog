#介绍
vLog 是一个轻量级的日志/博客系统,使用Markdown格式书写博文,使用tornado和MySQL驱动,之所以叫vLog是因为一开始打算只写接口使用Vim调用即可,因为我非常不喜欢写WEB页面,现在只提供了最基本的功能,写文章....,后台其余的都没写,因为我非常不喜欢写WEB页面2,所以现在实现了基本功能,其余的以后会慢慢加上, 模板使用octopress原因你也肯定懂

## 缓存
采用按照uri缓存,遇到post方法时则清除所有缓存

## 目录结构
```
|- core          // 核心代码,包括Handler基类,Logic基类,缓存和数据库操作杂类工具
|- doc           // 文档目录
|- utest         // 单元测试
|- web           // 主要代码
|   |- static    // 静态文件目录
|   |- template  // 模板目录
|   |- handler   // 业务请求
|   |- logic     // 业务逻辑
|- run.py        // 启动脚本
|- config.py     // 配置文件
|- mycnf.py      // 安装生成的数据库配置文件

```

#安装
##平台
* Linux
* python2.7
* MySQL
* Memcached 1.4.5


## 依赖包
* tornado
* jinja2
* MySQLdb
* pylibmc

## 开始安装
首先确认config.py的DEBUG是打开的,然后执行run.py,打开浏览器输入当前地址,会跳转到安装页面.按照提示安装,安装完毕后可以关闭DEBUG

#结合nginx
参阅[tornado文档](http://www.tornadoweb.cn/documentation#_14)


#从Wordpress中导入
## 从Wordpress导出
在wordpress管理后台选择工具->导出,下载导出文件可以导出一份xml

## 移动媒体文件
将/path/to/your/wordpress/wp-content/uploads/下的所有文件移动到/path/to/your/vlog/web/static/upload 下即可

务必要先执行这一步然后再在后台里导入xml

## 导入到vLog
进入vLog后台,选择导入,浏览选中导出的xml, 然后选择开始,等待提示成功后即导入成功

## 手动更改没有生效的链接
虽然我已经竭尽所能的让你手头的工作更少,但是还不够,还是存在许多需要手动更改的地方,
比如每篇文章的没有替换掉的图片链接

# 参与开发
请参阅[开发指南](/coldnight/vlog/blob/master/doc/DevDoc.md), [业务逻辑编写指南](/coldnight/vlog/blob/master/doc/Logic.md), [数据库操作指南](/coldnight/vlog/blob/master/doc/MySQL.md), [业务请求开发指南](/coldnight/vlog/blob/master/doc/Handler.md), [主题开发指南](/coldnight/vlog/blob/master/doc/Theme.md)
