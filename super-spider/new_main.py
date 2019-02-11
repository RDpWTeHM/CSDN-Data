#!/usr/bin/env python3


"""
"""
import sys
import os

from userindex import Subject_CSDN_UserInfoVisual
from observers import DBObserver
import online

import signal


def sigint_handler(signo, frame):
    ''' show catch Ctrl+C information!'''
    print("\nGoodbay Cruel World.....\n")
    raise SystemExit(1)


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


g_options = None


def main():
    # connection = online.connect_to_server()
    # obj = online.require_task(connection)
    obj = 'qq_29757283'  # real object will carry more information

    observer = DBObserver()
    sub = Subject_CSDN_UserInfoVisual(obj, g_options)
    sub.register(observer)
    sub.run()


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
