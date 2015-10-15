#!/usr/bin/env python
# coding: utf-8

"""
Usage:
    mdv [-t THEME] [-T C_THEME] [-x] [-l] [-L] [-c COLS] [-f FROM] [-m] [-M DIR] [-H] [-A] [MDFILE] [-V] [-VV]

Options:
    MDFILE    : Path to markdown file
    -t THEME  : Key within the color ansi_table.json. 'random' accepted.
    -T C_THEME: Theme for cod heighlight. If not set: Use THEME.
    -l        : Light background (not yet supported)
    -L        : Display links
    -x        : Do not try guess code lexer (guessing is a bit slow)
    -f FROM   : Display FROM given substring of the file.
    -m        : Monitor file for changes and redisplay FROM given substring
    -M DIR    : Monitor directory for markdown file changes
    -c COLS   : Fix columns to this (default: your terminal width)
    -A        : Strip all ansi (no colors then)
    -H        : Print html version
    -V        : Verbose mode
    -VV       : Debug mode

Notes:

    We use stty tool to derive terminal size.

    To use mdv.py as lib:
        Call the main function with markdown string at hand to get a
        formatted one back.

    FROM:
        FROM may contain max lines to display, seperated by colon.
        Example:
        -f 'Some Head:10' -> displays 10 lines after 'Some Head'
        If the substring is not found we set it to the *first* charactor of the
        file - resulting in output from the top (if you terminal height can be
        derived correctly through the stty cmd).

    File Monitor:
        If FROM is not found we display the whole file.

    Directory Monitor:
        We check only text file changes, monitoring their size.

        By default .md, .mdown, .markdown files are checked but you can change
        like -M 'mydir:py,c,md,' where the last empty substrings makes mdv also
        monitor any file w/o extension (like 'README').

        Running actions on changes:
        If you append to -M a '::<cmd>' we run the command on any change
        detected (sync, in foreground).
        The command can contain placeholders:
            _fp_    : Will be replaced with filepath
            _raw_   : Will be replaced with the base64 encoded raw content
                      of the file
            _pretty_: Will be replaced with the base64 encoded prettyfied output

        Like: mdv -M './mydocs:py,md::open "_fp_"'  which calls the open
        command with argument the path to the changed file.

    Theme rollers:
        mdv -T all:  All available code styles on the given file.
        mdv -t all:  All available md   styles on the given file.
                    If file is not given we use a short sample file.

        So to see all code hilite variations with a given theme:
            Say C_THEME = all and fix THEME
        Setting both to all will probably spin your beach ball, at least on OSX.

    Lastly: Using docopt, so this docstring is building the options checker.
    -> That's why this app can't currently use itself for showing the docu.
    Have to find a way to trick docopt to parse md ;-) -__-;

"""

from __future__ import print_function  # python 2 compatibility ...

import re
import sys
import logging
import itertools as it

import markdown
import markdown.util
from markdown.extensions import fenced_code
from markdown.extensions.tables import TableExtension

# code analysis for hilite:
try:
    from pygments import token
    have_pygments = True
except ImportError:
    have_pygments = False

from vendor.docopt import docopt

from mdv.core.version import VERSION
from mdv.core.helpers import j, unescape

from mdv.core.sample import make_sample
from mdv.core.term import Term
from mdv.core.theme import Themes
from mdv.core.code_formatter import CodeFormatter
from mdv.core.ansi.base import col, clean_ansi
from mdv.core.ansi.layout import set_hr_widths
from mdv.core.ansi.printers import AnsiPrintExtension

import config as cnf

# -------------------------------------------------------------------- Logging


def Logger():
    logging.getLogger().setLevel(logging.NOTSET)
    mdv = logging.getLogger('MDV')
    sh = logging.StreamHandler(stream=sys.stderr)
    sh.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    mdv.addHandler(sh)
    mdv.setLevel(logging.INFO)
    return mdv

mdv = Logger()


# ---------------------------------------------------------------------- Main

