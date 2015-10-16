import re
import logging

from markdown.util import HTML_PLACEHOLDER

# code analysis for hilite:
try:
    from pygments import lex
    from pygments import token
    from pygments.lexers import get_lexer_by_name
    from pygments.lexers import guess_lexer as pyg_guess_lexer
    have_pygments = True
except ImportError:
    have_pygments = False

from mdv.core.ansi.base import col, low
from mdv.core.helpers import unescape, remove_left_indent

mdv = logging.getLogger("MDV")


class CodeFormatter:

    def __init__(self, cnf, themer):
        self.cnf = cnf
        self.themer = themer

        assert self.cnf
        assert self.themer

        mdv.debug('code formatter loaded')

    def determine_lexer(self, text, lang):
        '''ask pygments to find a lexer for lang if present
        or to guess by looking at the text
        or use a configured default lexer
        '''
        try:
            if lang:
                lexer = get_lexer_by_name(lang)
            # @TOFIX, need to pass docopt c_no_guess
            elif self.cnf.guess_lexer:
                lexer = pyg_guess_lexer(text)
        except ValueError:
            red = self.cnf.default_text['R']
            err = 'Lexer for %s not found' % lang
            print(col(red, err))
        finally:
            lexer = get_lexer_by_name(self.cnf.def_lexer)
        assert lexer, "Need a pygments lexer."
        return lexer

    def ansify(self, code, lexer, colors):
        """colorize the stream of tokens from lexer(code) with passed colors"""
        tokens = lex(code, lexer)
        return ''.join(col(s, colors.get(t), self.cnf) for t, s in tokens if s)

    def prefix(self, indent):
        '''we want an indent of one and low ico prefix. this does it'''
        ico = low(self.cnf.icons['code_pref'], self.cnf)
        beg = col('', self.cnf.default_text['C'], self.cnf, no_reset=1)
        return '\n{ind}{ico} {beg}'.format(ind=indent, ico=ico, beg=beg)

    def reformat1(self, code, from_fenced_block=None, **kw):
        '''reformat logic for a single code block'''
        lang = kw.get('lang')
        hir = kw.get('hir', 2)  # outest hir is 2
        lexer = self.determine_lexer(code, lang)
        hl = self.themer.hl(token)

        assert hl, "Need hilite map."

        code = self.ansify(code, lexer, hl) if have_pygments else code
        code = remove_left_indent(code)
        code = self.prefix(' ' * hir).join(code.splitlines())
        fmt = '''
        {code}
        {reset}
        '''
        mdv.debug('code formatting done')
        return fmt.format(code=code, reset=self.cnf.reset_col)

    def reformat(self, md):
        '''reformat all code blocks'''

        # The RAW html within source, incl. fenced code blocks:
        # phs are numbered like this in the md, we replace back:
        blocks = md.htmlStash.rawHtmlBlocks
        mdv.debug('md.stash.rawHtmlBlocks: {x}'.format(x=len(blocks)))

        # thanks to: https://regex101.com/r/jZ7rZ1/1
        rx = r'<pre><code +class="(?P<lang>[^"]+)" *>(?P<code>.*)</code>.*'
        rx = re.compile(rx, re.S)

        source = md.ansi
        for num, (block, flag) in enumerate(blocks, 0):
            raw = unescape(block)
            m = re.match(rx, raw)
            mdv.debug('%s %s %s' % (raw, rx, m.groupdict() if m else None))
            code = m.groupdict().get('code')
            lang = m.groupdict().get('lang')
            colored_code = self.reformat1(code, from_fenced_block=1, lang=lang)
            mdv.debug('[code.format] %s %s' % (num, HTML_PLACEHOLDER))
            mdv.debug('[code.format][ansi.pre] %s' % source[250:300])
            assert colored_code
            source = source.replace(HTML_PLACEHOLDER % num, colored_code)
        return source
