#!/usr/bin/env python3

"""
Usage:
  terminal-1 $ python tmp.py # or $ python >>> import tmp; tmp.server_on()
  terminal-2 $ python -O new_main.py -b Chrome

TODO:
  -[o] n/a
"""


import sys
import os
import time

import threading
from threading import Thread
import queue

from crawllib import resourcemanage

from userindex import Subject_CSDN_UserInfoVisual
from observers import DBObserver
import online

import signal


qprogram = queue.Queue()
g_options = None
qtasks = queue.Queue()
g_thrs = []


def manage_selenium_start():
    res = resourcemanage.BrowserResource()
    if __debug__:
        print("check Singleton> id(res): {}".format(id(res)),
              file=sys.stderr)
    t = threading.Thread(target=res.manage, )
    t.setDaemon(True)
    t.start()
    del t


def manage_selenium_stop():
    res = resourcemanage.BrowserResource()
    res.handler_quit()


def sigint_handler(signo, frame):
    ''' show catch Ctrl+C information!'''
    t = Thread(target=manage_selenium_stop)
    t.start()
    g_thrs.append(t)

    qprogram.put('quit')
    # qprogram.put(('task_manage', 'quit'))
    print("\nGoodbay Cruel World.....\n")
    # raise SystemExit(1)


# def sigterm_handler(signo, frame):


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


class TaskManage(Thread):
    '''-[o] tobe singleton
    '''

    def __init__(self, qtasks):
        Thread.__init__(self)

        self.qtasks = qtasks
        self.task_nums = 0
        self.stop_more = False

        self.observer = DBObserver()

    def quit_task_manage(self, tim=False):
        try:
            pmsg = qprogram.get(timeout=tim)  # do not block!
            if pmsg == 'quit':
                qprogram.put(pmsg)
                return True
            # do other thread control things
        except queue.Empty:
            print("@loop>quit_task_manage: keep running...")
            return False
        else:
            print("@loop>quit_task_manage: pmsg=={}".format(pmsg))
            # not belong to me
            qprogram.put(pmsg)
        return False

    def handler_more_task(self):

        def check_system_resource_and_time():
            if self.task_nums < 4:
                return True
            else:
                return False

        if self.stop_more is False and check_system_resource_and_time():
            return True
        else:
            return False

    def release_tasks(self):
        pass

    def run(self):
        '''线程类：
          -[x] 线程终止
          -[o] 含有 socket, IO 超时
        '''

        while True:
            try:
                if self.handler_more_task():
                    # online  ##########################################
                    # -[o] final object will carry more information
                    connection = online.connect_to_server()
                    obj = online.require_task(connection)
                    print("{}@run: online got obj: {}".format(
                        type(self).__name__, obj))

                    # bridge to server ##################################
                    sub = Subject_CSDN_UserInfoVisual(obj, g_options)
                    sub.register(self.observer)

                    self.qtasks.put(sub)
                    self.task_nums += 1
            except ValueError as err:
                '''如何运行到这里：
                    ValueError 在 online.require_task 抛出，
                    抛出的条件是先继续请求，然后 server 回复 '' 字符串。
                        server 回复 '' 字符串的条件检查代码。
                    修改 `self.task_nums < 4` 判断条件，使最大数值大于 server user id list
                    的长度，这里就可以验证这个 except 代码是否工作！
                '''
                print("{}@run: {}".format(type(self).__name__, err))
                self.stop_more = True
            except Exception as err:
                import traceback; traceback.print_exc();
                print("{}@run quit whith: {}".format(type(self).__name__, err))
                self.release_tasks()
                break

            if self.quit_task_manage(60):  # every 1min do TaskManage().run()
                # -[o] make server know this-client
                #      not handler those tasks(user ids) any more
                self.release_tasks()
                print("{}@run: Thread quit".format(type(self).__name__))
                break


def loop():
    '''
        -[o] more functional - set subject with next run time;
             then loop subjects in qtasks.
    '''

    def quit_run_tasks(tim=1):
        try:
            pmsg = qprogram.get(timeout=tim)  # do not block!
            if pmsg == 'quit':
                qprogram.put(pmsg)
                return True
            # do other thread control thins...
        except queue.Empty:
            print("@loop>quit_run_tasks: keep running...")
            return False
        else:
            print("@loop>quit_run_tasks: pmsg=={}".format(pmsg))
            # not belong to me
            qprogram.put(pmsg)
        return False

    while True:
        # -[o] will sleep in sub.run() for multi-subject
        try:
            # key and subject-monitor ###########################
            sub = qtasks.get(block=False)
            print("@loop: {}".format(sub))
            sub.run()
            qtasks.put(sub)

            # report status/information to server ##############
            # - [ ] ...report_info...
        except queue.Empty:
            tsleep = 30
        except Exception as err:
            import traceback; traceback.print_exc();
            print("@loop quit with: {}".format(err))
            break
        else:
            # time.sleep(60*60*24)  # one loop one userid
            tsleep = 60

        if quit_run_tasks(tsleep):  # use block as sleep
            print("quit run_tasks")
            break


def main():
    # program-system back-end  ########################
    manage_selenium_start()

    # other-thread 2 -- task_manage
    # require job to qtasks
    task_manage = TaskManage(qtasks)
    task_manage.start()
    g_thrs.append(task_manage)

    print("start loop")
    loop()
    print("end loop")

    # program-system exit part ##########################
    # -[x] reference old CSDNData code.
    for t in g_thrs:
        t.join()


if __name__ == '__main__':
    if not __debug__:
        import argparse
        # usage = "Usage: %prog -O -b(--browser) <which browser>"
        # parser = OptionParser(usage=usage)
        parser = argparse.ArgumentParser(description="Specific Browser Type")

        parser.add_argument('-b', "--browser", dest='browser',
                            required=True, action='store',
                            choices={'Chrome', 'Edge', 'Firefox'},
                            # default='Chrome'
                            help="Chrome or Edge(Windows platform) or Firefox")
        args = parser.parse_args()

        g_options = args.browser

    prog_init()  # register signal; etc...

    main()


"""附
==== tmp.py 代码模拟 server ======
'''
-[o] got client quit information, put associate user_id back
'''
import os
import sys
import copy

from multiprocessing.connection import Listener


def run_sever():
    return Listener(('', 2736), authkey=b'CSDN-Data')


def response_user_id(connection, user_id):
    try:
        connection.send(user_id)
        while True:
            print(connection.recv())
    except EOFError:
        print("finished")

user_id_list = [
    'qq_29757283',
    'magic_wz',
    'alen1985',
    'liuzhixiong_521',
]

user_id_be_monitor = set()
user_id_left = set()
user_id_list_copy = set()

def give_user_id(conn):
    user_id_list_copy = set(user_id_list)
    user_id_left = user_id_list_copy - user_id_be_monitor

    try:
        new_be_monitor = user_id_left.pop()
        response_user_id(conn, copy.copy(new_be_monitor))
    except KeyError:
        response_user_id(conn, '')
    except Exception as err:
        import traceback; traceback.print_exc();
        print("[debug](NOT quit)@give_user_id: {}".format(err))
    else:  # success
        user_id_be_monitor.add(new_be_monitor)


def server_on():
    serv = run_sever()
    while True:
        try:
            client = serv.accept()
            print(client.recv())
            give_user_id(client)
        except Exception as err:
            import traceback; traceback.print_exc();
            raise SystemExit("@server_on: {}".format(err))
        except InterruptedError:
            raise SystemExit("processing quit!")


def main():
    try:
        server_on()
    except InterruptedError:
        raise SystemExit("processing quit!")


if __name__ == '__main__':
    main()

"""
