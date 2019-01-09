#!/usr/bin/env python3

"""
Reference:
 Python2 cookbook - CH9 > &9.4 使用线程池 
 (cookbook v2 = python2; cookbook v3 = python3)

Usage:
 libCrawler/ $ python [-O] ./spider/daemonize_use_threadpool.py start  # -O to disable log message
 ...
 libCrawler/ $ tail -f /tmp/20181125_1711.log.log  # [option]
 or
 libCrawler/ $ tail -f /tmp/error_20181125_1711.log.log  # [option]


TODO:
 -[x] cover code from pytho2 to python3
 -[x] add mission to pool
 -[x] start django project and this program self as daemon.
        django <=================> this program 
                 spider mission
 -[x] N/A
"""

import threading
import time
import sys
import queue
import atexit
import signal

from time import ctime
import random
from multiprocessing.connection import Listener
import traceback

from socket import *
import pickle

import os

if os.path.split(os.getcwd())[1] == 'libCrawler':
    ''' Make Sure run this program from upper folder
      due to this program need use the
      libCrawler/daemon/RunRrogasDaemon.py as module
    '''
    print("Congratulations! you use a right 'current work path'\n")
elif os.path.split(os.getcwd())[1] == 'spider':
    print("Please run me on upper folder\n"
          "\tUsage: $ [which python] "
          "./spider/daemonize_use_threadpool.py")
    sys.exit(1)  # command error
else:
    print("Don't support this\n",
          ">>>{}<<<\n".format(os.getcwd()),
          "current work path for now!")
    sys.exit(1)  # command error!

Qin = queue.Queue()
Qout = queue.Queue()
Qerr = queue.Queue()

Pool = []

browserQ = queue.Queue()

sys.path.append(os.getcwd())
from daemon.RunProgasDaemon import daemonize

sys.path.append(os.getcwd()[:os.getcwd().find("CSDNVisualize/libCrawler")-1])
import conf.handler_pagesource
CONF = conf.handler_pagesource.conf
MAX_BROWSER_RUN = CONF.MAX_BROWSER_RUN

from spider.threadpool import *

from spider.sites.csdn import PageSource
from spider.sites.csdn import HomePageSource
from spider.sites.csdn import BlogPageSource
from spider.sites.csdn import ArticlesPageSources

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging
from spider.sites.csdn import DaemonCrawlerClickError


