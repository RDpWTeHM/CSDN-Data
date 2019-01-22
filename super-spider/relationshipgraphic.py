"""super-spider/relationshipgraphic.py

n/a
"""

import os
import sys
import time
from collections import OrderedDict

import shelve
import copy


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
try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("CSDN-Data")]
    # if True:  # hole project as a package path
    if False:
        _package_path = os.path.join(_proj_abs_path, "")
    else:
        _package_path = os.path.join(_proj_abs_path, "CSDNVisualize")

    if _package_path not in sys.path:
        sys.path.append(_package_path)

    # import <project packages>
except Exception:
    import traceback; traceback.print_exc();  # -[o] fix later by using argv
    sys.exit(1)

from CSDNCrawler.models import UserID, Follows


def init_from_db_by_django():
    # Relationship Graphic DB path

    print("finish init relationship graphic from DB by Django")


todo_nodes = set()
done_nodes = set()
def update_from_db_by_django(N):
    node = "qq_29757283"  # start graphic node

    # debug_loop = 10
    debug_loop = True
    while debug_loop:
        try:
            userid = UserID.objects.get(user_id=node)

            quick_in = set(N.keys())
            if node not in quick_in:  # new node create.
                N[node] = [-1, set()]

            if True:  # (N[node][0] == -1) not skip already exist node
                follows = userid.follows_set.all()

                # init not exist in graphic node
                for _ in follows:
                    if _.follow_id not in quick_in:
                        N[_.follow_id] = [-1, set()]

                # setup node's Neighbours  #################
                _s = N[node][1]
                [_s.add(_.follow_id) for _ in follows]

                # setup node's status(total follow number) ##########
                N[node][0] = len(N[node][1])  # -[o] currently skip read from DB

                #
                # next node(grow)
                #
                print("[info] todo_nodes add: ", end='', flush=True)
                for tobe_todo_node in _s:
                    if tobe_todo_node not in done_nodes:
                        todo_nodes.add(tobe_todo_node)
                        print(tobe_todo_node, end=" ", flush=True)
                print("")

                if node in todo_nodes:
                    todo_nodes.remove(node)
                    print("[info] todo_nodes remove: ", node)
                old_done = copy.deepcopy(done_nodes)
                done_nodes.add(node)
                new_done = copy.deepcopy(done_nodes)
                print("[info] new done_nodes: ", new_done-old_done)

                node = todo_nodes.pop()
                while node in done_nodes:
                    node = todo_nodes.pop()
                print("[info] new node: ", node)
                # debug_loop -= 1
        except UserID.DoesNotExist as err:
            # pass
            node = todo_nodes.pop()
            while node in done_nodes:
                node = todo_nodes.pop()
            print("[info] new node: ", node)
            # debug_loop -= 1
        except KeyError as e:  # pop from an empty set
            print("[info] ", e)
            break
        except KeyboardInterrupt:
            print("User Interrupt!")
            break

    print("finish update relationship graphic from DB by Django")


def work_relationship_graphic():
    global IS_INIT_DB
    if IS_INIT_DB:
        init_from_db_by_django()
    else:
        update_from_db_by_django()
