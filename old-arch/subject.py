#!/usr/bin/env python3

import redis
import sys
import os
import time
import asyncio
import signal


from time import sleep

from datetime import datetime
# from datetime import timedelta

# from threading import Thread
# import threading
import shelve
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
    # filename=CONF.LOGGING_FILE,
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


###################################################
# save status for stop/restart || memonto pattern #
###################################################
memento_name = ".memento"
shelve_key2storage_memento_of_subject = 'subjects'


class Memento(object):
    def __init__(self, state):
        self._state = state

    def get_saved_state(self):
        return self._state


class Originator(object):
    _state = None

    def set(self, state):
        logging.debug(
            "Originator@{}: Setting state to {}".format(id(self), state))
        self._state = state

    def save_to_memento(self, state=None):
        logging.debug("Originator@{}: Saving to Memento.".format(id(self)))
        if state:
            self.set(state)
        self.memento = Memento(self._state)
        return self.memento

    def get_memento(self):
        return self.memento

    def restore_from_memento(self, memento):
        self._state = memento.get_saved_state()
        logging.info(
            "Originator@{}: State after restoring from Memento: {}".format(
                id(self), self._state))
        return self._state

    def get_state(self):
        return self._state


#
# utility
#
g_stop_signal = False  # asycio loop
g_asyncio_subject_tasks_number = 0


def sigint_handler(signo, frame):
    ''' end game'''
    global g_stop_signal
    g_stop_signal = True


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


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

    def __init__(self, user_ids, ID, ):
        '''__init__
          length of user_ids => 60s x 60m x 24h
          one user_id except 10s, but wait 60s, 1x10x24 => 240
        '''
        self.user_ids = user_ids
        # self.__url = gen_url(user_id)
        self.user_information = None
        self.user_article = None

        # Observer ####################
        self.__observers = set()

        # memento #####################
        self.ID = ID
        self.originator = Originator()

        # memento + observer ##########
        # loading memento
        try:
            fpmemento = shelve.open(memento_name)
            self.db_saved_states = fpmemento[shelve_key2storage_memento_of_subject]

            saved_state = self.db_saved_states[self.ID]
            user_id_index = self.originator.restore_from_memento(saved_state)
            logging.info("{}@{} loading memento got last user_id: {}".format(
                type(self).__name__, self.ID, user_id_index))

            user_id_index = self.user_ids.index(user_id_index) + 1
            # rebuild user_ids
            self.user_ids = self.user_ids[user_id_index:] + self.user_ids[:user_id_index]
        except (KeyError, ValueError) as err:
            # accept empty fpmemento
            # accept notexist user_id, not change self.user_ids iteration
            logging.warning(
                "{}@{} loading memento: {}. do not set user_ids".format(
                    type(self).__name__, self.ID, err))
            logging.info("{}\n".format(self.user_ids))
        finally:
            fpmemento.close()

        # setup observer ############
        # self.q_data = queue.Queue()
        self.q_monitor = Queue()  # [CSDN Customization]
        for user_id in self.user_ids:
            self.q_monitor.put(user_id)
            # print("[Debug] q_monitor put: {}".format(self._gen_url(user_id)),
            #       file=sys.stderr)

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
        global g_stop_signal, g_asyncio_subject_tasks_number
        #
        # do update
        #
        user_information = self.user_information
        # user_article = self.user_article  #[CSDN Customization]: not acheived

        # monitor_url = self.__url  # [Orginal] xxx

        retry_time = 0
        user_id = ''
        while True:
            # memento  ##################
            self.originator.set(user_id)

            # for quit program  #########
            if g_stop_signal:
                logging.info("{}@{} quit".format(type(self).__name__, self.ID))
                break

            __start_time = datetime.now()
            user_id, retry_time = self.do_it(retry_time)
            difference = datetime.now() - __start_time
            logging.info(
                "{} cost time: {}s".format(self.ID, difference.seconds))

            # use asyncio give out control  ##########
            if retry_time == 0:
                # -[o] to long  may could not work
                # await asyncio.sleep(60 * 60 * 24)
                await asyncio.sleep(
                    difference.seconds * g_asyncio_subject_tasks_number + 10
                )  # test version of sleep time
            else:  # after sleep retry time inteval, retry again
                await asyncio.sleep(retry_time)
            # await asyncio.sleep(60)

    def do_it(self, retry_time):
        try:
            browser = None
            # [CSDN Customization]: one object loop a grade user-ids
            user_id = self.q_monitor.get()
            self.q_monitor.put(user_id)  # put back to loop

            monitor_url = self._gen_url(user_id)
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
        return user_id, retry_time

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
    prog_init()
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
    logging.info("\n====== Program exit! ======")


def update_db():
    #
    # targets set by redis DB - user id list.
    # cnblogs_com.subject.r_cb <- redis_cnblogs
    # -[x] use from Redis
    # targets_grade = ["IAMTOM", "duoduotouhenying", ]

    # memento ######################
    saved_states = {}

    def setup_subject():

        def redis_rank_grade():
            return [0, 2500, 5000, 10000, 20000, 50000, 100000]
            # return [0, 2500]

        # multi-subject(one grade user-ids one subject)
        grades = redis_rank_grade()
        _raw_redis_datas = [r_csdn.zrangebyscore("RANK", grades[i] + 1, grades[i + 1], withscores=False) for i in range(len(grades) - 1)]
        # logging.info("update_db> setup_subject> _raw_redis_datas:", _raw_redis_datas)

        subjects = []
        for idx, rawdata in enumerate(_raw_redis_datas):
            subjects.append(
                Subject([_.decode('utf-8') for _ in rawdata],
                        "index_{}".format(idx), ))

        return subjects

    def software_logical(dbobserver, setup_subject):
        subject_targets = setup_subject()

        # register
        [_.register(dbobserver) for _ in subject_targets]
        return subject_targets

    dbobserver = DB_Observer()
    subjects = software_logical(dbobserver, setup_subject)

    def run(subject_targets):
        global g_asyncio_subject_tasks_number
        # build tasks
        tasks = [_.run_asyncio_version() for _ in subject_targets]

        # fix some task have interval time issue
        g_asyncio_subject_tasks_number = len(tasks)

        loop = asyncio.get_event_loop()
        # execute coroutine
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    run(subjects)

    # collect mementos  ############
    for subject in subjects:
        saved_states[subject.ID] = subject.originator.save_to_memento()

    # save to disk  ################
    fpmemento = shelve.open(memento_name)
    fpmemento[shelve_key2storage_memento_of_subject] = saved_states
    fpmemento.close()


if __name__ == '__main__':
    main()