# docopt
#     md <- file | sample
#     term
#     theme(term)
#     back <- backend(term, theme)
# |>  dom <- Parse(md)
# |>  Render(dom, back)


def main(md=None, filename=None, cols=None, theme=None, c_theme=None, bg=None,
        c_no_guess=None, display_links=None, from_txt=None, do_html=None,
        no_colors=None, **kw):
    """ md is markdown string. alternatively we use filename and read """

# --------------------------------------------------------------------- Loading

    if not md:
        if not filename:
            mdv.info('Using generated markdown sample')
            md = make_sample(cnf.admons)
        else:
            with open(filename) as f:
                md = f.read()

    # enforce desire column number from docopt args if present
    term = Term(cols) if cols else Term()

    mdv.debug(term)
    assert md and term

# --------------------------------------------------------------------- Theming

    themer = Themes(j('.', 'themes'), cnf.preconfigured)

    # if bg and bg == 'light':
    #     # not in use rite now:
    #     global background, color
    #     background = BGL
    #     color = T

    mdv.info('Theme selection: {theme}'.format(theme=theme))
    scheme = themer.get_theme(theme_selection=theme)

    if not c_theme:
        c_theme = theme or 'default'

    if c_theme == 'None':
        c_theme = None

    if c_theme:
        c_scheme = themer.get_theme(c_theme)

    if c_scheme or cnf.c_guess:
        if not have_pygments:
            err = 'No pygments, can not analyze code for hilite'
            mdv.info(col(err, cnf.default_text['R']))

    mdv.debug(themer)
    mdv.debug('current scheme: {scheme}'.format(scheme=scheme))

    assert themer and scheme and c_scheme


# --------------------------------------------------------------------- Parsing

    # Create an instance of the Markdown class with the new extension
    MD = markdown.Markdown(extensions=[AnsiPrintExtension(scheme, term, cnf),
                                       TableExtension(),
                                       fenced_code.FencedCodeExtension()])

    mdv.debug('markdown.extensions: {x}'.format(x=dir(MD)))
    mdv.debug('markdown.treeprocessors: {x}'.format(x=MD.treeprocessors))

    assert md

# ------------------------------------------------------------------- ANSI PASS

    the_html = MD.convert(md)

    mdv.debug('[html]')
    mdv.debug(the_html)

    if do_html:
        return the_html

    # who wants html, here is our result:
    try:
        ansi = MD.ansi
    except Exception as exn:

        # mdv.warn('[markdown.ansi] {exn}'.format(exn=exn))
        mdv.debug('[markdown.ansi] {exn} {md}'.format(exn=exn, md=dir(MD)))

        if do_html:
            # can this happen? At least show:
            mdv.debug("we have markdown result but no ansi.")
            mdv.debug(the_html)
        else:
            ansi = 'n.a. (no parsing result)'

    mdv.debug('[ansi]')
    mdv.debug(ansi)

    assert ansi

# -------------------------------------------------------------- Code Formatter

    # The RAW html within source, incl. fenced code blocks:
    # phs are numbered like this in the md, we replace back:
    stash = MD.htmlStash
    mdv.debug('md.stash.rawHtmlBlocks: {x}'.format(x=len(stash.rawHtmlBlocks)))

    CF = CodeFormatter(cnf, themer)

    for num, block in enumerate(stash.rawHtmlBlocks, 0):
        raw = unescape(block[0])  # @WAT
        # thanks to: https://regex101.com/r/jZ7rZ1/1
        rx = r'<pre><code +class="(?P<lang>[^"]+)" *>(?P<code>.*)</code>.*'
        m = re.match(rx, raw, re.S)
        mdv.debug('%s %s %s' % (raw, rx, m.groupdict() if m else None))

        code = m.groupdict().get('code')
        lang = m.groupdict().get('lang')
        colored_code = CF.code(code, from_fenced_block=1, lang=lang)

        mdv.debug('[code.format] %s %s' % (num, markdown.util.HTML_PLACEHOLDER))
        mdv.debug('[code.format][ansi.pre] %s' % ansi[250:300])

        assert colored_code
        ansi = ansi.replace(markdown.util.HTML_PLACEHOLDER % num, colored_code)

    # don't want these: gone through the extension now:
    # ansi = ansi.replace('```', '')

