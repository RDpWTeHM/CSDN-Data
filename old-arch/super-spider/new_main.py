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
# import queue

# import signal

# program-system    #################
from utils import progsys
from utils.progsys import prog_init

# main-thread(program)  ##############
import progtask

# component    ######################
from crawllib import resourcemanage

# import client
from client.task import TaskManage
from client.work import Work


###########################################
# main-thread global variables            #
###########################################
g_options = None

# program-system  ##############
progQ = progsys.progQ
pmsg = progsys.pmsg
progquits = progsys.progquits

# duty of main-thread  ##########
g_thrs = []  # threads need to be wait exit.


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
    t = Thread(target=res.handler_quit)
    t.start()
    g_thrs.append(t)


def seleniumage_quit_register():
    progquits.append(manage_selenium_stop)


def main():
    # program-system back-end  ########################
    manage_selenium_start()
    seleniumage_quit_register()  # seleniumage--v2 name

    # real client-system, do the main-function  #######
    # other-thread 2 -- task_manage
    # require job to tasksQ
    print("start task-mange")
    task_manage = TaskManage()
    task_manage.start()
    task_manage.register('QUIT')
    g_thrs.append(task_manage)

    print("start work")
    work = Work()
    work.start()
    g_thrs.append(work)

    # main-thread     ###################################
    progtask.progage()

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
