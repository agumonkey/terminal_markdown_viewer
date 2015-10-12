from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from vendor.tabulate import tabulate

from .base import col, low, plain, clean_ansi, rewrap
from .tags import Tags, is_text_node

from mdv.core.helpers import unescape, flatten, Not, Eq

# ---------------------------------------------------- Create the treeprocessor


class AnsiPrinter(Treeprocessor):

    def __init__(self, md, scheme, term, cnf):
        super().__init__(md)
        self.scheme = scheme
        self.term = term
        self.cnf = cnf

        # a little preemptive checking for the future
        assert self.cnf.markers
        assert self.cnf.show_links is None
        assert self.cnf.left_indent
        assert self.cnf.admons
        assert self.cnf.admons['H3']
        assert self.cnf.icons
        assert self.cnf.icons['list_pref']

    def run(self, doc):
        out = self.formatter(doc)

        # formatter has issues
        #  - nested lists
        #  - empty (None) results
        # @TOFIX
        out = '\n'.join(filter(Not(Eq(None)), flatten(out)))
        self.markdown.ansi = out

    def formatter(self, el, hir=0, pref='', parent=None):

        def is_header(tag):
            return tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')

        M = self.cnf.markers
        tags = Tags(self.scheme, self.cnf)
        out = []
        done_inline = 0

# ----------------------------------------------------------------------- HR --

        if el.tag == 'hr':
            return out.append(tags.hr('', hir=hir))

# -------------------------------------------------------------------- P | Text

        if el.text or el.tag == 'p':
            el.text = el.text or ''
            # <a attributes>foo... -> we want "foo....". Is it a sub
            # tag or inline text?
            done_inline, html = is_text_node(el)

            if done_inline:
                t = html.rsplit('<', 1)[0]
                t = t.replace('<code>', M['code_start']) \
                     .replace('</code>', M['code_end'])
                t = t.replace('<strong>', M['strong_start']) \
                     .replace('</strong>', M['strong_end'])
                t = t.replace('<em>', M['em_start']) \
                     .replace('</em>', M['em_end'])
                t = unescape(t)
            else:
                t = el.text

            t = t.strip()
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
            if is_header(el.tag):
                # header level:
                hl = int(el.tag[1:])
                ind = ' ' * (hl - 1)
                hir += hl

            t = rewrap(el, t, ind, pref, self.term)

# --------------------------------------------------------------- Text.Admon ..

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
            tag_formatter = getattr(tags, el.tag, plain_wrapper)
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

# -------------------------------------------------------------------- Table ..

        if el.tag == 'table':
            # processed all here, in one sweep:
            # markdown ext gave us a xml tree from the ascii,
            # our part here is the cell formatting and into a
            # python nested list, then tabulate spits
            # out ascii again:

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
                ind = (cols - w) / 2 or hir
                indl = [(ind * left) + l for l in bordered(tbl.splitlines())]
                out.extend(indl)
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
                out.append(rrrr)
            return out

        # UL | LI | OL 'list prefix style'
        #
        # UL | LI -> assign a list item prefix ('-' in config) as el.pref
        # OL      -> assign accumulated number of OL `nr`      as el.pref
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


# Then tell markdown about it


class AnsiPrintExtension(Extension):

    def __init__(self, scheme, term, cnf):
        self.scheme = scheme
        self.term = term
        self.cnf = cnf

    def extendMarkdown(self, md, md_globals):
        ansi_print_ext = AnsiPrinter(md, self.scheme, self.term, self.cnf)
        md.treeprocessors.add('ansi_print_ext', ansi_print_ext, '>inline')
