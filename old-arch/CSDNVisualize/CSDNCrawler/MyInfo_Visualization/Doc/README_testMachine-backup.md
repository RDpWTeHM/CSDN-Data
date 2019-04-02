# README

  将 CSDN 上的个人主页的数据可视化（先获数据）。

  积分，文章数量，阅读，排名，...等；做成折线，特别是文章发表和 阅读、排名、积分之间的关系。



***Overview***

[TOC]

## Contents

  N/A



## Sammary

**Usage**

```shell
$ mkvirtualenv CSDN
Using base prefix '/usr'
...
(CSDN) $ pip install BeautifulSoup4 \
-i https://pypi.tuna.tsinghua.edu.cn/simple/
(CSDN) $ pip install requests \
-i https://pypi.tuna.tsinghua.edu.cn/simple/
(CSDN) $ 
(CSDN) $ python main.py
user ID: qq_29757283
粉丝：2
点赞：3
评论：1
访问量：8091
积分：261
排名：30万+
(CSDN) $ deactivate
$ 
```



## ToDo

- [ ] N/A


## Note

### packages depends

> BeautifulSoup4; requests
>
>

n/a

## Change Log

### Aug/26/2018

***23:23*** - 添加了 personalProfile.py 文件

  将 main.py 中的 PersonCSDN CLASS 移动到了 personalProfile.py 文件中。

  重写了 PersonCSDN class 的 `__str__(self)` 方法。 print (object) 默认调用 str() 来输出类。

**Usage:**

```
(CSDN) $ python main.py
user ID: qq_29757283
粉丝：2
点赞：3
评论：1
访问量：8088
积分：261
排名：30万+
(CSDN) $ 
```



***17:51*** - main.py 完成了 PersonCSDN CLASS 中的 关键信息提取！

  用户ID 由用户指定

获得到：（all string） 

  文章数量， 粉丝数量， 点赞数量， 评论数量；

  总访问量， 积分， 排名；



***15:26*** - main.py 添加 PersonCSDN CLASS

  `class PersonCSDN(): ...` 用于保存 User 的 CSDN 数据！

  包括： 用户ID， 主页 HTML Data, 所有文章（list）, 粉丝数量， 点赞数量， 评论数量， 总访问量， CSDN 积分， CSDN 排名； 等。

  依赖 BeautifulSoup4 来解析主页 HTML 内容。

  当前， 主要的 User Profile 的关心数据已经能够提取到 userDataInfo， userGradeBox 两个变量中去。这两个变量都是 bs4 的 tag 类型！还需要进一步提取数据！



***11:45*** - 添加了 main.py

  main.py 获取 CSDN 自己的个人主页。 CSDN id: qq_29757283

个人主页： https://blog.csdn.net/qq_29757283

获取到的 HTML 代码内容确实是该页面的内容， 暂时没有什么问题。