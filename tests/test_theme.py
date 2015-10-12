import config as cnf
from mdv.core.helpers import j
from mdv.core.theme import Themes

te = Themes(j('.', 'themes'), cnf.preconfigured)
print('themer', te)
print('random theme', te.get_theme(theme_selection='random'))
print('default theme', te.get_theme(theme_selection='default'))
