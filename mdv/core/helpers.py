import os

from functools import reduce
from markdown.util import etree
from mdv.core.version import VERSION
if VERSION['MAJOR'] == '2':
    from HTMLParser import HTMLParser
else:
    from html.parser import HTMLParser


def j(p, f):
    '''short alias for os.path.join ... '''
    return os.path.join(p, f)


unescape = HTMLParser().unescape


# def derive(theme, mapping, placeholder=231, inclusive=True):
#     """derive a new dict from an old one a name map"""
#     n = theme.copy()
#     # {k: theme[v] for k, v in mapping.items()}
#     for k, v in mapping.items():
#         n[k] = theme[v]
#     return n

COLORSPACE = {}


def derive(theme, mapping, placeholder=231, inclusive=True):
    """derive a new dict from an old one a name map"""
    COLORSPACE.update(theme)

    def maybe(x):
        try:
            return theme[x]
        except KeyError:
            return COLORSPACE[x]

    # d = {k: theme[v] for k, v in mapping.items()}
    d = {k: maybe(v) for k, v in mapping.items()}
    if inclusive:
        d.update(theme)
    COLORSPACE.update(d)
    return d


def flatten(l):
    if not isinstance(l, list):
        return [l]
    else:
        return reduce(lambda a, b: a+b, map(flatten, l))


def Not(f):
    return lambda *p, **k: not f(*p, **k)


def Eq(v):
    return lambda w: w is v


def innerhtml(el):
    cs = [etree.tostring(c) for c in el]
    return (el.text or '').encode('utf8') + b''.join(cs)
