"""Translate owned Python presentation messages; keep protocol values unchanged."""
import json
from pathlib import Path
from language import language
HERE = Path(__file__).resolve().parent
MESSAGES = json.loads((HERE/'messages-de.json').read_text())
SOURCES = json.loads((HERE/'english-strings.json').read_text())


def t(text):
    source = SOURCES.get(text, text)
    return MESSAGES.get(source, source) if language() == 'de' else source
