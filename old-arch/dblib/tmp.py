#!/usr/bin/env python3


"""
def main(*args):
    print("main(*args) args: ", args)
    print("main(*args) *args: {}".format(*args))


if __name__ == "__main__":
    from optparse import OptionParser
    usage = "Usage: %prog [option] arg1 arg2"

    parser = OptionParser(usage=usage)
    parser.add_option("-b", "--browser",
                      action="store_true", dest="verbose",
                      help="Chrome Edge(Windows Platform) Firefox")

    (options, args) = parser.parse_args()

    print("type(options): {!r}".format(type(options)))
    print("options: {}".format(options))
    print(args)

    main(args)
"""

"""
def main(argv):
    print("main(argv) argv: ", argv)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Specific Browser Type")

    parser.add_argument("--browser", nargs=1, type=str,
                        help="browser type: Chrome or Edge(Windows) Firefox")

    args = parser.parse_args()
    print("type(args = parser.parse_args()): {!r}".format(type(args)))
    print("args: ", args)
    print("args.browser: ", args.browser)
    print("args.browser[0]: ", args.browser[0])

    argv = None
    main(argv)
"""


from selenium import webdriver

g_which_browser = None


def main():
    _f = getattr(webdriver, g_which_browser)
    browser = _f()
    browser.get("https://www.baidu.com")
    browser.quit


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Specific Browser Type")

    parser.add_argument('-b', "--browser", dest='browser', required=True, action='store',
                        choices={'Chrome', 'Edge', 'Firefox'},
                        # default='Chrome'
                        help="Chrome or Edge(Windows platform) or Firefox")
    args = parser.parse_args()
    if __debug__:
        print("type(args = parser.parse_args()): {!r}".format(type(args)))
        print("args: ", args)
        print("args.browser: ", args.browser)

    g_which_browser = args.browser

    main()
