#!/usr/bin/env python3
"""
filename: Cookbook_12.14_forkonUNIX.py

Reference: Python3-cookbook &12.14

Usage:
  要启动这个守护进程，用户需要使用如下的命令：

    bash % daemon.py start
    bash % cat /tmp/daemon.pid
    2882
    bash % tail -f /tmp/daemon.log
    Daemon started with pid 2882
    Daemon Alive! Fri Oct 12 13:45:37 2012
    Daemon Alive! Fri Oct 12 13:45:47 2012

  守护进程可以完全在后台运行，因此这个命令会立即返回。
  不过，你可以像上面那样查看与它相关的pid文件和日志。要停止这个守护进程，使用：

    bash % daemon.py stop
    bash %

"""

import os
import sys

import atexit
import signal

def daemonize(pidfile, *, stdin='/dev/null',
                          stdout='/dev/null',
                          stderr='/dev/null'):

    if os.path.exists(pidfile):
        raise RuntimeError('Already running')

    # First fork (detaches from parent)
    try:
        if os.fork() > 0:
            raise SystemExit(0)   # Parent exit
    except OSError as e:
        raise RuntimeError('fork #1 failed.')

    os.chdir('/')
    os.umask(0)
    os.setsid()
    # Second fork (relinquish session leadership)
    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError as e:
        raise RuntimeError('fork #2 failed.')

    # Flush I/O buffers
    sys.stdout.flush()
    sys.stderr.flush()

    # Replace file descriptors for stdin, stdout, and stderr
    with open(stdin, 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(stdout, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open(stderr, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Write the PID file
    with open(pidfile,'w') as f:
        print(os.getpid(),file=f)


DJANGO_PROJ_PATH = "/home/joseph/Devl/SVN/myGit/Gitee/Practice/daemon/test/create4test/"
DJANGO_PROJ_ARGV = " runserver 0.0.0.0:8000 "
DJANGO_PROJ_LOG  = "/tmp/django_proj_create4test.log"
SHELL_ARGV = " > {} 2>&1 & ".format(DJANGO_PROJ_LOG)


def start_djangoTest():
    if True:
        print("$ which python")
        import subprocess
        try:
            out_bytes = subprocess.check_output(
                'which python', timeout=1, shell=True)
        except subprocess.TimeoutExpired as e:
            print("run `$ which python` cost more than 1s is unnormal!", file=sys.stderr)
            print("subprocess.TimeoutExpired: ", e, file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            # out_bytes = e.output
            # code = e.returncode
            print("run `$ which python` Error!", file=sys.stderr)
            print("subprocess.CalledProcessError: ", e, file=sys.stderr)
            sys.exit(1)
        whichPython = out_bytes.decode('utf-8')
        if __debug__:
            print("run `$ which python`: {}\n".format(whichPython))

        os.system("{}manage.py {} {}".format(
            DJANGO_PROJ_PATH, DJANGO_PROJ_ARGV, SHELL_ARGV))
        os._exit(0)
        # raise SystemExit(0)  # not fixed [python3] <defunct>
    else:
        '''
         -[o] 当前 stdout， stdin， stderr 都和原本的进程相同，需要注意改变！
        '''
        os.execlv(
            "{}manage.py".format(DJANGO_PROJ_PATH),
            "runserver",
            "0.0.0.0:8000")
        assert False, "Should not run here"  # be notice that this stderr may not work


def main():
    import time
    sys.stdout.write('Daemon started with pid {}\n'.format(os.getpid()))
    while True:
        sys.stdout.write('Daemon Alive! {}\n'.format(time.ctime()))
        time.sleep(10)


if __name__ == '__main__':
    PIDFILE = '/tmp/daemon.pid'

    if len(sys.argv) != 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)

    if sys.argv[1] == 'start':
        try:
            daemonize(PIDFILE,
                      stdout='/tmp/daemon.log',
                      stderr='/tmp/daemon.log')
        except RuntimeError as e:
            print(e, file=sys.stderr)
            raise SystemExit(1)
        """
        try:
            ''' -[o] pid file 机制失效，
             RunPrograsDaemon.py stop 无效
            '''
            if os.fork() > 0:  # current
                main()
            else:  # child
                start_djangoTest()
        except OSError as e:
            raise RuntimeError('fork #3 for startu django test failed.')
        """
        if True:  # start django project > now, which be create4test
            '''this kind start solution could work!'''
            os.system("{}manage.py {} {}".format(
                DJANGO_PROJ_PATH, DJANGO_PROJ_ARGV, SHELL_ARGV))
        main()
    elif sys.argv[1] == 'stop':
        if os.path.exists(PIDFILE):
            with open(PIDFILE) as f:
                os.kill(int(f.read()), signal.SIGTERM)
        else:
            print('Not running', file=sys.stderr)
            raise SystemExit(1)

    else:
        print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)
