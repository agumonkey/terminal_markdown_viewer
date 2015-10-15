from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from vendor.tabulate import tabulate

from .base import col, low, plain, clean_ansi
from .layout import rewrap
from .tags import Tags

from mdv.core.helpers import unescape, flatten, Not, Eq, innerhtml

# ---------------------------------------------------- Create the treeprocessor


class AnsiPrinter(Treeprocessor):

    def __init__(self, md, scheme, term, cnf):
        super().__init__(md)
        self.scheme = scheme
        self.term = term
        self.cnf = cnf
        self.tags = Tags(self.scheme, self.cnf)

        # @TOFIX ensure existence of defaults regardless
        # of config.py existence
        # a little preemptive checking for the future
        assert self.cnf.markers
        assert self.cnf.show_links in (None, True)
        assert self.cnf.left_indent
        assert self.cnf.admons
        assert self.cnf.admons['H3']
        assert self.cnf.icons
        assert self.cnf.icons['list_pref']

    def run(self, doc):
        # formatter has issues
        #  - nested lists
        #  - empty (None) results
        # @TOFIX, review logic, use clean in the mean time
        def clean(tree):
            return filter(Not(Eq(None)), flatten(tree))
        formatted = self.formatter(doc)
        cleaned = clean(formatted)
        self.markdown.ansi = '\n'.join(cleaned)

    def f_hr(self, el, hir):
        return [self.tags.hr('', hir=hir)]

    def f_text(self, el, hir):

        def is_text_node(el):
            '''
            element with only '<em>', '<code>', '<strong>'
            or plain text as element childs
            '''
            inner = innerhtml(el).decode('utf8')
            inlines = ('<em>', '<code>', '<strong>')
            is_inline = lambda s: any(s.startswith(tag) for tag in inlines)
            # do we start with another tag not in inlines
            if not inner.startswith('<') and not is_inline(inner):
                return True, inner
            else:
                return False, None

        # Inline colored elements now decoupled out of ansi.base.col()
        # but .. the formatter rewrite html tags as arbitrary ASCII codes..
        # then replaced by arbitrary associations between tags and scheme
        # colors => @WAT
        # Let's do it in one pass in the formatter.

        # def colorize_inline(s, cnf):
        #     M = cnf.markers
        #     BG = cnf.background
        #     marks = ((M['code_start'], M['code_end'], cnf.default_text['H2']),
        #              (M['strong_start'], M['strong_end'], cnf.default_text['H2']),
        #              (M['em_start'], M['em_end'], cnf.default_text['H3']))
        #     for beg, end, color in marks:
        #         if beg in s:
        #             # inline code:
        #             s = s.replace(beg, col('', color, cnf, bg=BG, no_reset=1))
        #             s = s.replace(end, col('', color, cnf, no_reset=1))

        def colorize_inline(is_inline, html, cnf):
            bg = cnf.background
            marks = (('<code>', '</code>', cnf.default_text['H2']),
                     ('<strong>', '</strong>', cnf.default_text['H2']),
                     ('<em>', '</em>', cnf.default_text['H3']))
            if is_inline:
                t = html.rsplit('<', 1)[0]
                for beg, end, color in marks:
                    t = t.replace(beg, col('', color, cnf, bg=bg, no_reset=1))
                    t = t.replace(end, col('', color, cnf, no_reset=1))
                t = unescape(t)
            else:
                t = el.text
            return t.strip()

        out = []
        el.text = el.text or ''

        done_inline, html = is_text_node(el)
        t = colorize_inline(done_inline, html, self.cnf)

        # ------------------------------------------------------- Text.Admon ..

        admon = ''
        pref = body_pref = ''
        if t.startswith('!!! '):
            for k in self.cnf.admons:
                if t[4:].startswith(k):
                    pref = body_pref = '┃ '
                    pref += (k.capitalize())
                    admon = k
                    t = t.split(k, 1)[1]

        # set the parent, e.g. nrs in ols:
        if el.get('pref'):
            # first line pref, like '-':
            pref = el.get('pref')
            # next line prefs:
            body_pref = ' ' * len(pref)
            el.set('pref', '')

        ind = self.cnf.left_indent * hir

        t = rewrap(el, t, ind, pref, self.term)

        # indent. can color the prefixes now, no more len checks:
        if admon:
            out.append('\n')
            pref = col(pref, self.cnf.admons['H3'], self.cnf)
            body_pref = col(body_pref, self.cnf.admons['H3'], self.cnf)

        if pref == self.cnf.icons['list_pref']:
            pref = col(pref, self.scheme['H4'], self.cnf)
        if pref.split('.', 1)[0].isdigit():
            pref = col(pref, self.scheme['H3'], self.cnf)

        t = ('\n' + ind + body_pref).join((t).splitlines())
        t = ind + pref + t

        # headers outer left: go sure.
        # actually... NO. commented out.
        # if is_header(el.tag):
        #    pref = ''

        # calling the class Tags functions (fallback on plain)
        plain_wrapper = lambda x, **kw: plain(x, self.cnf)
        tag_formatter = getattr(self.tags, el.tag, plain_wrapper)
        out.append(tag_formatter(t, hir=hir))

        if self.cnf.show_links:
            for l in 'src', 'href':
                if l in el.keys():
                    out[-1] + low('(%s) ' % el.attrib.get(l, ''), self.cnf)
                    # @WAT

        if admon:
            out.append('\n')

        return out

        # have children?
        #    nr for ols:
        if done_inline:
            return out

    def f_headers(self, el, hir):
        hl = int(el.tag[1:])  # hl <- 'H[0-9]>'
        ind = ' ' * (hl - 1)
        hir += hl
        return rewrap(el, el.text, ind, el.get('pref'), self.term)

    def formatter(self, el, hir=0, pref='', parent=None):

        if el.tag == 'hr':
            return self.f_hr(el, hir)

        if el.text or el.tag == 'p':
            return self.f_text(el, hir)

        if el.tag == 'table':
            return self.f_table(el, hir)

        if el.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'):
            return self.f_headers(el, hir)

        # UL | LI | OL 'list prefix style'
        #
        # UL | LI -> assign a list item prefix ('-' in config) as el.pref
        # OL      -> assign accumulated number of OL `nr`      as el.pref
        out = []
        nr = 0
        for c in el:
            if el.tag in ('ul', 'li'):
                c.set('pref', self.cnf.icons['list_pref'])
            elif el.tag is 'ol':
                nr += 1
                c.set('pref', str(nr) + ' ')
            # handle the ``` style unindented code blocks -> parsed as p:
            # is_code = None  # never used anywhere
            out.append(self.formatter(c, hir+1, parent=el))

        if el.tag == 'ul' or el.tag == 'ol' and not out[-1] == '\n':
            out.append('\n')

        return out

    def f_table(self, el, hir):
        # processed all here, in one sweep:
        # markdown ext gave us a xml tree from the ascii,
        # our part here is the cell formatting and into a
        # python nested list, then tabulate spits
        # out ascii again:

        # out = []

        # el = <table><thead>...</thead><tbody>...</tbody></table>
        #               `-> header        `-> body
        header, body = el
        joinfmt = lambda e: '\n'.join(self.formatter(e, 0))
        t = [[joinfmt(TD) for TD in TR.getchildren()]
             for sub in (header, body)
             for TR in sub.getchildren()]

        # good ansi handling:
        tbl = tabulate(t)

        def bordered(t):
            t[0] = t[-1] = low(t[0].replace('-', '─'), self.cnf)
            return t

        # do we have right room to indent it?
        # first line is seps, so no ansi esacapes foo:
        w = len(tbl.split('\n', 1)[0])
        cols = self.term.cols
        if w <= cols:
            left = self.cnf.left_indent
            ind = hir or (cols - w) // 2
            indl = [(ind * left) + l for l in bordered(tbl.splitlines())]
            # out.extend(indl)
            return indl
        else:
            # TABLE CUTTING WHEN NOT WIDTH FIT
            # oh snap, the table bigger than our screen. hmm.
            # hey lets split into vertical parts:
            # but len calcs are hart, since we are crammed with esc.
            # seqs.
            # -> get rid of them:
            tc = [[clean_ansi(cell) for cell in row] for row in t]
            table = tabulate(tc)
            rrrr = self.split_blocks(table, w, cols, part_fmter=bordered)
            # out.append(rrrr)
            return rrrr
        # return out

# Then tell markdown about it


class AnsiPrintExtension(Extension):

    def __init__(self, scheme, term, cnf):
        self.scheme = scheme
        self.term = term
        self.cnf = cnf

    def extendMarkdown(self, md, md_globals):
        ansi_print_ext = AnsiPrinter(md, self.scheme, self.term, self.cnf)
        md.treeprocessors.add('ansi_print_ext', ansi_print_ext, '>inline')
