"""Read the local account and existing recent files; never invent history."""
import json
import os
from pathlib import Path
import pwd
import socket
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

home = Path.home()
account = pwd.getpwuid(os.getuid())
recent = []
try:
    source = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share')) / 'recently-used.xbel'
    bookmarks = sorted(ET.parse(source).getroot().findall('bookmark'),
                       key=lambda b: b.get('visited') or b.get('modified') or '', reverse=True)
    for entry in bookmarks:
        uri = entry.get('href', '')
        parsed = urlparse(uri)
        if parsed.scheme != 'file' or parsed.netloc not in ('', 'localhost'):
            continue
        path = Path(unquote(parsed.path))
        if (not path.exists() or path.name.startswith('.')
                or path.parent.parts[-3:] == ('kde-customizations', 'launcher', 'evidence')):
            continue
        mime = entry.find('.//{http://www.freedesktop.org/standards/shared-mime-info}mime-type')
        kind = mime.get('type', '') if mime is not None else ''
        icon = 'folder' if path.is_dir() else ('image-x-generic' if kind.startswith('image/') else 'text-x-generic')
        recent.append(dict(title=entry.findtext('title') or path.name, detail=str(path.parent).replace(str(home), '~', 1), uri=uri, icon=icon))
        if len(recent) == 12:
            break
except (OSError, ET.ParseError):
    pass
face = next((str(p) for p in [home / '.face.icon', home / '.face', Path('/var/lib/AccountsService/icons') / account.pw_name] if p.is_file()), '')
print(json.dumps(dict(name=account.pw_gecos.split(',')[0] or account.pw_name, detail=f'{account.pw_name} · {socket.gethostname()}', face=face, recent=recent)))
