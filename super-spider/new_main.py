#!/usr/bin/env python3


"""
"""
import sys
import os

import threading

from crawllib import resourcemanage

from userindex import Subject_CSDN_UserInfoVisual
from observers import DBObserver
import online

import signal


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
    print("\nGoodbay Cruel World.....\n")
    raise SystemExit(1)


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


g_options = None


def main():
    # program-system back-end  ########################
    manage_selenium_start()

    # online  ##########################################
    # -[o] final object will carry more information
    connection = online.connect_to_server()
    obj = online.require_task(connection)

    # bridge to server ##################################
    observer = DBObserver()
    sub = Subject_CSDN_UserInfoVisual(obj, g_options)
    sub.register(observer)

    # key and subject-monitor ###########################
    sub.run()

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
