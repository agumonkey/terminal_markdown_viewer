import term

TERM = term.Term(40, 100)


def test_0():
    assert TERM, 'instance is ok'
    assert TERM.rows == 80 and TERM.cols == 200, 'default size MUST be 80x200'
    # print(TERM)
    # print(TERM.refresh())
    REFRESHED_TERM = TERM.refresh()
    assert TERM == REFRESHED_TERM, 'dunno how to mock a terminal to check size'
