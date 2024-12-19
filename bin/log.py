import sys
from config import DEBUG


def log(level, msg, *args):
    """
        Write log messages to stderr.

        :param level:
        :param msg:
        :param args:
        :return:
    """

    m = f'[mattermost-alert] [{level}] {msg}'

    if len(args) > 0:
        m += ': '
        m += ' '.join([str(a) for a in args])

    sys.stderr.write(m + '\n')


def info(msg, *args):
    """
        Write info messages.

        :param msg:
        :param args:
        :return:
    """

    log('info', msg, *args)


def error(msg, *args):
    """
        Write info messages.

        :param msg:
        :param args:
        :return:
    """

    log('error', msg, *args)


def debug(msg, *args):
    """
        Write debug messages.

        :param msg:
        :param args:
        :return:
    """

    if DEBUG:
        log('--> debug <--', msg, *args)
