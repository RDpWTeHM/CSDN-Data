"""
filename    : PersonalData_v0.0.4/utils.py
Author      : Joseph Lin
Email       : joseph.lin@aliyun.com
Date        : 2018/Nov/03
Last Change : 2018/Nov/03

TODO:
 -[o] import error warn
 -[o] 重构或使用其它方式使用 getSubTagfrom() function
"""

import sys, os
import re
import time
# from bs4 import BeautifulSoup
'''-[o] import error alert
因为大概率使用“虚拟环境”的原因，
所以在没有使用虚拟环境的情况下， 需要提醒！
（就像 django 的 manage.py 那样！）

Q: getSubTagfrom() 内部是使用 BeautifulSoup 的 tag object,
    没有 import BeautifulSoup 在外部调用这个function 能用？
A: 能用！ -- 结论是这样，具体一些的原理，有待了解。
'''


# 使用同级路径下的 phantojs/bin/ 文件夹下的 phantojs 应用程序作为默认
DEFAULT_BROWSER_PATH = './phantomjs/bin/'

if sys.platform == 'win32':
    DEFAULT_BROWSER_NAME = 'phantomjs.exe'
elif sys.platform == 'linux':
    DEFAULT_BROWSER_NAME = 'phantomjs'
elif sys.platform == 'cygwin':
    DEFAULT_BROWSER_NAME = 'phantomjs.exe'


def getSubTagfrom(tag, htmlId=None, htmlTag=None, htmlClass=None):
    subTag = None
    if htmlClass is not None:
        list_ = tag.findAll(htmlClass[0], {'class': htmlClass[1]})
        return list_[0]
    for content in tag.contents:
        """ -[o] 用 流畅的python 中的‘单分派泛函数’ 重构本段代码"""
        if htmlId is not None:
            key = htmlId
            '''因为 htmlclass 是后增加的，本段代码有点儿遗忘，
            所以把逻辑和之前的保持一致！'''
            if str(content).find(key) != -1:
                subTag = content
                break
        elif htmlTag is not None:
            key = htmlTag
            '''因为 htmlclass 是后增加的，本段代码有点儿遗忘，
            所以把逻辑和之前的保持一致！'''
            if str(content).find(key) != -1:
                subTag = content
                break
        else:
            break
    return subTag


def cover_WANG_to_integet(_str):
    highOrder = re.sub("\D", "", _str)
    if "万" in _str:
        return int(highOrder) * 10000 + 9999
    else:
        return int(highOrder)


from socket import *
import pickle


def negotiateIPCInfo():
    serverHost = 'localhost'
    serverPort = 50007
    msg = ['OK, give me the port number']

    sockObj = socket(AF_INET, SOCK_STREAM)
    sockObj.connect((serverHost, serverPort), )
    # sockObj.send(pickle.dump(msg[0]))
    sockObj.send(msg[0].encode())
    data = sockObj.recv(1024)
    data = pickle.loads(data)
    if __debug__:
        print('[Debug]: negotiateIPCInfo> Client received: ', data, file=sys.stderr)
    sockObj.close()

    return data


from multiprocessing.connection import Client


def getPageSourceOf(whichPage, _IPCData):
    MAX_RETRY_TIMES = 4
    for failTimes in range(MAX_RETRY_TIMES):  # 尝试三次链接 IPC。
        try:
            c = Client(('localhost', _IPCData['port']), authkey=b'CSDN-Data')
        except ConnectionRefusedError as e:
            print("[Info] ConnectionRefusedError: ", e)
            if failTimes == MAX_RETRY_TIMES - 1:  # 第 MAX_RETRY_TIMES 次链接失败
                import traceback; traceback.print_exc()
            time.sleep(1 * (failTimes + 1))
        else:
            break
    recv_result = False
    if whichPage == 'HomePage':
        counter = 0
        while True:
            _recv = c.recv()  # <--- this will block
            if not _recv:     # timeout not work.
                counter += 1
                if counter > 60:
                    print("getHomePageHTMLText> connection timeout",
                          file=sys.stderr)
                    c.close()
                    sys.exit(1)
                sleep(0.1)
            else:
                if recv_result is False:
                    if _recv == 'SYNC':
                        c.send('SYNC')
                    elif _recv == 'Req: whichPage':
                        c.send('HomePage')
                    elif _recv == 'Req: req_url':
                        c.send(_IPCData['req_url'])
                    elif _recv == 'Rsp: pagesource':
                        c.send("Ready")
                        recv_result = True
                else:
                    _pagesource = _recv
                    c.close()
                    return _pagesource
    elif whichPage == 'BlogPage':
        counter = 0
        while True:
            _recv = c.recv()  # <--- this will block
            if not _recv:     # timeout not work.
                counter += 1
                if counter > 60:
                    print("getBlogPageHTMLText> connection timeout",
                          file=sys.stderr)
                    c.close()
                    sys.exit(1)
                sleep(0.1)
            else:
                if recv_result is False:
                    if _recv == 'SYNC':
                        c.send('SYNC')
                    elif _recv == 'Req: whichPage':
                        c.send('BlogPage')
                    elif _recv == 'Req: req_url':
                        c.send(_IPCData['req_url'])
                    elif _recv == 'Rsp: pagesource':
                        c.send("Ready")
                        recv_result = True
                else:
                    _pagesource = _recv
                    c.close()
                    return _pagesource


def getPageSourcesOf(whichPages, _IPCData):
    MAX_RETRY_TIMES = 4
    for failTimes in range(MAX_RETRY_TIMES):  # 尝试 MAX_RETRY_TIMES 次链接 IPC。
        try:
            c = Client(('localhost', _IPCData['port']), authkey=b'CSDN-Data')
        except ConnectionRefusedError as e:
            print("[Info] ConnectionRefusedError: ", e)
            if failTimes == MAX_RETRY_TIMES - 1:  # 第 MAX_RETRY_TIMES 次链接失败
                import traceback; traceback.print_exc()
            time.sleep(1 * (failTimes + 1))
        else:
            break
    recv_result = False
    if whichPages == 'ArticlesPages':
        while True:
            _recv = c.recv()
            if recv_result is False:
                if _recv == 'SYNC':
                    c.send('SYNC')
                elif _recv == 'Req: whichPage':
                    c.send('ArticlesPages')
                elif _recv == 'Req: req_url':
                    c.send(_IPCData['req_url'])
                elif _recv == 'Rsp: pagesource':
                    c.send('Ready')
                    recv_result = True
            else:
                _pagesources = _recv
                c.close()
                return _pagesources
    else:
        return None  # raise myself define unknow type?
