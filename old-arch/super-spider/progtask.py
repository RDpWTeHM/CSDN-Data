"""progtask.py

n/a
"""

import sys
import os
import time


# import queue
# import queue.Empty as EmptyQ


from utils import progsys  # *.py in program root, use 'folder' directory


######################################
#  system wide global variables      #
######################################
progQ = progsys.progQ
pmsg = progsys.pmsg


from utils.progsys import prog_quit, prog_memonto


def progage():  # program manage
    while True:
        try:
            manage_loop()
        except RuntimeError:
            return  # quit main-thread loop


def manage_loop():
    try:
        # main-thread: program schedule
        _task = progQ.get()  # -[o] fine block?

        if _task == pmsg.QUIT:
            progQ.put(pmsg.QUIT)
            prog_quit()
            prog_memonto()
            raise RuntimeError  # for break loop
        # elif ...
        #     restart_prog()
    except RuntimeError:
        raise
    except Exception as err:
        import traceback; traceback.print_exc();
        # logging.error("manage_loop: {}".format(err))
        print("manage_loop: {}".format(err))
        raise RuntimeError


def restart_prog():
    pass
