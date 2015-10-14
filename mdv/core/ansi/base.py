import re


def col(s, c, cnf, bg=0, no_reset=0):
    """
    print col('foo', 124) -> red 'foo' on the terminal
    c = color, s the value to colorize """

    M = cnf.markers
    marks = ((M['code_start'], M['code_end'], cnf.default_text['H2']),
             (M['strong_start'], M['strong_end'], cnf.default_text['H2']),
             (M['em_start'], M['em_end'], cnf.default_text['H3']))

    DEFAULT_BG = cnf.background

    for _strt, _end, _col in marks:
        if _strt in s:
            # inline code:
            s = s.replace(_strt, col('', _col, cnf, bg=DEFAULT_BG, no_reset=1))
            s = s.replace(_end, col('', c, cnf, no_reset=1))

    s = '\033[38;5;%sm%s%s' % (c, s, '' if no_reset else cnf.reset_col)
    if bg:
        pass
    # s = col_bg(bg) + s
    return s


# def col_bg(c):
#     """ colorize background """
#     return '\033[48;5;%sm' % c


def low(s, cnf, **kw):
    # shorthand
    return col(s, cnf.default_text['L'], cnf)


def plain(s, cnf, **kw):
    # when a tag is not found:
    return col(s, cnf.default_text['T'], cnf)


# ----------------------------------------------------- Text Termcols Adaptions


def clean_ansi(s):
    ansi_escape = re.compile(r'\x1b[^m]*m')
    # if someone does not want the color foo:
    return ansi_escape.sub('', s)
