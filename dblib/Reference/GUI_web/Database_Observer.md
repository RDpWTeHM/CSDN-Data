# Database Observer Develop Note



## *Overview*

[TOC]

## Time Line

### 2019/01/12

#### notified format

**Jobbole.com - User Info**

```
Observer_Jobbole_UserInfo: notify> updateDB with:
	 (<sites.jobbole_com.user.index.Subject_Joble_UserInfo object \
	 at 0x7f2759c819b0>, \
	 {'name': '杨泽涛', 'url': 'http://www.jobbole.com/members/wx2336528394', \
	 'follow_num': '0', 'fans_num': '12'}) \
	 {}.

Observer_Jobbole_UserInfo: notify> updateDB with:
	 (<sites.jobbole_com.user.index.Subject_Joble_UserInfo object \
	 at 0x7f2759c81978>, \
	 {'name': '伯小乐', 'url': 'http://www.jobbole.com/members/aoi', \
	 'follow_num': '1', 'fans_num': '49'}) \
	 {}.
```

以字典的形式。字典的键就是定义的 model fileds

> 上面是 commit 726d31771d6c34527fb0be7b0e6fc2b9a66ae7a8 的运行效果。
>
> `$ python -O devl_crawllib.py  -b Chrome`

#### post data to DB API

##### 库？

就是 requests 库即可。requests 库就是 HTTP 请求的封装接口。

post 数据：

(post 用户数据就是 create a new user)

```python
>>> url = "http://localhost:8000/api/sites/1/userids/"
>>> import requests
>>> import json
>>> 
>>> # 就是 notified 的 data
>>> data = { 
    ...:     "article_num": -1, 
    ...:     "visit": -1, 
    ...:     "rank": -1, 
    ...:     "like_num": -1, 
    ...:     "comment_num": -1, 
    ...:     "fan_num": 8, 
    ...:     "follow_num": 4, 
    ...:     "user_id": "N/A", 
    ...:     "name": "N/A", 
    ...:     "regitster_date": "2016-01-12T01:00:00Z", 
    ...:     "signature": "N/A“, 
    ...:     "profession": "N/A", 
    ...:     "location": "北京", 
    ...:     "powered_by": 1 
    ...: }
>>> headers = {'Content-Type': 'application/json', }
>>> r = requests.post(url, headers=headers, data=json.dumps(data))
>>> print(r.text)
```

注意，比如“profession” 要么不发，要么要有值。



##### post to create new user-id

在 `dbobserver.py` 中的 `Observer_Jobbole_UserInfo` class 中的 notify 中的 updateDB 中 post：

```python
from . import jobbole_userid_parse, jobbole_userid_post

class Observer_Jobbole_UserInfo(Observer):
    def __init__(self, user_id):
        self.user_id = user_id

    def notify(self, subject, *args, **kw):
        if subject:
            if __debug__:
                print("{} notify by:\n\t subject -> {}\n\t *args ->{}".format(
                      type(self).__name__, subject, args), file=sys.stderr)
            args = args[1:]
            self.updateDB(*args, **kw)

    def updateDB(self, *args, **kw):
        if __debug__:
            print("\n{}: notify> updateDB with:\n\t {!r} {!r}.".format(
                  type(self).__name__, args, kw),
                  file=sys.stderr)
        try:
            print(jobbole_userid_post(jobbole_userid_parse(args[0])))
        except RuntimeError:
            raise
```

`from . import <any>` 意味着在 `dbobserver.py` 同级目录下创建一个 `__init__.py`，里面来实现想要的 class 或函数。



所以，创建该文件和实现：

```python
"""__init__.py """

import os, sys, json, requests, re, copy

def cover2apiformat(site, datetime_str):
    if "jobbole" in site:
        return True  # -[o]

jobbole_site_pk = 1
django_server_port = 9999

def jobbole_userid_parse(data):
    # fields = ("name", ~~"url"~~, "follow_num", "fan_num",
    #           "user_id", "regitster_date", "signature",
    #           "profession", "location", "powered_by")
    _d = copy.deepcopy(data)

    _url = _d.pop("url")
    _d["user_id"] = re.findall("http://www.jobbole.com/members/(.*)$", _url)[0]
    _d["powered_by"] = jobbole_site_pk
    # _d["regitster_date"] = cover2apiformat(_d.pop("regitster_date"))
    return json.dumps(_d)

def jobbole_userid_post(json_data):
    ''' -[o] hard-code here '''
    #              -[o] develop port \/
    url = "http://localhost:" + str(django_server_port) +\
          "/api/sites/" + str(jobbole_site_pk) + "/userids/"
    #                          /\
    # -[o] jobbole mapping pk not always the same
    headers = {'Content-Type': 'application/json', }
    r = requests.post(url, headers=headers, data=json_data)
    if r.status_code != 201:
        raise RuntimeError(r.text)
    else:
        return r.text

```



#### 测试

```shell
$ python -O devl_crawllib.py  -b Chrome
{"id":12,"article_num":-1,"visit":-1,"rank":-1,"like_num":-1,
"comment_num":-1,"fan_num":0,"follow_num":1,"user_id":"2302901867",
"name":"寒秋暮色恋伊人","regitster_date":"1970-01-01T00:00:00Z",
"signature":"","profession":"","location":"","powered_by":1}
{"id":13,"article_num":-1,"visit":-1,"rank":-1,"like_num":-1,
"comment_num":-1,"fan_num":3,"follow_num":4,"user_id":"%E7%83%9B%E9%BE%99%E4%B8%80%E7%8E%B0",
"name":"烛龙一现","regitster_date":"1970-01-01T00:00:00Z",
"signature":"","profession":"","location":"","powered_by":1}
$ 
```



