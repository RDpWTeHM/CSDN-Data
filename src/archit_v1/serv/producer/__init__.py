# serv/producer/__init__.py
"""
Note:
    producer/ under django-project -> "serv/",
    but it's not application of django

"""

import sys
# import os
from time import sleep
from time import ctime

from functools import partial

from csdndata.models import UserID


dbg_print = partial(print, file=sys.stderr)


def run():
    while True:
        try:
            loop()
        except Exception as err:
            print("{}".format(err), file=sys.stderr)
            sleep(10)


def loop():
    ''''''

    objs = UserID.objects.all()[:3]
    dbg_print("##{}##".format(ctime()), end="  ", flush=True)
    [dbg_print("{}".format(obj), end="\t", flush=True) for obj in objs]
    dbg_print("")

    sleep(5)
