'''
fake interim loggers
'''


def info(*msg):
    print(*('[info]',) + msg)


def warn(*msg):
    print(*('[warn]',) + msg)
