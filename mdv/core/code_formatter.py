import logging

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
from mdv.core.ansi.helpers import remove_left_indent

mdv = logging.getLogger("MDV")


class CodeFormatter:

    def __init__(self, cnf, themer):
        self.cnf = cnf
        self.themer = themer
        mdv.debug('code formatter loaded')

    def style_ansi(self, raw_code, lang=None):
        """ actual code hilite """

        try:
            if lang:
                lexer = get_lexer_by_name(lang)
            # @TOFIX, need to pass docopt c_no_guess
            elif self.cnf.guess_lexer:
                lexer = pyg_guess_lexer(raw_code)
        except ValueError:
            red = self.cnf.default_text['R']
            err = 'Lexer for %s not found' % lang
            print(col(red, err))
        finally:
            lexer = get_lexer_by_name(self.cnf.def_lexer)

        assert lexer, "Need a pygments lexer."

        tokens = lex(raw_code, lexer)
        hl = self.themer.hl(token)

        assert hl, "Need hilite map."

        return ''.join([col(s, hl.get(t)) for t, s in tokens if s])

    def code(self, s, from_fenced_block=None, **kw):
        """ md code AND ``` style fenced raw code ends here"""
        lang = kw.get('lang')
        hir = kw.get('hir', 2)  # outest hir is 2

        s = self.style_ansi(s, lang=lang) if have_pygments else s
        s = remove_left_indent(s)

        # we want an indent of one and low vis prefix. this does it:
        vis = low(self.cnf.icons['code_pref'], self.cnf)
        pre = col('', self.cnf.default_text['C'], self.cnf, no_reset=1)
        prefix = ('\n{ind}{vis} {pre}'.format(ind=' ' * hir, vis=vis, pre=pre))
        code = prefix.join(s.splitlines())
        fmt = '''
        {code}
        {reset}
        '''
        mdv.debug('code formatting done')
        return fmt.format(code=code, reset=self.cnf.reset_col)
