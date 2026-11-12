#!/usr/bin/env python3
"""Assemble the documented shell sources in a NEW directory; never install them."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inside(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes source tree: {name}')
    return path


def prepare(upstream, output):
    lock = json.loads((HERE / 'shell-lock.json').read_text())
    revision = subprocess.check_output(
        ['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != lock['upstream']['commit']:
        raise ValueError('Wrong Caelestia revision; use the commit in shell-lock.json.')
    if output.exists() or output.is_symlink():
        raise ValueError(f'Output already exists; choose a new directory: {output}')
    # Read committed upstream objects, never uncommitted local configuration.
    archive = subprocess.check_output(
        ['git', '-C', str(upstream), 'archive', revision + ':shell'])
    patch = (HERE / 'shell-integration.patch').read_bytes()
    if sha(patch) != lock['patch_sha256']:
        raise ValueError('Integration patch differs from the reviewed manifest.')
    sources = []
    for item in lock['files']:
        if 'source' in item:
            source = inside(REPO, item['source'])
            if sha(source.read_bytes()) != item['source_sha256']:
                raise ValueError(f'Source changed; refresh the shell manifest: {source}')
            sources.append((item, source))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='.flausen-shell-') as tmp:
        stage = Path(tmp) / 'shell'
        stage.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for entry in tar.getmembers():
                inside(stage, entry.name)
                if entry.issym() or entry.islnk():
                    raise ValueError(f'Unexpected upstream link: {entry.name}')
            tar.extractall(stage, filter='data')
        for item, source in sources:
            dest = inside(stage, item['target'])
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            dest.chmod(item['mode'])
        if patch:
            subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-d', str(stage)],
                           input=patch, check=True, stdout=subprocess.DEVNULL)
        for item in lock['files']:
            dest = inside(stage, item['target'])
            if sha(dest.read_bytes()) != item['sha256']:
                raise ValueError(f'Assembled file differs: {item["target"]}')
            dest.chmod(item['mode'])
        # Build products and personal state are intentionally not part of the assembly.
        (stage / 'flausen-source.json').write_text(json.dumps({
            'snapshot': lock['snapshot'], 'upstream': lock['upstream'],
            'files_verified': len(lock['files'])}, indent=2) + '\n')
        stage.rename(output)
    print(f'{len(lock["files"])} flausen files verified: {output}')
    print('Sources prepared only. Follow installation/MANUAL.md to build and activate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        prepare(args.upstream.resolve(), args.output.absolute())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')
