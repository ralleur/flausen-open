"""Merge flausen messages into Caelestia's existing German Qt catalog."""
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
QT = Path('/usr/lib/qt6/bin')


def build(shell, replacements):
    messages = json.loads((HERE/'messages-de.json').read_text())
    with tempfile.TemporaryDirectory(prefix='flausen-i18n-') as directory:
        work = Path(directory)
        base = work/'base.ts'
        subprocess.run([str(QT/'lconvert'), '-i', str(shell/'translations/caelestia_de.qm'), '-o', str(base)], check=True, capture_output=True)
        tree = ET.parse(base)
        root = tree.getroot()
        contexts = {c.findtext('name'): c for c in root.findall('context')}
        by_source = {}
        for context in contexts.values():
            for message in context.findall('message'):
                translation = message.find('translation')
                if translation is not None and translation.text and not translation.get('type'):
                    by_source.setdefault(message.findtext('source'), translation.text)
        by_source.update(messages)
        # Scan the exact staged QML, so contexts and newly normalized sources agree.
        stage = work/'qml'
        stage.mkdir()
        for path in shell.rglob('*.qml'):
            dest = stage/path.relative_to(shell)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(replacements.get(path, path.read_bytes()))
        extracted = work/'extracted.ts'
        subprocess.run([str(QT/'lupdate'), str(stage), '-no-obsolete', '-ts', str(extracted)], check=True, capture_output=True)
        for context in ET.parse(extracted).getroot().findall('context'):
            name = context.findtext('name')
            target = contexts.get(name)
            if target is None:
                target = ET.SubElement(root, 'context')
                ET.SubElement(target, 'name').text = name
                contexts[name] = target
            existing = {(m.findtext('source'), m.findtext('comment')): m for m in target.findall('message')}
            for message in context.findall('message'):
                source = message.findtext('source')
                if message.get('numerus') == 'yes':
                    if source == '%n transfer(s) recorded':
                        for old in target.findall('message'):
                            if old.findtext('source') == source: target.remove(old)
                        current = ET.SubElement(target, 'message', numerus='yes')
                        ET.SubElement(current, 'source').text = source
                        translation = ET.SubElement(current, 'translation')
                        for form in ['%n Übertragung erfasst', '%n Übertragungen erfasst']:
                            ET.SubElement(translation, 'numerusform').text = form
                    continue
                if source not in by_source: continue
                key = (source, message.findtext('comment'))
                current = existing.get(key)
                if current is None and (source, None) in existing:
                    continue
                if current is None:
                    current = ET.SubElement(target, 'message')
                    ET.SubElement(current, 'source').text = source
                    if key[1]: ET.SubElement(current, 'comment').text = key[1]
                translation = current.find('translation')
                if translation is None: translation = ET.SubElement(current, 'translation')
                translation.attrib.clear()
                translation.text = by_source[source]
        target = contexts.get('Flausen')
        if target is None:
            target = ET.SubElement(root, 'context')
            ET.SubElement(target, 'name').text = 'Flausen'
        existing = {m.findtext('source'): m for m in target.findall('message')}
        for source, translated in messages.items():
            if source in existing: continue
            message = ET.SubElement(target, 'message')
            ET.SubElement(message, 'source').text = source
            ET.SubElement(message, 'translation').text = translated
        merged = work/'merged.ts' 
        tree.write(merged, encoding='utf-8', xml_declaration=True)
        output = work/'caelestia_de.qm'
        subprocess.run([str(QT/'lrelease'), str(merged), '-qm', str(output)], check=True, capture_output=True)
        return output.read_bytes()


def standalone():
    messages = json.loads((HERE/'messages-de.json').read_text())
    root = ET.Element('TS', version='2.1', language='de_DE')
    context = ET.SubElement(root, 'context')
    ET.SubElement(context, 'name').text = 'Flausen'
    for source, translated in messages.items():
        message = ET.SubElement(context, 'message')
        ET.SubElement(message, 'source').text = source
        ET.SubElement(message, 'translation').text = translated
    with tempfile.TemporaryDirectory() as directory:
        ts, qm, po, mo = [Path(directory)/('flausen.'+ext) for ext in ('ts','qm','po','mo')]
        ET.ElementTree(root).write(ts, encoding='utf-8', xml_declaration=True)
        subprocess.run([str(QT/'lrelease'), str(ts), '-qm', str(qm)], check=True, capture_output=True)
        # JSON quoting is compatible with gettext's quoted UTF-8 strings.
        lines = ['msgid ""', 'msgstr ""', '"Content-Type: text/plain; charset=UTF-8\\n"', '']
        for source, translated in messages.items():
            lines += ['msgid '+json.dumps(source, ensure_ascii=False), 'msgstr '+json.dumps(translated, ensure_ascii=False), '']
        po.write_text('\n'.join(lines))
        subprocess.run(['msgfmt', str(po), '-o', str(mo)], check=True, capture_output=True)
        return qm.read_bytes(), mo.read_bytes()
