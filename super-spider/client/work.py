"""client/work.py

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


######################################
#  system wide global variables      #
######################################
progQ = progsys.progQ
pmsg = progsys.pmsg
progquits = progsys.progquits

from . import tasksQ


class Work(Thread):
    '''
        -[o] more functional - set subject with next run time;
             then loop subjects in tasksQ.
    '''

    def wheather_quit(self, tim=1):
        try:
            prog_msg = progQ.get(timeout=tim)  # do not block!
            if prog_msg == pmsg.QUIT:
                progQ.put(pmsg.QUIT)
                return True
            # do other thread control thins...
        except EmptyQ:
            print("Work@wheather_quit: keep running...")
            return False
        else:
            print("Work@wheather_quit: prog_msg=={}".format(prog_msg))
            # not belong to me
            progQ.put(prog_msg)
        return False

    def run(self):
        while True:
            try:
                # -[o] will sleep in sub.run() for multi-subject
                _timesleep = self.loop()
            except RuntimeError:
                break

            if self.wheather_quit(_timesleep):  # use block as sleep
                print("client Work: quit/stop")
                break

    def loop(self):
        try:
            # key and subject-monitor ###########################
            # -[o] 按目前这种写法，需要优先队列！
            sub = tasksQ.get(block=False)
            print("{}@loop: {}".format(type(self).__name__, sub))
            sub.run()
            tasksQ.put(sub)

            # report status/information to server ##############
            # - [ ] ...report_info...
        except EmptyQ:
            tsleep = 30
        except Exception as err:
            import traceback; traceback.print_exc();
            print("{}@loop quit with: {}".format(type(self).__name__, err))
            # self.illness()  # TODO: for main-thread
            raise RuntimeError
        else:
            # time.sleep(60*60*24)  # one loop one userid
            tsleep = 60

        return tsleep

    def release(self):
        pass

    def register(self, _type):  # no need for now.
        if _type == 'QUIT':
            self.release()
