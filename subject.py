#!/usr/bin/env python3

import redis
import sys
import os
import time
import asyncio


from time import sleep

from datetime import datetime
# from datetime import timedelta

# from threading import Thread
import threading
from queue import Queue
import requests
import logging
import traceback
from requests.exceptions import ConnectionError

###############################
#     logging                 #
###############################
import conf.client_active_daemon
CONF = conf.client_active_daemon.conf

logging.basicConfig(
    filename=CONF.LOGGING_FILE,
    level=logging.INFO,
    # level=logging.DEBUG,
    format='[%(asctime)s]%(levelname)-9s%(message)s',
)

#########################################################
#                 Design Pattern                        #
#########################################################

###########################
# DB for subject(monitor) #
###########################
# -[o] need update those db code
REDIS_DB_NUM = 1
REDIS_DB_NAME = "CSDN-Data_UserID"

r_csdn = redis.Redis(host='localhost', port=6379, db=REDIS_DB_NUM)
# r_csdn = redis.Redis(host='192.168.29.103', port=6379, db=REDIS_DB_NUM)


def check_redis_db_match(redis_p, db_name):
    return redis_p.get("DB_NAME").decode('utf-8') == db_name


#
# check Redis DB
#
logging.info("checking Redis DB...")
try:
    if check_redis_db_match(r_csdn, REDIS_DB_NAME):
        logging.info("Redis DB matching!")
    else:
        raise RuntimeError("don't match")
except (RuntimeError, Exception):
    logging.critical("Redis DB does not match!")
    sys.exit(1)  # check redis DB fail


#
# utility
#
# gen_url = lambda _id: "https://me.csdn.net/{!s}".format(_id)


class CrawlError(Exception):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


class BrowserAcquireCrawlError(CrawlError):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


#
# Subject (monitor user id) - Observer pattern
#
class Subject(object):
    '''Subject
      -[o] need update package reference
    '''

    def __init__(self, user_ids):
        '''__init__
          length of user_ids => 60s x 60m x 24h
          one user_id except 10s, but wait 60s, 1x10x24 => 240
        '''
        self.user_ids = user_ids
        # self.__url = gen_url(user_id)
        self.user_information = None
        self.user_article = None
        # self.q_data = queue.Queue()
        self.q_monitor = Queue()  # [CSDN Customization]
        for user_id in user_ids:
            self.q_monitor.put(self._gen_url(user_id))
            # print("[Debug] q_monitor put: {}".format(self._gen_url(user_id)),
            #       file=sys.stderr)

        self.__observers = set()
        # self._

    def _gen_url(self, user_id):
        '''__url stracture:
          - django server
          - CSDN Crawler Application
          - active url
          - specify target-format
        '''
        __url = "http://localhost:8010/" +\
                "CSDNCrawler/" +\
                "startcrawler/" + \
                "?user_id=" + "{!s}".format(user_id)
        return __url

    def register(self, observer):
        self.__observers.add(observer)

    def notifyAll(self, *args, **kw):
        for observer in self.__observers:
            try:
                # self necessary \/ for OBSERVER can register mutil subject
                # ret = observer.notify(self, *args, **kw)
                observer.notify(self, *args, **kw)
            except Exception as err:
                logging.critical(
                    "Subject> notifyAll> observer.notify{}".format(err))
            else:
                # print("{!r}".format(ret))
                pass

    async def run_asyncio_version(self):
        await self.__monitor_update_asyncio_version()

    def __acquire_browser_handler(self):
        # _browser = None
        return True

    def __release_browser_handler(self, browser):
        pass

    async def __monitor_update_asyncio_version(self):
        #
        # do update
        #
        user_information = self.user_information
        # user_article = self.user_article  #[CSDN Customization]: not acheived

        # monitor_url = self.__url  # [Orginal] xxx

        retry_time = 0
        while True:
            try:
                browser = None
                # [CSDN Customization]: one object loop a grade user-ids
                monitor_url = self.q_monitor.get()
                self.q_monitor.put(monitor_url)  # put back to loop
                logging.info("monitor_url: {} to notifyAll.".format(monitor_url))

                # [CSDN Customization]: not be used, currently
                browser = self.__acquire_browser_handler()
                # browser.get(monitor_url)  # set browser with cacp - "none" \/
                # time.sleep(20)  # -[o] wait browser excute, update later

                # user_information = self.__parse_information(browser)
                data = {"requests": monitor_url}
                user_information = self.__parse_information(data)
                self.notifyAll(user_information)  # notifyAll django-crawl-url

                # user_article = self.__parse_artical(browser)
                # self.notifyAll(user_article)

            except BrowserAcquireCrawlError as err:
                logging.error("Subject> __monitor_update> ", err)
                raise StopIteration(err)
            except Exception as err:
                logging.critical("Subject> __monitor_update> ", err)
                retry_time += 60
            else:
                retry_time = 0
            finally:
                # [CSDN Customization]: not be used
                if browser:
                    self.__release_browser_handler(browser)
                    del browser

            #
            # use asyncio give out control
            #
            if retry_time == 0:
                # -[o] to long  may could not work
                # await asyncio.sleep(60 * 60 * 24)
                await asyncio.sleep(60)  # test version of sleep time
            else:  # after sleep retry time inteval, retry again
                await asyncio.sleep(retry_time)
            # await asyncio.sleep(60)

    def __parse_information(self, _browser_handler):
        # return {"user_id": self.user_id, "test": True}
        ''' return user_information
         -[o] user_information used to notifyAll,
           update to django-crawl url
        '''
        # currently, _browser_handler is fake,
        # the real value is request django crawl url, used to notifyAll
        return _browser_handler

    def __parse_artical(self, _browser_handler):
        # return {"user_id": self.user_id, "test": True}
        # return user_article
        # -[o] user_article used to notifyAll,
        #   not be used fornow
        raise RuntimeError("not Acheived yet")