def do_work_from_queue():
    '''工作线程的“获得一点工作”，“做一点工作的主循环”'''
    while True:
        command, item = Qin.get()  # 这里可能会停止并等待
        logging.info("command: {}; type(item): {}".format(command, type(item)))
        logging.info("item: {}".format(str(item)))
        if command == 'stop':
            logging.warning("{} stop".format(item))
            break
        try:
            # 模拟工作线程的工作
            if command == 'CSDN-Data':  # this is Customized
                logging.info("new mission, start run CSDN-Data handler")
                req_data, conn = item  # 元组拆包
                logging.warning("req_data: {}; conn: {}".format(req_data, str(conn)))
                try:
                    thisThreadBrowser = browserQ.get()  # this may block
                    safe_get_tab = thisThreadBrowser.window_handles[0]
                    logging.info("str(thisThreadBrowser) = %s" % (str(thisThreadBrowser)))
                    excute_script_str = "window.open('{}','CSDN-Data');".format("about:blank")
                    thisThreadBrowser.execute_script(excute_script_str)

                    thisThreadBrowser.switch_to.window('CSDN-Data')
                    whichPage = req_data['whichPage']
                    if whichPage == 'HomePage':
                        homepagesource = HomePageSource(thisThreadBrowser)
                        page_source = homepagesource.getPageSourceBy(req_data['req_url'])
                    elif whichPage == 'BlogPage':  # BlogPage
                        blogpagesource = BlogPageSource(thisThreadBrowser)
                        page_source = blogpagesource.getPageSourceBy(req_data['req_url'])
                    elif whichPage == 'ArticlesPages':
                        articlespagesources = ArticlesPageSources(thisThreadBrowser)
                        page_sources = articlespagesources.getPageSourcesBy(req_data['req_url'])

                    if whichPage == 'ArticlesPages':
                        conn.send(page_sources)
                    else:
                        conn.send(page_source)
                    # result = "get url: \"%s\" success!" % (req_data['req_url'])
                except TimeoutException:
                    logging.warning("browser timeout")
                    # (result, ) = ("[Error]: ##Timeout## get '" +
                    #               req_data['req_url'] + "' fail!", )
                    conn.send("timeout")  # timeout case!
                except DaemonCrawlerClickError as err:
                    logging.error("%s @ %s" % (req_data['req_url'], err))
                    conn.send("Crawler Error")
                except WebDriverException as err:
                    # sys.stderr.write("selenium > browser issue?：{}".format(err))
                    logging.error("selenium > browser issue?：{}".format(err))
                    conn.send("Crawler Error")
                except Exception as e:
                    # sys.stderr.write(
                    #     "[Error]: in commad='CSDN-Data' handler: {}\n".format(e))
                    logging.error("in commad='CSDN-Data' handler: %s" % (e))
                    conn.send("Crawler Error")
                finally:
                    thisThreadBrowser.close()
                    thisThreadBrowser.switch_to.window(safe_get_tab)
                    browserQ.put(thisThreadBrowser)
            else:
                raise (ValueError, 'Unknown command %r' % command)
        except Exception as e:
            '''
            无条件的 except 是对的，因为我们要报告所有错误
            sys.stderr.write("[Eorror]: <{}>@<{}>: {}\n".format(
                item, command, e))
            '''
            logging.error('<{}>@<{}>: {}'.format(item, command, e))
            # report_error()
            pass  # 还没有理清如何使用队列来处理线程输出
        else:
            # Qout.put(result)
            pass  # 还没有理清如何使用队列来处理线程输出


def make_and_start_thread_pool(number_of_threads_in_pool=5, daemons=True):
    '''创建一个 N 线程的池子， 使所有线程成为守护线程，启动所有线程'''
    for i in range(number_of_threads_in_pool):
        new_thread = threading.Thread(target=do_work_from_queue)
        new_thread.setDaemon(daemons)
        Pool.append(new_thread)
        new_thread.start()
    del new_thread

    t = threading.Thread(target=manage_browser)
    t.setDaemon(True)
    t.start()
    del t

    t = threading.Thread(target=server_status)
    t.setDaemon(True)
    t.start()
    del t


def manage_browser():
    pass


def handler_status(conn):
    pass


def server_status():
    while True:
        try:
            serv = Listener((CONF.STATUS_DOMAIN, CONF.STATUS_PORT),
                            authkey=b'CSDN-Data')
            client_conn = serv.accept()
            handler_status(client_conn)
        except Exception:
            traceback.print_exc()


