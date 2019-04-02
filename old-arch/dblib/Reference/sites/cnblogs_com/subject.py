"""sites/cnblogs.com/subject.py

N/A
"""

import redis
import sys
import os
import time
import asyncio

#
# check packages
#
print("[Debug] sys.path before:", sys.path)
try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("Practice")]
    _package_path = os.path.join(_proj_abs_path, "super-spider")
    if _package_path not in sys.path:
        sys.path.append(_package_path)

    from hostresource.manage import Resource as Hres_Resource
except Exception:
    raise  # -[o] fix later by using argv
print("[Debug] sys.path after:", sys.path)

REDIS_DB_NUM = 5
REDIS_DB_NAME = "CNBLOGS_USER-ID"

r_cb = redis.Redis(host='localhost', port=6379, db=REDIS_DB_NUM)


def check_redis_db_match(redis_p, db_name):
    return redis_p.get("DB_NAME").decode('utf-8') == db_name


#
# check Redis DB
#
print("[Info] checking Redis DB...")
try:
    if check_redis_db_match(r_cb, REDIS_DB_NAME):
        print("[Info] Redis DB matching!")
    else:
        raise RuntimeError("don't match")
except (RuntimeError, Exception):
    print("[Critical] Redis DB does not match!")
    sys.exit(1)  # check redis DB fail

#
# utility
#
gen_url = lambda _id: "https://www.cnblogs.com/{!s}/".format(_id)


class CrawlError(Exception):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


class BrowserAcquireCrawlError(CrawlError):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


class Subject(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.__url = gen_url(user_id)
        self.user_information = None
        self.user_article = None
        import queue
        self.q_data = queue.Queue()

        self.__observers = set()
        # self._

    def register(self, observer):
        self.__observers.add(observer)

    def notifyAll(self, *args, **kw):
        for observer in self.__observers:
            # self necessary \/ for OBSERVER can register mutil subject
            observer.notify(self, *args, **kw)

    def run(self):
        self.__monitor_update()

    async def run_asyncio_version(self):
        await self.__monitor_update_asyncio_version()

    def __acquire_browser_handler(self):
        _browser = None
        res = Hres_Resource()
        try:
            _browser = res.acquire_browser_handler_by_create()
        except Exception:  # -[o] not decide Exception-name yet
            _browser = res.acquire_browser_handler_from_queue()

        if not _browser:
            raise BrowserAcquireCrawlError(
                "Can not acquire browser_handler resource")

        return _browser

    def __release_browser_handler(self, browser):
        res = Hres_Resource()
        res.release_browser_handler(browser)

    async def __monitor_update_asyncio_version(self):
        #
        # do update
        # -[o] those belong to "sites/cnblogs_com/user/index.py"
        #
        user_information = self.user_information
        user_article = self.user_article
        monitor_url = self.__url

        retry_time = 0
        while True:
            try:
                # do -> while
                browser = self.__acquire_browser_handler()
                browser.get(monitor_url)  # set browser with cacp - "none" \/
                time.sleep(20)  # -[o] wait browser excute, update later

                user_information = self.__parse_information(browser)
                self.notifyAll(user_information)

                user_article = self.__parse_artical(browser)
                self.notifyAll(user_article)

            except BrowserAcquireCrawlError as err:
                print("[Error] Subject> __monitor_update> ", err,
                      file=sys.stderr)
                raise StopIteration(err)
            except Exception as err:
                print("[Critical] Subject> __monitor_update> ", err,
                      file=sys.stderr)
                retry_time += 60
            else:
                retry_time = 0
            finally:
                self.__release_browser_handler(browser)
                del browser

            #
            # use asyncio give out control
            #
            # if retry_time == 0:
            #     # -[o] to long  may could not work
            #     # await asyncio.sleep(60 * 60 * 24)
            #     await asyncio.sleep(60)  # test version of sleep time
            # else:  # after sleep retry time inteval, retry again
            #     await asyncio.sleep(retry_time)
            await asyncio.sleep(60)

    def __monitor_update(self):
        use_asyncio = False

        #
        # do update
        # -[o] those belong to "sites/cnblogs_com/user/index.py"
        #
        user_information = self.user_information
        user_article = self.user_article
        monitor_url = self.__url

        retry_time = 0
        while True:
            try:
                # do -> while
                browser = self.__acquire_browser_handler()
                browser.get(monitor_url)  # set browser with cacp - "none" \/
                time.sleep(20)  # -[o] wait browser excute, update later

                user_information = self.__parse_information(browser)
                self.notifyAll(user_information)

                user_article = self.__parse_artical(browser)
                self.notifyAll(user_article)

            except BrowserAcquireCrawlError as err:
                print("[Error] Subject> __monitor_update> ", err,
                      file=sys.stderr)
                if not use_asyncio:
                    break
                else:
                    raise StopIteration(err)
            except Exception as err:
                print("[Critical] Subject> __monitor_update> ", err,
                      file=sys.stderr)
                retry_time += 60
            else:
                retry_time = 0
            finally:
                self.__release_browser_handler(browser)
                del browser

                #
                # use asyncio give out control
                #
                if not use_asyncio:
                    if not retry_time:
                        time.sleep(60 * 60 * 24)  # -[o] to long could not work
                    else:  # after sleep retry time inteval, retry again
                        time.sleep(retry_time)
                else:
                    #
                    # asyncio
                    #
                    yield

    def __parse_information(self, _browser_handler):
        return {"user_id": self.user_id, "test": True}

    def __parse_artical(self, _browser_handler):
        return {"user_id": self.user_id, "test": True}


def main():
    pass


if __name__ == '__main__':
    main()
