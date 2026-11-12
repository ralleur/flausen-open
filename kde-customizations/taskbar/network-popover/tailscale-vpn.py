#!/usr/bin/env python3
"""Small, bounded adapter for Tailscale's own daemon, independent of NM profiles."""
import json
import shutil
import subprocess
import sys


def status_from_result(code, output, error):
    result = dict(installed=True, connected=False, state='Unavailable', detail='Status unavailable')
    try:
        data = json.loads(output)
        state = data.get('BackendState', 'Unavailable')
        result.update(state=state, connected=state == 'Running')
        descriptions = {'Running': 'Connected', 'Stopped': 'Disconnected', 'NeedsLogin': 'Sign-in required',
                        'NeedsMachineAuth': 'Device authorization required', 'Starting': 'Connecting …'}
        result['detail'] = descriptions.get(state, 'Status unavailable')
        if code and state == 'Unavailable':
            result['detail'] = 'Tailscale service unavailable'
    except (ValueError, TypeError, AttributeError):
        result['detail'] = 'Tailscale service unavailable' if code else 'Invalid status response'
    return result


def execute(action, binary=None, run=subprocess.run):
    binary = binary or shutil.which('tailscale')
    if not binary:
        return dict(installed=False, connected=False, state='NotInstalled', detail='')
    if action == 'status':
        try:
            proc = run([binary, 'status', '--json'], capture_output=True, text=True, timeout=5)
            return status_from_result(proc.returncode, proc.stdout, proc.stderr)
        except (OSError, subprocess.TimeoutExpired):
            return dict(installed=True, connected=False, state='Unavailable', detail='Tailscale service unavailable')
    if action not in ('connect', 'disconnect'):
        raise ValueError('Unsupported action')
    # No reset, sudo, or replacement preferences: retain the user's Tailscale setup.
    try:
        proc = run([binary, 'up' if action == 'connect' else 'down'], capture_output=True, text=True, timeout=20)
        error = (proc.stderr or proc.stdout).strip()[-1600:]
        return dict(success=proc.returncode == 0, error=error if proc.returncode else '')
    except subprocess.TimeoutExpired:
        return dict(success=False, error='Tailscale timed out. Check sign-in and service status.')
    except OSError as exc:
        return dict(success=False, error=str(exc))


if __name__ == '__main__':
    print(json.dumps(execute(sys.argv[1] if len(sys.argv) > 1 else 'status'), ensure_ascii=False))
