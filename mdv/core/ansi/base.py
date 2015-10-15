import re


def col(s, c, cnf, bg=0, no_reset=0):
    """
    print col('foo', 124) -> red 'foo' on the terminal
    c = color, s the value to colorize """
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
