#!/usr/bin/env python3

"""threadpool.py

TODO:
  -[x] sys.stdout.write() in show_all_result/show_all_error - logging.info
"""
import sys
import queue
# import threading

from spider.daemonize_use_threadpool import Qin, Qout, Qerr, Pool, browserQ

import logging


def report_error():
    '''通过将错误信息放入 Qerr 来报告错误'''
    Qerr.put(sys.exc_info()[:2])


def get_all_from_queue(Q):
    '''可以获取队列 Q 中所有项，无须等待'''
    try:
        while True:
            yield Q.get_nowait()
    except queue.Empty:
        raise StopIteration


def request_work(data, command='process'):
    '''工作请求在 Qin 中形如（command，data）的数对'''
    Qin.put((command, data))


def get_result():
    return Qout.get()  # 这里可能会停止并等待


def show_all_results():
    for result in get_all_from_queue(Qout):
        logging.info('result: {}'.format(result))


def show_all_errors():
    for etyp, err in get_all_from_queue(Qerr):
        logging.info("Error: {} {}".format(etyp, err))


def stop_and_free_thread_pool():
    # 顺序使很重要的，首先要求所有线程停止
    for i in range(len(Pool)):
        request_work(str(Pool[i]), 'stop')

    # 然后，等待每个线程的终止
    for existing_thread in Pool:
        existing_thread.join()

    # 清除线程池
    del Pool[:]


if __name__ == "__main__":
    print("{}\n{}".format("not usage like this!",
                          "this .py should be module!"),
          file=sys.stderr)
    sys.exit(1)
