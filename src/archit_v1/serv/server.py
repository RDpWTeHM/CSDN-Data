# serv/server.py
"""
"""

import sys
from time import sleep
from time import ctime
from functools import partial


dbg_print = partial(print, file=sys.stderr)


def run():
    '''loop until universe collapses'''

    while True:
        try:
            loop()
        except Exception as err:
            print("{}".format(err), file=sys.stderr)
            sleep(10)


def loop():
    from csdndata.models import UserID

    sleep(5)

    objs = UserID.objects.all()[:3]
    dbg_print("##{}##".format(ctime()), end="  ", flush=True)
    [dbg_print("{}".format(obj), end="\t", flush=True) for obj in objs]
    dbg_print("")
