# code analysis for hilite:
try:
    from pygments import lex
    from pygments.lexers import get_lexer_by_name
    from pygments.lexers import guess_lexer as pyg_guess_lexer
    have_pygments = True
except ImportError:
    have_pygments = False

from mdv.core.ansi.base import col, low


class CodeFormatter:

    def __init__(self, cnf):
        self.cnf = cnf

    def style_ansi(self, raw_code, lang=None):
        """ actual code hilite """

        # lexer = 0
        # if lang:
        #     try:
        #         lexer = get_lexer_by_name(lang)
        #     except ValueError:
        #         print(col(self.cnf.default_text['R'],
        #                   'Lexer for %s not found' % lang))

        # try:
        #     if self.cnf.guess_lexer:
        #         lexer = pyg_guess_lexer(raw_code)
        # except:
        #     lexer = get_lexer_by_name(self.cnf.def_lexer)

        try:
            if lang:
                lexer = get_lexer_by_name(lang)
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
        cod = []
        for t, v in tokens:
            if not v:
                continue
            _col = self.cnf['code_hl_tokens'].get(t)
            if _col:
                cod.append(col(v, _col))
            else:
                cod.append(v)
        return ''.join(cod)

    def code(self, _, s, from_fenced_block=None, **kw):
        """ md code AND ``` style fenced raw code ends here"""
        lang = kw.get('lang')

        raw_code = s
        if have_pygments:
            s = self.style_ansi(raw_code, lang=lang)

        # outest hir is 2, use it for fenced:
        ind = ' ' * kw.get('hir', 2)
        # if from_fenced_block: ... WE treat equal.

        # shift to the far left, no matter the indent (screenspace matters):
        firstl = s.split('\n')[0]
        del_spaces = ' ' * (len(firstl) - len(firstl.lstrip()))
        s = ('\n' + s).replace('\n%s' % del_spaces, '\n')[1:]

        # we want an indent of one and low vis prefix. this does it:
        code_lines = ('\n' + s).splitlines()
        prefix = ('\n%s%s %s' % (ind, low(self.cnf.code_pref),
                                 col('', self.cnf.default_text['C'],
                                     no_reset=1)))
        code = prefix.join(code_lines)
        return code + '\n' + self.cnf.reset_col
