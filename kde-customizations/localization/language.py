#!/usr/bin/env python3
"""KDE UI-language selection, independent of regional formats and stale session env."""
import argparse
import configparser
import os
from pathlib import Path
import subprocess


def select(preference, supported=('de', 'en')):
    for candidate in preference.split(':'):
        code = candidate.split('.')[0].split('@')[0].replace('-', '_')
        if code in ('C', 'POSIX'):
            return 'en'
        language = code.split('_')[0]
        if language in supported:
            return language
    return 'en'


def preferences(config_path=None, environment=None):
    env = os.environ if environment is None else environment
    config = configparser.ConfigParser(interpolation=None, strict=False)
    path = Path(config_path) if config_path else Path(env.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))/'plasma-localerc'
    try:
        config.read(path)
        ui = config.get('Translations', 'LANGUAGE', fallback='')
        formats = config.get('Formats', 'LANG', fallback='')
    except (OSError, configparser.Error):
        ui = formats = ''
    fallback = next((env[key] for key in ('LANGUAGE','LC_ALL','LC_MESSAGES','LANG') if env.get(key)), 'en_US')
    return ui or formats or fallback, formats


def language(config_path=None, environment=None):
    return select(preferences(config_path, environment)[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--qml')
    args, extra = parser.parse_known_args()
    code = language()
    if not args.qml:
        print(code)
        return
    env = dict(os.environ)
    env.pop('LC_ALL', None)
    env['LANGUAGE'] = code
    env['LC_MESSAGES'] = 'de_DE.UTF-8' if code == 'de' else 'en_US.UTF-8'
    formats = preferences()[1]
    if formats: env['LANG'] = formats
    command = ['/usr/lib/qt6/bin/qml']
    if code == 'de':
        command += ['--translation', str(Path(__file__).with_name('flausen_de.qm'))]
    command += [args.qml, *extra]
    raise SystemExit(subprocess.call(command, env=env))

if __name__ == '__main__':
    main()
