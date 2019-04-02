# serv/usr/producer.py
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

import pika


HOST_ADDR = 'localhost'
QUEUE = 'csdndata'
ROUTING_KEY = 'csdndata'


def rabbitmq_init(queue=QUEUE):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=HOST_ADDR))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    return connection, channel


dbg_print = partial(print, file=sys.stderr)


class ThreadQuit(Exception):
    pass


def run():

    conn, chnl = rabbitmq_init()
    while True:
        try:
            loop(conn, chnl)
        except ThreadQuit:
            break
        except Exception as err:
            print("{}".format(err), file=sys.stderr)
            sleep(10)

    conn.close()  # it wouldn't run here for now actually!


def loop(connection, channel):
    ''''''

    userids = UserID.objects.all()[:3]
    # dbg_print("##{}##".format(ctime()), end="  ", flush=True)
    # [dbg_print("{}".format(obj), end="\t", flush=True) for obj in objs]
    # dbg_print("")

    dbg_print("####  {} <> producer  ####".format(ctime()))
    for userid in userids:
        channel.basic_publish(exchange='',
                              routing_key=ROUTING_KEY,
                              body=userid.user_id)

        dbg_print(" [x] Sent '{}'".format(userid.user_id))

    sleep(5)
