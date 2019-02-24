#!/usr/bin/env python3

"""
Usage:
  $ python -O new_main.py -b Chrome

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
    manage_selenium_stop()
    qprogram.put(('run_tasks', 'quit'))
    print("\nGoodbay Cruel World.....\n")
    raise SystemExit(1)


# def sigterm_handler(signo, frame):


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


class TaskManage(Thread):
    '''
    -[o] the threading.Thread sub-class define?
    '''

    def __init__(self, qtasks):
        Thread.__init__(self)
        self.task_nums = 0
        self.qtasks = qtasks
        self.observer = DBObserver()

    def can_handler_more_task(self):
        def check_system_resource_and_time():
            if self.task_nums < 10:
                return True
            else:
                return False

        if check_system_resource_and_time():
            return True
        else:
            return False

    def run(self):
        while True:
            if self.can_handler_more_task():
                # online  ##########################################
                # -[o] final object will carry more information
                connection = online.connect_to_server()
                obj = online.require_task(connection)

                # bridge to server ##################################
                sub = Subject_CSDN_UserInfoVisual(obj, g_options)
                sub.register(self.observer)

                self.qtasks.put(sub)
                self.task_nums += 1

            time.sleep(60)  # every 1min do TaskManage().run()


def loop():
    '''
    '''
    qtasks = queue.Queue()

    def run_tasks():
        def quit_run_tasks():
            pmsg = qprogram.get()
            try:
                if pmsg[0] == 'run_tasks':
                    if pmsg[1] == 'quit':
                        return True
            except IndexError:
                qprogram.put(pmsg)

            # not belong to me
            qprogram.put(pmsg)
            return False

        while True:
            if quit_run_tasks():
                break

            # key and subject-monitor ###########################
            sub = qtasks.get()  # block
            sub.run()
            qtasks.put(sub)

            # report status/information to server ##############
            # - [ ] ...report_info...

    t = threading.Thread(target=run_tasks)
    t.setDaemon(False)
    t.start()

    # require job to qtasks
    task_manage = TaskManage(qtasks)
    task_manage.start()


def main():
    # program-system back-end  ########################
    manage_selenium_start()

    loop()

    # program-system exit part ##########################
    # -[x] reference old CSDNData code.
    manage_selenium_stop()


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
