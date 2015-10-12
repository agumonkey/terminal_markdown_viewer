import config as cnf
from mdv.core.term import Term
from mdv.core.theme import Themes

import markdown
from mdv.core.ansi.printers import AnsiPrintExtension


fixtures = {
    'header': '''# Markdown Header''',
    'headers': '''# Markdown Header
    ## Markdown SubHeader'''
}


def before():
    term = Term()
    themer = Themes('./themes', cnf.preconfigured)
    return term, themer


def test_AnsiPrinter_0():
    term, themer = before()
    ansi = AnsiPrintExtension(themer.get_theme(), term, cnf)
    md = markdown.Markdown(extensions=[ansi])
    texts = {k: md.convert(v) for k, v in fixtures.items()}
    print(texts)
    assert texts, 'dummy test'
    return texts