#
# observer.py
#
class DB_Observer():
    _totimes = 0

    def runningsleep(self, IsNoServer):
        if IsNoServer is False:
            self._totimes = 0
        elif IsNoServer is True:
            self._totimes += 1
            sleep(self._totimes * CONF.NOSERVER_BASEWAITE)
        else:
            raise Exception("<timeoutsleep> Error parameter gived!")

    def notify(self, _subj, _d):
        logging.info("{} notify: {}".format(
            type(_subj).__name__, _d))
        #
        # use django db-rest API to update data
        # -[o] csdn current case,
        #   request crawl url is OK
        return self._update_visual_user_info(_d)

    def _update_visual_user_info(self, _d):
        try:
            r = requests.get(_d["requests"])
        except ConnectionError as e_conn:
            logging.error(
                "requests.get(url) ConnectionError: %s" % (e_conn))
            self.runningsleep(True)
        except Exception as e:
            traceback.print_exc()
            logging.error(
                "requests.get(url) unknow Exception: %s" % (e))
            self.runningsleep(True)
        else:
            self.runningsleep(False)
        if r.status_code != 200:
            raise Exception("r.status_code != 200")
        result = r.text

        # 没有什么需要做的了，工作在 django 的 views.<func> 中完成。
        logging.info("DB_Observer: observer update" +
                     "'{}' =result=>".format(_d["requests"]) +
                     "success")
        return result


#
# demo -[o] need update code
#
def main():
    #
    # run Resource in mange.py maybe if need.
    #
    ''' why use thread can not work???
    from threading import Thread
    t = Thread(target=update_db)
    t.setDaemon(False)
    t.start()

    # wait finish
    t.join()
    '''

    # -[x] Bug: it will request twice? unknow resonse
    #  run, this program twice by mistake,
    #  -[o] fix this issue!
    update_db()


def update_db():
    # multi-subject(one grade user-ids one subject)
    grades = []

    #
    # targets set by redis DB - user id list.
    # cnblogs_com.subject.r_cb <- redis_cnblogs
    # -[x] use from Redis
    # targets_grade = ["IAMTOM", "duoduotouhenying", ]

    # 1592 currently
    _raw_radis_data = r_csdn.zrangebyscore("RANK", 1, 2500, withscores=True)
    targets_grade = [_[0].decode('utf-8') for _ in _raw_radis_data]
    grades.append(targets_grade)

    _raw_radis_data = r_csdn.zrangebyscore("RANK", 2501, 5000, withscores=False)
    targets_grade = [_.decode('utf-8') for _ in _raw_radis_data]
    grades.append(targets_grade)

    # 5001~10000 => 1408 currently
    _raw_radis_data = r_csdn.zrangebyscore("RANK", 5001, 10000, withscores=False)
    targets_grade = [_.decode('utf-8') for _ in _raw_radis_data]
    grades.append(targets_grade)

    _raw_radis_data = r_csdn.zrangebyscore("RANK", 10001, 20000, withscores=False) # 1408 currently
    targets_grade = [_.decode('utf-8') for _ in _raw_radis_data]
    grades.append(targets_grade)

    _raw_radis_data = r_csdn.zrangebyscore("RANK", 20001, 80000, withscores=False) # 1554 currently
    targets_grade = [_.decode('utf-8') for _ in _raw_radis_data]
    grades.append(targets_grade)

    subjs_targets = []
    [subjs_targets.append(Subject(grade)) for grade in grades]

    db_observer = DB_Observer()

    # register
    [subj_t.register(db_observer) for subj_t in subjs_targets]

    # build tasks
    tasks = [subj_t.run_asyncio_version() for subj_t in subjs_targets]

    loop = asyncio.get_event_loop()
    # execute coroutine
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    main()