# ------------------------------------------------------------------------ Seek

    # seek :: md.ansi -> string-to-match -> lines-after-match -> md.ansi'

    def seek(md, position):
        '''text -> (match:str, after:int) -> new text
        seek for `match` in text, return md lines `after` that point
        '''
        def parse(position):
            '''@TOFIX, avoid parsing by using two docopt flags'''
            fmt = '^(?P<match>[^:]+):(?P<lines>.*)$'
            m = re.match(fmt, position)
            if m:
                d = m.groupdict()
                match = d.get('match')
                lines = int(d.get('lines'))
                return True, match, lines
            else:
                err = 'position format must be `<string>:<lines>`, not `{pos}`'
                mdv.warn(err.format(pos=position))
                return False, None, None

        check, match, after = parse(position)
        if not check:
            return md
        elif match in md:
            #    dropwhile not(in(match)) md
            # |> take after
            lines = md.splitlines()
            lines = it.dropwhile(lambda l: match not in l, lines)
            lines = list(lines)[:after]
            return '\n'.join(lines)
        else:
            lines = md.splitlines()[:after]
            return '\n'.join(lines)

    mdv.info('seeking from ' + (from_txt if from_txt else 'start'))
    ansi = seek(ansi, from_txt) if from_txt else ansi

# ------------------------------------------------------------------------ Wat?

    ansi = set_hr_widths(ansi, term, cnf.icons, cnf.markers) + '\n'
    # @TODO, try to avoid formatting and then unformatting u_u;
    if no_colors:
        return clean_ansi(ansi)

    return ansi + '\n'


def demo(md, filename, theme, c_theme, themer, term, cnf):
    ''' I guess this is a way to test all Markdown theme or Code theme'''
    # style rolers requested?
    if c_theme == 'all' or theme == 'all':
        for k, v in themer.themes().items():
            if not filename:
                yl = 'You like *%s*, *%s*?' % (k, v['name'])
                md = md.replace(cnf.you_like, yl)
            mdv.info(col('%s%s%s' % ('\n\n', '=' * term.cols, '\n'), k['L']))
            # should really create an iterator here:
            if theme == 'all':
                args['theme'] = k
            else:
                args['c_theme'] = k
            print(main(**args))
        return ''

if __name__ == '__main__':

    if VERSION['MAJOR'] == '2':
        reload(sys)
        sys.setdefaultencoding("utf-8")
    # no? see http://stackoverflow.com/a/29832646/4583360 ...

    args = docopt(__doc__, version='mdv v0.1')
    # if args.get('-m'):
    #     monitor(args)
    # if args.get('-M'):
    #     monitor_dir(args)
    # else:
    #     print(run_args(args))

    # @TOFIX, I still get logging levels backward it seems.
    level = {
        0: logging.INFO,
        1: logging.WARN,
        2: logging.DEBUG,
        3: logging.CRITICAL
    }

    mdv.setLevel(level.get(args.get('-V'), logging.INFO))
    mdv.debug('[docopts] {args}'.format(args=args))
    kw = {
        'filename': args.get('MDFILE'),
        'theme': args.get('-t', 'random'),
        'cols': args.get('-c'),
        'from_txt': args.get('-f'),
        'c_theme': args.get('-T'),
        'c_no_guess': args.get('-x'),
        'do_html': args.get('-H'),
        'no_colors': args.get('-A'),
        'display_links': args.get('-L')
    }
    mdv.debug('[docopt] -> named dict: {kw}'.format(kw=kw))

    formatted = main(**kw)
    print(formatted)

    mdv.info('Done.')
