#!/usr/bin/env python3

"""
# filename: loopCSDNCrawlerArticles.py
# function: --

NOTE:
  1. 需要确认 shelve db 文件中对应的 ODM 值不会在 line 45 出问题！
  2. handle result 在 key 不存在的情况会有 bug！

TODO:
  -[o] thread lock shelve db not be test yet.
  -[x] 精确地处理 django server 没有启动的异常。
"""


import sys
import os
# import time
from time import sleep
import logging
from time import ctime
# from selenium import webdriver
# from collections import OrderedDict
# from bs4 import BeautifulSoup
import requests
# from random import randint
import shelve
import queue
import threading

import signal

import traceback
from requests.exceptions import ConnectionError

# sys.path.append(os.getcwd())
import conf.client_active_daemon
CONF = conf.client_active_daemon.conf


Qid_in = queue.Queue()
Qid_done = queue.Queue()
Qid_err = queue.Queue()

try:
    dbfp = shelve.open(CONF.SHELVE_DB_PATH + "/" + CONF.ALL_USER_FILE)

    all_user_ids = dbfp['ALL_USER_IDs']
    dbfp.close()
    # all_user_ids.reverse()
    _number = 400
    for i in range(_number):
        Qid_in.put(("active", all_user_ids[i]))
except IOError as e:
    print("open ALL_USER_IDs IOError:", e, file=sys.stderr)
    sys.exit(1)
finally:
    del dbfp, all_user_ids, _number, i


def sigint_handler(signo, frame):
    '''that thread finish its jos,
      then, do stop
      -[o] 因为 Qid_id 在上面是所有 ID 都放好的。
      所以这段代码暂时没用
    '''
    for i in range(CONF.THREAD_NUM):
        Qid_in.put(("stop", None))


def timeoutsleep():
    '''
      Usage:
          tosleep = timeoutsleep()
          try: ...
          except **Timeout:
             tosleep(True)
          else:
             tosleep(False)
             ...
    '''
    _totimes = 0

    def runningsleep(IsTimeout):
        nonlocal _totimes  # fluent python - & 7.6 nonlocal
        if IsTimeout is False:
            _totimes = 0
        elif IsTimeout is True:
            _totimes += 1
            sleep(_totimes * 5)
        else:
            raise Exception("<timeoutsleep> Error parameter gived!")
    return runningsleep


class Work(object):
    '''==============================
              multi Thread part
    '''
    global CONF, Qid_in, Qid_done, Qid_err
    (loopArticles_base_url, ) = (CONF.DJANGO_SERVER +
                                 '/' + CONF.DJANGO_ARTICLES_URL +
                                 "/?user_id=", )
    _totimes = 0

    def runningsleep(self, IsNoServer):
        if IsNoServer is False:
            self._totimes = 0
        elif IsNoServer is True:
            self._totimes += 1
            sleep(self._totimes * CONF.NOSERVER_BASEWAITE)
        else:
            raise Exception("<timeoutsleep> Error parameter gived!")

    def request_work(self, data, command):
        Qid_in.put((command, data))

    def do_work_from_queue(self):
        while True:
            try:
                '''本程序下的 Queue 卡住的情况基本上可以认为全部任务已经完成。 '''
                command, data = Qid_in.get(timeout=10)  # 有无 timeout 决定了是否持续运行！

                # getattr(self, 'do_'+command)(data)
                if command == 'stop':
                    self._quit()
                    break  # 退出 while True，线程退出。
                elif command == 'active':
                    result = self.run(data)
                else:
                    logging.warning(
                        "Thread: receive not support work type ->" +
                        "{} with data: {}".format(command, data))
            except queue.Empty:
                ''' 本 except 是 try: 本程序... 这段任务完成“说明”的实际实现 '''
                logging.info("queue.Empty! request thread(s) quit!")
                self.request_work(None, 'stop')
            except Exception as e:
                logging.debug("Thread: <{}@{}> unknow condition: {}".format(
                    command, data, e))
                Qid_err.put((command, data, "Exception: {}".format(e)))
            else:
                Qid_done.put((command, data, result))

    def _quit(self):
        ''' 指示“本”线程退出
          要知道，程序中可能存在其它部分是和本 work 线程相关的地方。
          比如，目前的 handler result 用于更新 shelve DB，
                所以它就等待“所有”的 work 线程退出，这意味着没有 user id 需要更新到 shelve DB 中，
                于是 handler result 的线程最后可以退出。
                这就说明，本线程在退出之前需要“告诉” handler result 的线程。
          所以调用本函数并非是真正地退出本 work 线程。
          而是在要退出本 work 线程之前必要做的工作。
        '''
        logging.debug("run stop to quit thread")
        Qid_done.put((None, None, None))  # 使 handler result 线程退出。

    def run(self, _data):
        handler_userid = _data
        loopArticles_url = "{}{}".format(
            self.loopArticles_base_url, handler_userid)
        logging.info("Thread: request crawler articles of" +
                     "\"{}\"".format(handler_userid))

        try:
            r = requests.get(loopArticles_url)
        except ConnectionError as e_conn:
            logging.error("requests.get(url) ConnectionError: %s" % (e_conn))
            self.runningsleep(True)
        except Exception as e:
            traceback.print_exc()
            logging.error("requests.get(url) unknow Exception: %s" % (e))
            self.runningsleep(True)
        else:
            self.runningsleep(False)
        if r.status_code != 200:
            raise Exception("r.status_code != 200")
        result = r.text

        # 没有什么需要做的了，工作在 django 的 views.<func> 中完成。
        logging.info("Thread: loop articles of" +
                     "'{}' =result=> {}".format(handler_userid, result))
        return result


