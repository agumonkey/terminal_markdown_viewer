'''
fake interim loggers
'''

raise Exception('This module is deprecated. Use logging.')

def info(*msg):
    print(*('[info]',) + msg)


def debug(*msg):
    print(*('[debug]',) + msg)


def warn(*msg):
    print(*('[warn]',) + msg)
