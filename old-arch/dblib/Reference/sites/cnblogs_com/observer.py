"""super-spider/sites/cnblogs_com/observer.py

N/A
"""

import redis
import sys
import os
import time
import asyncio

try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("Practice")]
    _package_path = os.path.join(_proj_abs_path, "super-spider")
    if _package_path not in sys.path:
        sys.path.append(_package_path)

    from hostresource.manage import Resource as Hres_Resource
except Exception:
    raise  # -[o] fix later by using argv


def main():
    pass


if __name__ == '__main__':
    main()
