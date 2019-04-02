"""client/task.py

n/a
"""

import sys
import os
import time

# import threading
from threading import Thread

import queue
EmptyQ = queue.Empty


'''Solution of not installed utils/ model on Program

'''
#
# Project path
#
try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("super-spider")]
    if True:  # hole project as a package path
        _package_path = os.path.join(_proj_abs_path, "super-spider")
    else:
        _package_path = os.path.join(_proj_abs_path, "<package-dir>")

    if _package_path not in sys.path:
        sys.path.append(_package_path)

    # import <project packages>
except Exception:
    import traceback; traceback.print_exc();  # -[o] fix later by using argv
    sys.exit(1)


from utils import progsys
from observers import DBObserver
import online
from userindex import Subject_CSDN_UserInfoVisual


######################################
#  system wide global variables      #
######################################
progQ = progsys.progQ
pmsg = progsys.pmsg
progquits = progsys.progquits

from . import tasksQ


class TaskManage(Thread):
    '''-[o] tobe singleton
    '''

    def __init__(self):
        Thread.__init__(self)

        self.tasksQ = tasksQ
        self.task_nums = 0
        self.stop_more = False

        self.observer = DBObserver()

    def register(self, _type):
        if _type == 'QUIT':
            # -[o] make server know this-client
            #      not handler those tasks(user ids) any more
            progquits.append(self.release_tasks)
        elif _type == 'ILLNESS':  # reserver extension
            pass

    def handler_more_task(self):

        def check_system_resource_and_time():
            if self.task_nums < 6:
                return True
            else:
                return False

        if self.stop_more is False and check_system_resource_and_time():
            return True
        else:
            return False

    def release_tasks(self):
        pass

    def wheather_quit(self, tim=False):
        if isinstance(tim, int):
            q_get_kwargs = {'timeout': tim}
        else:  # if tim type error, should throw error
            q_get_kwargs = {'block': tim}

        try:
            prog_msg = progQ.get(**q_get_kwargs)  # do not block!
            if prog_msg == pmsg.QUIT:
                progQ.put(prog_msg)
                return True
            # do other thread control things
        except EmptyQ:
            print("TaskManage@loop>wheather_quit: keep running...")
            return False
        else:
            print("TaskManage@loop>wheather_quit: prog_msg=={}".format(prog_msg))
            # not belong to me
            progQ.put(prog_msg)
        return False

    def run(self):
        '''线程类：
          -[x] 线程终止
          -[o] 含有 socket, IO 超时
        '''

        while True:
            try:
                self.loop()
            except RuntimeError:
                break

            if self.wheather_quit(60):  # every 1min do TaskManage().run()
                print("{}@run: Thread quit".format(type(self).__name__))
                break

    def loop(self):
        try:
            if self.handler_more_task():
                # online  ##########################################
                # -[o] final object will carry more information
                connection = online.connect_to_server()
                obj = online.require_task(connection)
                print("{}@run: online got obj: {}".format(
                    type(self).__name__, obj))

                # bridge to server ##################################
                sub = Subject_CSDN_UserInfoVisual(obj, 'Chrome')  # g_options)
                sub.register(self.observer)

                self.tasksQ.put(sub)
                self.task_nums += 1
        except ValueError as err:
            '''如何运行到这里：
                ValueError 在 online.require_task 抛出，
                抛出的条件是先继续请求，然后 server 回复 '' 字符串。
                    server 回复 '' 字符串的条件检查代码。
                修改 `self.task_nums < 4` 判断条件，使最大数值大于 server user id list
                的长度，这里就可以验证这个 except 代码是否工作！
            '''
            print("{}@loop: {}".format(type(self).__name__, err))
            self.stop_more = True
        except Exception as err:
            import traceback; traceback.print_exc();
            print("{}@loop quit whith: {}".format(type(self).__name__, err))
            # self.illness()  # TODO: for main-thread
            raise RuntimeError
