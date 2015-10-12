from markdown.util import etree

from mdv.core.ansi.base import col, low


class Tags:
    """ can be overwritten in derivations. """

    def __init__(self, scheme, cnf):
        self.scheme = scheme
        self.cnf = cnf

    def h(_, s, level):
        return '\n%s%s' % (low('#' * 0, _.cnf),
                           col(s, _.scheme['H%s' % level], _.cnf))

    def h1(_, s, **kw): return _.h(s, 1)

    def h2(_, s, **kw): return _.h(s, 2)

    def h3(_, s, **kw): return _.h(s, 3)

    def h4(_, s, **kw): return _.h(s, 4)

    def h5(_, s, **kw): return _.h(s, 5)

    def h6(_, s, **kw): return _.h(s, 5)  # have not more then 5

    def h7(_, s, **kw): return _.h(s, 5)  # cols in the themes, low them all

    def h8(_, s, **kw): return _.h(s, 5)

    def p(_, s, **kw): return col(s, _.scheme['T'], _.cnf)

    def a(_, s, **kw): return col(s, _.scheme['L'], _.cnf)

    def hr(_, s, **kw):
        # we want nice line seps:
        hir = kw.get('hir', 1)
        ind = (hir - 1) * _.cnf.left_indent
        s = e = col(_.cnf.icons['hr_ends'], _.scheme['H%s' % hir], _.cnf)
        return low('\n%s%s%s%s%s\n' %
                   (ind, s, _.cnf.markers['hr_marker'], e, ind),
                   _.cnf)


def is_text_node(el):
    # @TOFIX: use dom, not str.split ...
    # @>>> e = lxml.etree.fromstring('<div><code>wt</code><pre>dh</pre></div>')
    # @>>> e
    # <Element div at 0x7fb91f6e0e88>
    # @>>> e.getchildren()
    # [<Element code at 0x7fb91ce7ae48>, <Element pre at 0x7fb91ea79b08>]

    # strip our tag:
    html = etree.tostring(el) \
                .decode('utf8') \
                .split('<%s' % el.tag, 1)[1] \
                .split('>', 1)[1] \
                .rsplit('>', 1)[0]

    # do we start with another tagged child which is NOT in inlines:?
    if not html.startswith('<'):
        return 1, html

    inlines = ('<em>', '<code>', '<strong>')
    for inline in inlines:
        if html.startswith(inline):
            return 1, html
    return 0, 0
