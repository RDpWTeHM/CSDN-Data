"""super-spider/online.py

bring MONITOR online to SERVER(database, tasks)

TODO:
 n/a

"""

import os
import sys
from multiprocessing.connection import Client
# ConnectionRefusedError

###########################################
#                 Configuration           #
###########################################
SERVER_PORT = 2736  # 9-keybord of CSDN
SERVER_DOMAIN = "127.0.0.1"
SERVER_AUTHKEY = 'CSDN-Data'


def connect_to_server():
    print("online.py: connectting to SERVER...")
    try:
        conn = Client((SERVER_DOMAIN, SERVER_PORT),
                      authkey=SERVER_AUTHKEY.encode('utf-8'))
    except EOFError:
        raise SystemExit("Server positively close connnection before finish things to be done.")
    except ConnectionRefusedError:
        raise SystemExit("Fail to connect SERVER!")

    except Exception:
        import traceback; traceback.print_exc();
    else:
        print("online.py: connection established!")
        return conn


def require_task(conn):
    print("online.py: require task...")
    obj = None
    try:
        conn.send("require task")
        recv = conn.recv()
        # checking_receive(recv)
        obj = recv
        print("online.py: finish require task.")

    except EOFError:
        raise SystemExit("Server positively close connnection before finish things to be done.")

    except Exception:
        import traceback; traceback.print_exc();

    else:
        pass
    finally:
        conn.close()

    return obj
