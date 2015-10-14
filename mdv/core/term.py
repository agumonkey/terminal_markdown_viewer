import os
import logging

LOG = logging.getLogger('MDV')


class Term:

    def __init__(self, cols=80, rows=200):
        self.rows = rows
        self.cols = cols

    def __str__(self, ):
        return '<Term {cols}:{rows}>'.format(cols=self.cols, rows=self.rows)

    def dimensions(self):
        return self.rows, self.cols

    def refresh(self):
        # columns(!) - may be set to smaller width:
        try:
            r, c = list(map(int, os.popen('stty size').read().split()))
            self.rows = r
            self.cols = c
        except:
            LOG.warn('!! Could not derive your terminal width !!')
        return self
