"""Task Manager message catalogs; KDE's UI-language preference precedes the environment."""
import argparse
import configparser
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_PATH = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))/'plasma-localerc'


class Language:
    def __init__(self, config_path=None, environment=None):
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        self.environment = os.environ if environment is None else environment
        self.language = None
        self.locale = 'en_US'
        self.messages = {}
        self.refresh()

    def refresh(self):
        config = configparser.ConfigParser(interpolation=None)
        try:
            config.read(self.config_path)
            preference = config.get('Translations', 'LANGUAGE', fallback='')
            if not preference:
                preference = config.get('Formats', 'LANG', fallback='')
        except (OSError, configparser.Error):
            preference = ''
        if not preference:
            preference = next((self.environment.get(key) for key in ('LANGUAGE','LC_ALL','LC_MESSAGES','LANG') if self.environment.get(key)), 'en_US')
        supported = {'en'} | {path.stem for path in (HERE/'locales').glob('*.json')}
        chosen = 'en_US'
        for candidate in preference.split(':'):
            candidate = candidate.split('.')[0].split('@')[0].replace('-', '_')
            if candidate.split('_')[0] in supported:
                chosen = candidate
                break
        language = chosen.split('_')[0]
        self.locale = chosen
        if language != self.language:
            path = HERE/'locales'/(language+'.json')
            try:
                self.messages = json.loads(path.read_text()) if path.exists() else {}
            except (OSError, ValueError):
                self.messages = {}
            self.language = language

    def translate(self, text, **values):
        result = self.messages.get(text, text)
        return result.format(**values) if values else result


def desktop_value(entry, key):
    return entry.get(key+'['+language.locale+']', entry.get(key+'['+language.language+']', entry.get(key, '')))


language = Language()
t = language.translate

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--locale', action='store_true')
    parser.parse_args()
    print(language.locale)
