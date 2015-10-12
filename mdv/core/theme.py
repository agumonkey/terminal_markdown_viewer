import os
from json import loads
from random import choice

from mdv.core.helpers import j


class Themes:

    DB = 'ansi_color_schemes.json'

    def __init__(self, themes_dir, preconfigured):
        self.preconfigured = preconfigured
        self.themes_dir = themes_dir
        self.db = j(self.themes_dir, Themes.DB)
        self._default = 'default'

        def load_db():
            with open(self.db) as f:
                return loads(f.read())

        self._themes = load_db() or {}

    def __str__(self):
        return '<Themes {db}({count}):{default}>'.format(
            db=self.db,
            count=len(self._themes.items()),
            default=self._default)

    def __repr__(self):
        return self.__str__()

    # Interface

    def themes(self):
        ''' -> [THEMES]'''
        return self._themes

    def hl(self, token):
        '''
        hl :: cnf.code_hl -> pygments.token -> [(pygments.token, COLORS)]

        Turns the preconfigured code color scheme (str -> int) map
        into a (pygments.token -> int) map
        '''
        hl = self.preconfigured['code_hl']
        return {getattr(token, k): col for k, col in hl.items()}

    def get_theme(self, theme_selection=None):
        default_scheme = self.themes()['default']

        env_selection = os.environ.get('AXC_THEME', 'random')
        theme_selection = theme_selection or env_selection
        if theme_selection is 'default':
            scheme = default_scheme
        elif theme_selection is 'random':
            scheme = self.themes()[choice(list(self.themes().keys()))]
        else:  # theme_selection is a scheme name ?
            scheme = self.themes().get(theme_selection, default_scheme)

        assert scheme is not None
        assert len(scheme['colors']) is 5, ">>> %s" % scheme['colors']

        names = ["H1", "H2", "H3", "H4", "H5"]
        s = dict(zip(names, scheme['colors']))
        d = self.preconfigured['default_text'].copy()
        d.update(s)
        return d