def main(argc, argv):
    logging.warning("{}".format('=' * 30))
    logging.warning('Daemon started with pid {}'.format(os.getpid()))
    logging.warning("main start time: {}".format(ctime()))

    make_and_start_thread_pool(number_of_threads_in_pool=MAX_BROWSER_RUN)

    def client_IPC_handler(_conn):
        try:
            # while True:
            # .recv() will Blocks until there is something to receive
            #     msg = _conn.recv()

            _conn.send("SYNC")                   # ===>
            time.sleep(0.2)                      # SYNC
            msg = _conn.recv()                   # <===
            if msg == 'SYNC':                    #
                _conn.send("Req: whichPage")     # ====>
                time.sleep(0.2)                  # whichPage
                whichPage = _conn.recv()         # <====

                _conn.send("Req: req_url")       # ====>
                time.sleep(0.2)                  # req_url
                req_url = _conn.recv()           # <====

                _conn.send("Rsp: pagesource")    # =====>
                time.sleep(0.2)                  # Ready?
                IsReady = _conn.recv()           # <=====
                data = {'whichPage': whichPage,
                        'req_url': req_url,
                        'IsReady': IsReady}
                mission = (data, _conn)
                request_work(mission, command='CSDN-Data')
            else:
                raise Exception
            msg = _conn.recv()  # wait client close!
            # -[o] 这个等待 client close 需要设定超时。
        except EOFError:
            logging.warning("Connection closed!")
            return  # -[o] raise "this thread finished" is better
        else:  # -[x] fix 掉一处隐藏的 bug，如果 client 没有按预期工作，接收完成之后没有 close
            logging.warning("Server close IPC initiative, due to Client not close: {}".format(msg))
            _conn.close()

    def server_handler(address, authkey, lock=None):
        _lock = lock
        if _lock is not None:
            try:
                with _lock:
                    serv = Listener(address, authkey=authkey)
                    client_conn = serv.accept()

                client_IPC_handler(client_conn)
            except OSError as e:
                # OSError: [Errno 98] Address already in use
                logging.warning("OSError: {}; and pass this.\n".format(e))
                # pass this connection as server refuse-that client retry fail
                pass
            except Exception:
                traceback.print_exc()
        else:
            try:
                serv = Listener(address, authkey=authkey)
            except OSError as e:
                # OSError: [Errno 98] Address already in use
                # -[o] joseph, log error here
                logging.warning("OSError: {} when listen {}; and pass this.\n".format(e, address))
                # pass this connection as server refuse-that client retry fail
                return
            except Exception:
                traceback.print_exc()
                return
            if True:
                '''
                  MUST NOT use while True here,
                  this IPC only established once and quit.
                '''
                try:
                    client_conn = serv.accept()

                    client_IPC_handler(client_conn)
                except Exception:
                    traceback.print_exc()
                    return

    sockObj = socket(AF_INET, SOCK_STREAM)
    sockObj.bind((CONF.NEGOTIATE_DOMAIN, CONF.NEGOTIATE_PORT), )
    sockObj.listen(5)

    def now():
        return time.ctime(time.time())  # current time on the server

    def handleClient(connection, _lock):
        IPCNegotiate = dict()
        time.sleep(1)
        while True:
            data = connection.recv(1024)
            # data = pickle.load(data)
            if not data:
                break
            logging.warning('Recv data=> {} at {}'.format(data, now()))
            # connection.send(reply.encode())
            # check recv data is OK?
            IPCNegotiate['port'] = 10086 + random.randint(1, 10000)
            connection.send(pickle.dumps(IPCNegotiate))
            connection.close()
            break
        server_handler(('', IPCNegotiate['port']), authkey=b'CSDN-Data',
                       lock=_lock)

    # IPCListener_lock = threading.Lock()
    IPCListener_lock = None

    def dispatcher():
        while True:
            connection, address = sockObj.accept()
            logging.warning('Server Be Connected by {} at {}'.format(address, now()))
            newIPCHandlerThread = threading.Thread(
                target=handleClient,
                args=(connection, IPCListener_lock, ))
            newIPCHandlerThread.start()
    dispatcher()


# -[o] not right value here:
DJANGO_PROJ_PATH = "/home/joseph/Devl/SVN/myGit/Gitee/Practice/daemon/test/create4test/"
DJANGO_PROJ_ARGV = " runserver 0.0.0.0:8000 "
DJANGO_PROJ_LOG  = "/tmp/django_proj_create4test.log"
SHELL_ARGV = " > {} 2>&1 & ".format(DJANGO_PROJ_LOG)


