import re


def col(s, c, cnf, bg=0, no_reset=0):
    """
    print col('foo', 124) -> red 'foo' on the terminal
    c = color, s the value to colorize """

    reset = cnf.reset_col
    if no_reset:
        reset = ''

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

    s = '\033[38;5;%sm%s%s' % (c, s, reset)
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


def set_hr_widths(result, term, icons, markers):
    """
    We want the hrs indented by hierarchy...
    A bit 2 much effort to calc, maybe just fixed with 10
    style seps would have been enough visually:
    ◈────────────◈
    """
    HR = markers['hr_marker']
    SEP = icons['hr_sep']
    # set all hrs to max width of text:
    mw = 0
    hrs = []
    if HR not in result:
        return result
    for line in result.splitlines():
        if HR in line:
            hrs.append(line)
            continue
        if len(line) < mw:
            continue
        l = len(clean_ansi(line))
        if l > mw:
            mw = l
    for hr in hrs:
        # pos of hr marker is indent, derives full width:
        # (more indent = less '-'):
        hcl = clean_ansi(hr)
        ind = len(hcl) - len(hcl.split(HR, 1)[1]) - 1
        w = min(term.cols, mw) - 2 * ind
        hrf = hr.replace(HR, SEP * w)
        result = result.replace(hr, hrf)
    return result


def split_blocks(text_block, w, cols, icons, scheme, part_fmter=None):
    """ splits while multiline blocks vertically (for large tables) """
    ts = []
    for line in text_block.splitlines():
        parts = []
        # make equal len:
        line = line.ljust(w, ' ')
        # first part full width, others a bit indented:
        parts.append(line[:cols])
        scols = cols-2

        # the txt_block_cut in low makes the whole secondary tables
        # low. which i find a feature:
        # if you don't want it remove the col(.., L)

        def F(i, l):
            icon = icons['txt_block_cut']
            color = scheme['L']
            r = ' ' + col(icon, color, no_reset=1) + line[i:i+scols]
            return r

        parts.extend([F(i, line) for i in range(cols, len(line), scols)])
        ts.append(parts)

    blocks = []
    for block_part_nr in range(len(ts[0])):
        tpart = []
        for lines_block in ts:
            tpart.append(lines_block[block_part_nr])
        if part_fmter:
            part_fmter(tpart)
        tpart[1] = col(tpart[1], scheme['H3'])
        blocks.append('\n'.join(tpart))
    t = '\n'.join(blocks)
    return('\n%s\n' % t)


def rewrap(el, t, ind, pref, term):
    """ Reasonably smart rewrapping checking punctuations """
    cols = term.cols - len(ind + pref)
    if el.tag == 'code' or len(t) <= cols:
        return t
    # wrapping:
    # we want to keep existing linebreaks after punctuation
    # marks. the others we rewrap:

    puncs = ',', '.', '?', '!', '-', ':'
    parts = []
    origp = t.splitlines()
    if len(origp) > 1:
        pos = -1
        while pos < len(origp) - 1:
            pos += 1
            # last char punctuation?
            if origp[pos][-1] not in puncs and \
                    not pos == len(origp) - 1:
                # concat:
                parts.append(origp[pos].strip() + ' ' +
                             origp[pos+1].strip())
                pos += 1
            else:
                parts.append(origp[pos].strip())
        t = '\n'.join(parts)
    # having only the linebreaks with puncs before we rewrap
    # now:
    parts = []
    for part in t.splitlines():
        parts.extend([part[i:i+cols]
                      for i in range(0, len(part), cols)])
    # last remove leading ' ' (if '\n' came just before):
    t = []
    for p in parts:
        t.append(p.strip())
    return '\n'.join(t)
