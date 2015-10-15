import re


def col(text, color, cnf, bg=0, no_reset=0):
    """
    print col('foo', 124) -> red 'foo' on the terminal
    c = color, s the value to colorize
    """
    reset = '' if no_reset else cnf.reset_col
    s = '\033[38;5;{color}m{text}{reset}' \
        .format(color=color, text=text, reset=reset)

    # if bg:
    #     pass
    # s = col_bg(bg) + s

    return s


def col_bg(c):
    """ colorize background """
    return '\033[48;5;{bg}m'.format(bg=c)


def low(s, cnf, **kw):
    # shorthand
    return col(s, cnf.default_text['L'], cnf)


def plain(s, cnf, **kw):
    # when a tag is not found:
    return col(s, cnf.default_text['T'], cnf)


# ----------------------------------------------------- Text Termcols Adaptions

ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')


def clean_ansi(s):
    return ANSI_ESCAPE.sub('', s)