if __name__ == '__main__':
    PIDFILE = CONF.PIDFILE

    if len(sys.argv) != 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)

    if sys.argv[1] == 'start':

        #
        # start Browser
        #
        def _debug_startBrowser(i):
            capa = DesiredCapabilities().CHROME
            capa["pageLoadStrategy"] = "none"
            # capa["pageLoadStrategy"] = 'eager'
            from selenium.webdriver.chrome.options import Options
            croptions = Options()
            # croptions.headless = True
            croptions.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geoko) Chrome/70.0.3538.102 Safari/537.36")

            browser = webdriver.Chrome(
                executable_path="/usr/lib/chromium-browser/chromedriver",
                desired_capabilities=capa,
                chrome_options=croptions, )
            time.sleep(1)
            x = 0 if (-1) ** int(i + 1 / 2) == 1 else 1  # 奇数 (-1)^0=1
            y = 0 if (-1) ** int(i / 2) == 1 else 1    # 偶数 -1^0=1
            print("640*x = {}".format(640 * x))
            print("\t512*y = {}\n".format(512 * y))
            browser.set_window_size(480, 480)  # not work well
            browser.set_window_position(
                320 * x * 20, 320 * y * 20)  # *100 是临时手动适配！
            browserQ.put(browser)
            del browser

        # setup browsers
        # 放在 daemonize 之前，确保 browser.quit() 之后，剩余的浏览器资源可以被 init 回收。
        if __debug__:
            setupbrowser_threads = []
            for i in range(MAX_BROWSER_RUN):
                t = threading.Thread(
                    target=_debug_startBrowser, args=(i, ))
                t.setDaemon(True)
                setupbrowser_threads.append(t)
            for i in range(MAX_BROWSER_RUN):
                setupbrowser_threads[i].start()
            for i in range(MAX_BROWSER_RUN):
                setupbrowser_threads[i].join()
        else:
            print("!!!!!update no __debug__ mode code!!!!!!", file=sys.stderr)
            sys.exit(1)
            for i in range(MAX_BROWSER_RUN):
                ffoptions = webdriver.FirefoxOptions()
                ffoptions.add_argument('-headless')
                browser = webdriver.Firefox(options=ffoptions)
                browserQ.put(browser)
                del browser

        #
        # daemonize
        #
        try:
            daemonize_LOG_PATH = CONF.LOG_PATH
            daemonize(PIDFILE,
                      stdout=daemonize_LOG_PATH + CONF.STD_FILE,
                      # stderr=daemonize_LOG_PATH + CONF.ERR_FILE)
                      stderr=daemonize_LOG_PATH + CONF.STD_FILE)

        except RuntimeError as e:
            print(e, file=sys.stderr)
            raise SystemExit(1)

        #
        # logging
        #
        logging.basicConfig(
            filename=daemonize_LOG_PATH + CONF.STD_FILE,
            # level=logging.INFO,
            level=logging.WARNING,
            format='[%(asctime)s]%(levelname)-9s%(message)s',
        )

        # Arrange to have the PID file removed on exit/signal
        atexit.register(lambda: os.remove(PIDFILE))

        # Signal handler for termination (required)
        def sigterm_handler(signo, frame):
            ''' 如果要退出程序，清除 robot browsers'''
            while True:
                try:
                    browser = browserQ.get(timeout=3)
                    browser.quit()
                except queue.Empty:
                    break

            stop_and_free_thread_pool()
            # show_all_results()   # show_all_errors()
            logging.warning("daemon end time: {}\n".format(ctime()))
            raise SystemExit(1)

        signal.signal(signal.SIGTERM, sigterm_handler)

        if False:  # start django project > now, which be create4test
            '''this kind start solution could work!'''
            os.system("{}manage.py {} {}".format(
                DJANGO_PROJ_PATH, DJANGO_PROJ_ARGV, SHELL_ARGV))

        main(len(sys.argv), sys.argv)

    elif sys.argv[1] == 'stop':
        if os.path.exists(PIDFILE):
            with open(PIDFILE) as f:
                os.kill(int(f.read()), signal.SIGTERM)
        else:
            print('Not running', file=sys.stderr)
            raise SystemExit(1)

    else:
        print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)