def handler_result():
    counter_for_exit = 0
    while True:
        if False:
            try:
                command, data, result = Qid_done.get(timeout=1)
                if command == 'active':
                    updateShelve(data, result)
                elif command is None:
                    logging.debug("handler_result(): command is None")
                    counter_for_exit += 1
                    if counter_for_exit == CONF.THREAD_NUM:
                        break  # thread quit
            except queue.Empty:
                break
        else:
            command, data, result = Qid_done.get()
            if command == 'active':
                updateShelve(data, result)
            elif command is None:
                logging.debug("handler_result(): command is None")
                counter_for_exit += 1
                if counter_for_exit == CONF.THREAD_NUM:
                    break  # thread quit


# shelve_db_lock = threading.Lock()


def updateShelve(data, result):
    '''更新 shelve all user id 数据库
      shelve all user ids 是 sqlite3 中已有的所有 user ids,
      然后爬取所有 sqlite3 中有的 user ids 的 articles。
      1. 该 user id 的 articls 还未爬取过，爬取成功，将该 id 移动到 key 为 DONE_IDs
      2. 爬取该 user id 的 articles 超时，
        （可能是因为该 id 没有 articles）将该 id 移动到 key 为 TIMEOUT_IDs
      3. 请求爬取该 user id, 但是 django server 回复该 user id 的 articles 已经爬取过了，同 1. 移动。
      因为 1, 3 的 shelve DB key 相同，但是时间有所不同，简单加上 "[ctime] =/-" 指示。
    '''
    short_result = ''
    # with shelve_db_lock:  # not work well for now.
    if True:
        try:
            # read data from shelve DB
            dbfp = shelve.open(CONF.SHELVE_DB_PATH + "/" + CONF.ALL_USER_FILE)
            all_user_ids = dbfp['ALL_USER_IDs']
            timeout_ids = dbfp['TIMEOUT_IDs']
            done_ids = dbfp['DONE_IDs']

            if 'OK' in result:
                short_result = 'OK'
                all_user_ids.remove(data)
                done_ids[data] = "{} =".format(ctime())
            elif 'timeout' in result.lower():
                short_result = "timeout"
                all_user_ids.remove(data)
                timeout_ids.append(data)
            elif "Already Exists".lower() in result.lower():
                short_result = "already exists"
                all_user_ids.remove(data)
                done_ids[data] = "{} -".format(ctime())
            elif "CrawlerError".lower() in result.lower():
                short_result = "crawler error"
                all_user_ids.remove(data)
                timeout_ids.append(data)
            else:  # unknow condition - do not update DB
                Qid_err(("updateShelve()", data,
                         "unknow result: {}".format(result)))

            # save data to shelve DB
            dbfp['TIMEOUT_IDs'] = timeout_ids
            dbfp['ALL_USER_IDs'] = all_user_ids
            dbfp['DONE_IDs'] = done_ids
            dbfp.close()
        except IOError as e:
            logging.debug("open ALL_USER_IDs IOError: %s" % e)
            Qid_err.put(("Update Shelve DB", data, "IOError: {}".format(e)))
        except Exception as e:
            logging.debug("<None@updateShelve()> unknow condition: %s" % (e))
            Qid_err.put(("Update Shelve DB", "<{}@{}>".format(data, result),
                         "Exception: {}".format(e)))
        else:
            logging.info("update '{}' in shelve DB with '{}' finish".format(
                data, short_result))


def handler_error():
    ''' -[x] 替换成 logging 的 error '''
    try:
        while True:
            command, data, errmsg = Qid_err.get()
            logging.error("{}@{}: '{}'".format(command, data, errmsg, ))
    except Exception as e:
        print("handler_error(): Exception: ", e, file=sys.stderr)


def main():
    # program run start flag
    logging.warning("=" * 30)
    logging.warning(" " * 13 + "Start loop Articles")
    logging.warning("=" * 30)

    thread_pool = []
    for i in range(CONF.THREAD_NUM):
        work = Work()
        t = threading.Thread(target=work.do_work_from_queue)
        t.setDaemon(True)
        thread_pool.append(t)
        t.start()
    del t, work

    # handler result mainly update shelve DB
    t = threading.Thread(target=handler_result)
    t.setDaemon(True)
    thread_pool.append(t)
    t.start()

    t = threading.Thread(target=handler_error)
    t.setDaemon(True)  # True 表示不关心的子线程状态，父线程退出，则程序退出
    t.start()

    #
    # catch singal(Ctrl+C)
    #
    signal.signal(signal.SIGINT, sigint_handler)

    for existing_thread in thread_pool:
        ''' 修改代码要随时小心线程退出不干净导致程序 hang 死'''
        existing_thread.join()
        logging.debug("{} exit".format(existing_thread))

    del thread_pool[:]


if __name__ == "__main__":
    logging.basicConfig(
        filename=CONF.LOGGING_FILE,
        level=logging.INFO,
        # level=logging.DEBUG,
        format='[%(asctime)s]%(levelname)-9s%(message)s',
    )

    main()
