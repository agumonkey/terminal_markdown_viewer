'''
lxml.etree utils
'''

import re


class AbstractElementTreeWalk:

    def __init__(self, tree):
        self.tree = tree

    def walk(self):
        ''' walker '''
        def _(e, d=0):
            for k in e:
                yield from _(k, d+1)
            yield self.tag(e, d)
        yield from _(self.tree)

    def tag(self, e):
        pass


class DummyWalker(AbstractElementTreeWalk):

    def tag(self, e, d):
        # print(d * '>>', e.tag, '@', e.attrib, '$', e.text)
        import pdb; pdb.set_trace()

        print(d * '>>', e.tag, e.attrib, re.sub(r'[\n\r]', '\\\\\'n', str(e.text)))
