"""super-spider/relationshipgraphic.py

n/a
"""

import os
import sys
import time
from collections import OrderedDict

import shelve


g_rg_db_path = None
IS_INIT_DB = True


#
# utils
#
def project_db_file_setup(workdir, belongdir, filename):
    return os.path.join(
        workdir[:workdir.find(belongdir) + len(belongdir)],
        filename)


def project_environment_check_and_setup():
    global g_rg_db_path, IS_INIT_DB
    DB_FILENAME = "relationship_graphic"
    g_rg_db_path = project_db_file_setup(os.getcwd(), "super-spider", DB_FILENAME)
    if os.path.exists(g_rg_db_path):
        IS_INIT_DB = False
    else:
        IS_INIT_DB = True


#
# DO Project environment check and setup configuration
#
project_environment_check_and_setup()



def rd_db_update(graphic_node):
    global g_rg_db_path
    rg_db_path = g_rg_db_path
    # open

    # check each neighbour node(create 'None' if not exist)

    # create node

    # save and quit
    return


#
# UserID, Follows
#
def init_from_db_by_django():
    # Relationship Graphic DB path

    print("finish init relationship graphic from DB by Django")


def update_from_db_by_django():
    pass

    print("finish update relationship graphic from DB by Django")


def work_relationship_graphic():
    global IS_INIT_DB
    if IS_INIT_DB:
        init_from_db_by_django()
    else:
        update_from_db_by_django()
