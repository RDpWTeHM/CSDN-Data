# Develop Note

## *Overview*

[TOC]

## simple code subject/observer demo

```powershell
#### test result:
>
>python crawl.py
Chrome run get url:
         http://www.jobbole.com/members/wx2336528394/
Chrome run find element by xpath:
         //div[@class='member-profile box']//span[@class='profile-title']//a
Chrome run .text
Chrome run find element by xpath:
         //div[@class='member-profile box']//span[@class='profile-title']//a
Chrome run .get_attribute():
         args > ('href',) kw > {}
Chrome run find element by xpath:
         //div[@class='profile-follow']/a
Chrome run .text
Chrome run find element by xpath:
         //div[@class='profile-follow'][2]/a
Chrome run .text
Observer_Jobbole_UserInfo notify by:
         subject -> <__main__.Subject_Joble_UserInfo object at 0x000001B297AE6400>
         *args ->(<__main__.Subject_Joble_UserInfo object at 0x000001B297AE6400>, ['name: Chrome._text', "url: Chrome.get_attribute(('href',), {})", 'follow_num: Chrome._text', 'fans_num: Chrome._text'])

Observer_Jobbole_UserInfo: notify> updateDB with:
         (<__main__.Subject_Joble_UserInfo object at 0x000001B297AE6400>, ['name: Chrome._text', "url: Chrome.get_attribute(('href',), {})", 'follow_num: Chrome._text', 'fans_num: Chrome._text']) {}.

>
>
>python -O crawl.py --browser Edge
Observer_Jobbole_UserInfo notify by:
         subject -> <__main__.Subject_Joble_UserInfo object at 0x00000289997B6198>
         *args ->(<__main__.Subject_Joble_UserInfo object at 0x00000289997B6198>, ['name: 杨泽涛', 'url: http://www.jobbole.com/members/wx2336528394', 'follow_num: 0', 'fans_num: 12'])

Observer_Jobbole_UserInfo: notify> updateDB with:
         (<__main__.Subject_Joble_UserInfo object at 0x00000289997B6198>, ['name: 杨泽涛', 'url: http://www.jobbole.com/members/wx2336528394', 'follow_num: 0', 'fans_num: 12']) {}.

>
```

:point_up_2: those work on `commit 722886c650f38ab881d58dc4e2c900c1cfbb0cfe`



