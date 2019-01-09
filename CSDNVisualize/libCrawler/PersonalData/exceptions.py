# filename: exceptions.py


class NetworkError(Exception):
    """docstring for NetworkError"""
    pass


class CrawlerError(NetworkError):

    def __str__(self):
        return "CrawlerError, handler pagesource internal issue"


class CrawlerTimeoutError(CrawlerError):

    def __str__(self):
        return "timeout"
