# serv/server.py
"""
"""

# import sys
from time import sleep
# from time import ctime


def run():
    '''loop until universe collapses'''

    sleep(3)  # just want to wait django-server ready

    # trick: use django-models,
    # must import after `os.environ.setdefault(`
    from usr import producer
    producer.run()
