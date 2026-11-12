"""Private Hermes Codex login. JSON events contain no access/refresh tokens."""
import contextlib
import json
import os
from pathlib import Path
import sys

os.umask(0o077)
os.environ['HERMES_HOME']=str(Path.home()/'.local/state/ralleur-hermes/profile')
sys.path.insert(0,str(Path.home()/'.local/share/ralleur-hermes/runtime'))

def emit(**value):
    print(json.dumps(value,ensure_ascii=False),flush=True)

def auth_status():
    from hermes_cli.auth import get_codex_auth_status
    state=get_codex_auth_status()
    return dict(loggedIn=bool(state.get('logged_in')),
                expired=bool(state.get('expired')))

def login():
    from hermes_cli.auth import _save_codex_tokens, _utc_now_z
    from hermes_cli.auth_codex import (_codex_request_device_code,_codex_poll_authorization_code,
                                      _codex_exchange_authorization_code,CODEX_OAUTH_CLIENT_ID)
    issuer='https://auth.openai.com'
    data=_codex_request_device_code(issuer,CODEX_OAUTH_CLIENT_ID)
    emit(event='device',url=issuer+'/codex/device',code=data['user_code'])
    response=_codex_poll_authorization_code(issuer,device_auth_id=data['device_auth_id'],
                                           user_code=data['user_code'],poll_interval=data['interval'])
    tokens=_codex_exchange_authorization_code(issuer,CODEX_OAUTH_CLIENT_ID,response)
    if not tokens.get('access_token') or not tokens.get('refresh_token'):
        raise ValueError('Incomplete credentials')
    _save_codex_tokens({key:tokens[key] for key in ('access_token','refresh_token')},
                       last_refresh=_utc_now_z(),set_active=False)
    emit(event='complete',ok=True,**auth_status())

def main():
    try:
        if sys.argv[1:] == ['login']:login()
        else:
            with contextlib.redirect_stdout(sys.stderr):state=auth_status()
            emit(ok=True,**state)
    except Exception:
        # Provider exceptions may contain sensitive response details; never echo them.
        emit(ok=False,event='error',error='Could not complete Codex sign-in. Please try again.')

if __name__=='__main__':main()
