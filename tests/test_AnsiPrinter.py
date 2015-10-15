import sys
import logging

import config as cnf
from mdv.core.term import Term
from mdv.core.theme import Themes

import markdown
from markdown.extensions import fenced_code
from markdown.extensions.tables import TableExtension

from mdv.core.ansi.printers import AnsiPrintExtension

mdv = logging.getLogger('MDV')

fixtures = {
    'header': '''# Markdown Header''',
    'headers': '''# Markdown Header
    ## Markdown SubHeader''',
    'zzzzzzzzz': '''# Markdown Header
    ## Markdown SubHeader
     - item 1
     - item 2

    ## Code
    ```python
      # (define id (lambda (x) x))
      def id(x):
          return x
    ```
'''
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


def test_AnsiPrinter_1():
    mdv.setLevel(0)
    term, themer = before()
    ansi = AnsiPrintExtension(themer.get_theme(), term, cnf)
    md = markdown.Markdown(extensions=[ansi,
                                       TableExtension(),
                                       fenced_code.FencedCodeExtension()])
    texts = {k: md.convert(v) for k, v in fixtures.items()}
    print(md.ansi, file=sys.stderr)
    print(texts, file=sys.stderr)
    assert texts, 'dummy test'
    return texts


def test_table():
    '''
    - in-table wrapping
    - width too long for term (not fit)
    '''
    pass


def test_ul():
    '''
    - prefix
    - rewrap
    '''
    pass


def test_ol():
    '''
    - number prefix
    - rewrap
    '''
    pass


def test_header1():
    pass


def test_header2():
    pass


def test_indent():
    pass
