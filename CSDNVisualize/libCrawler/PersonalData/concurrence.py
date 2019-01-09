"""
filename    : PersonalData_v0.0.4/concurrence.py
Author      : Joseph Lin
Email       : joseph.lin@aliyun.com
Date        : 2018/Nov/03
Last Change : 2018/Nov/03

TODO:
 -[o] import error warn(虽然目前 multiprocessing 是标准库中的模块，但是难免以后这里会拓展)
"""


import multiprocessing
from time import ctime


class MyProcess(multiprocessing.Process):
    """docstring for MyProcess
    Reference: MyThread
    """

    def __init__(self, func, args, name='', doDebug=False):
        multiprocessing.Process.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.doDebug = doDebug

    def run(self):
        if self.doDebug:
            print('Starting ', self.name, 'at: ', ctime())
        # use multiprocessing.Manager() > manager.dict() to get return
        self.func(*self.args)
        if self.doDebug:
            print('Finished ', self.name, 'at: ', ctime())
