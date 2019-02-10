#!/usr/bin/env python3


"""
"""
import sys
import os

from userindex import Subject_CSDN_UserInfoVisual
from crawllib import Observer


class DBObserver(Observer):
    def notify(self, *args, **kw):
        print("BDObserver> notify: *args: {}\n\t**kw: {}".format(
            *args, **kw))


def main():
    observer = DBObserver()
    sub = Subject_CSDN_UserInfoVisual('qq_29757283', "Chrome")
    sub.register(observer)
    sub.run()


if __name__ == '__main__':
    main()
