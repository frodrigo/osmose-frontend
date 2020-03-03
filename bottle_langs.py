'''
'''

__author__ = "Frederic Rodrigo"
__version__ = '0.1'
__license__ = 'MIT'

### CUT HERE (see setup.py)

from bottle import request, response
import gettext, inspect


class LangsPlugin(object):
    '''
    '''

    name = 'langs'
    api  = 2

    def __init__(self, allowed_languages, keyword='langs'):
        self.allowed_languages = allowed_languages
        self.keyword = keyword
        self.cache = {}

    def parse_accept_language(self, langs):
        if langs and 'auto' in langs:
            langs = request.get_header('Accept-Language')
        if not langs:
            langs = 'en'
        langs = map(lambda lang: lang.split(';')[0].strip(), langs.split(','))
        langs += list(map(lambda lang: lang.split('_')[0].lower(), langs))
        return langs

    def get_language(self):
        langs = request.params.get('langs')
        if langs:
            langs = self.parse_accept_language(langs)

        if not langs and len(request.script_name) > 3:
            lang = request.script_name[-3:-1]
            if lang in self.allowed_languages:
                langs = [lang]

        return langs

    def apply(self, callback, route):
        conf = route.config.get('langs') or {}
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'langs' keyword.
        # Ignore it if it does not need a gettext handle.
        args = inspect.getargspec(route.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            # Add the languages as a keyword argument.
            kwargs[keyword] = self.get_language()

            return callback(*args, **kwargs)

        return wrapper

Plugin = LangsPlugin