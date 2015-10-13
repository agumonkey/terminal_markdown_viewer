from mdv.core.helpers import derive

# --------------------------------------------------------------------- Schemes

icons = {
    "hr_ends": '◈',
    "hr_sep": '─',
    "txt_block_cut": '✂',
    "code_pref": '░ ',
    "list_pref": '- ',
}

markers = {
    'code_start': '\x07',
    'code_end': '\x08',
    'strong_start': '\x09',
    'strong_end': '\x10',
    'em_start': '\x11',
    'em_end': '\x12',
    'punctuationmark': '\x13',
    'fenced_codemark': '\x14',
    'hr_marker': '\x15',
}

# ansi cols (default):
# R: Red (warnings), L: low visi, BG: background, BGL: background light, C=code
# H1 - H5 = the theme, the numbers are the ansi color codes:

default_text = {
    "H1": 231,
    "H2": 153,
    "H3": 117,
    "H4": 109,
    "H5": 65,
    "R": 124,
    "L": 59,
    "BG": 16,
    "BGL": 188,
    "T": 188,
    "TL": 59,
    "C": 102,
}

# also global. but not in use, BG handling can get pretty involved, to do with
# taste, since we don't know the term backg....:
background = default_text['BG']

# normal text color:
color = default_text['T']

reset_col = '\033[0m'

# Code (C is fallback if we have no lexer). Default: Same theme:

default_code = derive(default_text, {
    "CH5": 'H5',
    "CH1": 'H1',
    "CH2": 'H2',
    "CH3": 'H3',
    "CH4": 'H4',
})

code_hl = derive(default_code, {
    "Keyword": 'CH3',
    "Name": 'CH1',
    "Comment": 'L',
    "String": 'CH4',
    "Error": 'R',
    "Number": 'CH4',
    "Operator": 'CH5',
    "Generic": 'CH2'
}, inclusive=False)

admons = derive(default_text, {
    'note': 'H3',
    'warning': 'R',
    'attention': 'H1',
    'hint': 'H4',
    'summary': 'H1',
    'hint': 'H4',
    'question': 'H5',
    'danger': 'R',
    'caution': 'H2'
})

preconfigured = {
    'default_text': default_text,
    'default_code': default_code,
    'code_hl': code_hl,
    'admons': admons
}

# ----------------------------------------------------------------------- Rest

def_lexer = 'python'
c_guess = True
guess_lexer = True

# hierarchical indentation by:
left_indent = '  '

show_links = None

# dir monitor recursion max:
mon_max_files = 1000

# ------------------------------------------------------------------ End Config