### 2019/01/13

#### Article 使用 API 入库

##### 当前 data 格式

对应的 commit 和上面的一样。从 selenium 通过 xpath 获取下来的未处理过的原生数据格式：

```shell
ObserverJobboleArticle: notify> updateDB with:
	 ({'article_id': '114168', \
	 'title': '2 年面试 900 多位工程师后，我总结了这些经验', \
	 'pub_date': '2018/08/08 · 职场 · 面试', \
	 'copyright': '本文由 <a href="http://blog.jobbole.com">伯乐在线</a> - \
	               <a href="http://www.jobbole.com/members/dimple11">dimple11</a> 翻译，\
	               <a href="http://www.jobbole.com/members/liuchang">刘唱</a> 校稿。未经许可，禁止转载！\
	               <br>英文出处：<a target="_blank" href=\
	               "http://blog.triplebyte.com/how-to-interview-engineers">Ammon Bartram</a>。欢迎加入\
	               <a target="_blank" href="https://github.com/jobbole/translation-project">翻译组</a>。', \
	 'comment_num': '评论', 'like_num': '1', 'collect_num': '4 收藏'},) {}.
pass
```

上面省略了 "body" : \`innerHTML`

1. pub_date

   `[int(_) for _ in re.findall("^(\d{4})/(\d{2})/(\d{2})", data["pub_date"])[0]]`

   => `[2018, 8, 8]`

2. copyright:

   ```python
   copyright = data.pop("copyright")
   if "翻译" in copyright:
       data["copyright"] = "translation"
   elif "出处" in copyright:
       data["copyright"] = "reprint"
   elif "专栏作者" in copyright:
       data["copyright"] = "originality"
   ```

3. comment, like, collect number:

   ```python
   _tup = ("comment_num", "like_num", "collect_num")
   _td = {}
   for _t in _tup:
       try:
           _td[_t] = int(re.findall("^(\d*)", data[_t])[0])
       except ValueError:
           pass
   ##
   >>> _td
   {'collect_num': 4, 'like_num': 1}
   ```

4. `RuntimeError: {"from_user_id":["Incorrect type. Expected pk value, received str."]}`

   这是个问题！

   ```python
   _d["from_user_id"] = jobbole_userid2pk(user_id)
   or
   _d["from_user_id"] = jobbole_userid2pk("jobbole_reprint")
   
   def jobbole_userid2pk(user_id):
       _url = "http://localhost:" + str(django_server_port) +\
              "/api/jobbole/userids/" + user_id + "/articles/"
       r = requests.get(_url)
       _d = json.loads(r.text)
       pk = _d[0]["from_user_id"]
       return pk
   ```



##### notify

```python
class Subject_Joble_UserArticle(CommonVisitCrawl, SubjectCrawl):
    [...]

    def _monitor(self):
        self._setup_browser(browser_type=self.browser_type)
        self.notifyAll(self, self._parse(), self.user_id)

        self._free_browser()
```



##### parse data and post

parse data 就是将上面的 “当前 data 格式” 的几个solution 用起来

```python
def jobbole_article_parse(data, user_id):
    # fields = ("article_id", ~~"url"~~, "title",
    #           ~~"tag",~~
    #           "pub_date", "copyright",
    #           ~~"body",~~ ~~"res",~~
    #           "comment_num", "like_num", "collect_num",
    #           ~~"reputation_score", "from_user_id",~~ )
    _d = copy.deepcopy(data)
    _d["pub_date"] = '-'.join(
        [_ for _ in re.findall(r"^(\d{4})/(\d{2})/(\d{2})", _d.pop("pub_date"))[0]]
    ) + "T00:00:00Z"

    copyright = _d.pop("copyright")
    if "翻译" in copyright:
        _d["copyright"] = "translation"
        _d["from_user_id"] = jobbole_userid2pk(user_id)
    elif "出处" in copyright:
        _d["copyright"] = "reprint"
        _d["from_user_id"] = jobbole_userid2pk("jobbole_reprint")
    elif "专栏作者" in copyright:
        _d["copyright"] = "originality"
        _d["from_user_id"] = jobbole_userid2pk(user_id)
    else:
        print(copyright, file=sys.stderr)
        _d["copyright"] = "unknow"
        _d["from_user_id"] = jobbole_userid2pk("jobbole")

    for _t in ("comment_num", "like_num", "collect_num"):
        try:
            _d[_t] = int(re.findall(r"^(\d*)", _d[_t])[0])
        except ValueError:
            _d[_t] = 0

    # if __debug__:
    print("{!r}".format(_d), file=sys.stderr)

    return user_id, json.dumps(_d)


def jobbole_article_post(user_id_and_json_data):
    user_id, json_data = user_id_and_json_data
    url = "http://localhost:" + str(django_server_port) +\
          "/api/jobbole/userids/" + user_id + "/articles/"
    return post2(url, json_data)
```









------



## Reference



