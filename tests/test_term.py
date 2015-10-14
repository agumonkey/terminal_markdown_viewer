from mdv.core.term import Term

TERM = Term()


def test_0():
    assert TERM, 'instance is ok'
    assert TERM.cols == 80 and TERM.rows == 200, \
        'default size MUST be 80x200, not %s' % s

    REFRESHED_TERM = TERM.refresh()

    assert TERM == REFRESHED_TERM, 'dunno how to mock a terminal to check size'

    import os
    # ensure that refreshed terminal
    # has the same size as the current terminal
    cr, cc = list(map(int, os.popen('stty size').read().split()))
    tr, tc = TERM.dimensions()

    assert cr == tr
    assert cc == tc
