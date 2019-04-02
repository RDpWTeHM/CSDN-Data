"""utils/progsys.py

n/a
"""

import sys
import os
import time

from collections import namedtuple

# import threading
# from threading import Thread

import signal

import queue
from queue import Queue
EmptyQ = queue.Empty


###########################################
#   program-system global variables       #
###########################################
progQ = Queue()

ProgMsg = namedtuple('ProgMsg', ['QUIT', ])
pmsg = ProgMsg(QUIT='quit')

progquits = []  # thread register quit function here


def sigint_handler(signo, frame):
    ''' show catch Ctrl+C information!'''
    progQ.put(pmsg.QUIT)

    print("\nGoodbay Cruel World.....\n")

    '''
    -[o] raise SystemExit can not work at other-thread which is blocking ?
    '''
    # raise SystemExit(1)


# def sigterm_handler(signo, frame):


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


def prog_quit():
    '''
      -[o] achieve thread-quit function register
            -[x] seleniumage(v2 named) register Coded;
            -[x] client>TaskMange register Coded;
      -[o] SIGALRM to make sure not block in quit-func (program-watchdag)
    '''
    for progquit in progquits:
        progquit()


def prog_memonto():  # reserve for save status
    pass
