主题开发指南
=============
# 介绍
模板引擎使用 jinja2 ,所以主题模板语言应该使用与之想对应的模板语言,
主题必须包含3个文件,分别是 索引页面(index.jinja),详情页面 (page.jinja)和错误页面(error.jinja)

# 主要模板变量
## 全局模板变量
* title   标题
* SITE_TITLE  站点标题
* SITE_SUB_TITLE 站点副标题
* description     描述
* keywords        关键字
* page            所有页面
* request         Tornado ReuqestHandler的 request 成员属性
* comments        最新的评论
* new             最新的文章
* categories      所有分类
* tags            所有标签
* months          所有文章归档月份
* links           所有链接
* uid             当前用户uid, 没登录则为None
* username        当前用户用户名, 没则为None

### page
```
[{
    id
    title
}, ...]
```

### comments
```
[{
    date
    pid           // 对应的文章id
    name          // 作者
    content
    short_content
}...]
```

### new
```
[{
    id
    title
},...]
```

### categories
```
[{
    id
    name
    post_num
}, ...]
```

### tags
```
[{
    id
    name
    post_num
}, ...]
```

### months
```
[{
    year
    month
}, ...]
```

### links
```
[{
    url
    text
}, ...]
```


## 索引页面变量
* posts           当前页面文章
* pageinfo        分页信息

### posts
```
[{
    id
    title
    short_content
    content
    category : [{
        id
        name
    },...]
    author: { name, id }
    tag : [{ name, id }, ...],
    comment_num
},...]
```

### pageinfo
```
{
    totalpage: // 总页面
    pageindex: // 当前页面索引
    prevpage : // 前一页索引
    nextpage : // 后一页索引
    pagesize : // 每页显示条数
}
```

## 详情页变量
* post            文章
* post_comments   文章评论
* pageinfo        评论分页信息
* ispage          是否是页面, 否则为文章

### post
```
{
    id
    title
    short_content
    content
    category : [{
        id
        name
    },...]
    author: { name, id }
    tag : [{ name, id }, ...],
    comment_num
}
```

### post_comments
```
[{
    gravatar          // 经过md5加密的email
    name              // 评论人
    url               // 评论url
    allowed           // 是否通过
}, ...]
```

### 错误页面变量
* status_code  错误代码
* info         错误信息

# 主要接口
## 添加评论
### url
/post/(pid)

### 方法
POST

### 参数
```
name
email
url
content
parent
```

## 编辑文章
### url
/admin/editpost/(pid)

### 方法
GET

## 编辑页面
### url
/admin/editpage/(pid)

### 方法
GET

## 允许评论通过
### url
/admin/allow/comment/(pid)/(cid)/(page|post)

### 方法
GET

## 删除评论
### url
/admin/del/comment/(post|page)/(cid)

### 方法
GET
