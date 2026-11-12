"""Device-login contract without a network request or real credentials."""
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock,patch
from contextlib import redirect_stdout

spec=importlib.util.spec_from_file_location('openai_auth',Path(__file__).resolve().parents[1]/'helpers/openai_auth.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

class LoginTests(unittest.TestCase):
    def test_device_flow_saves_only_to_hermes_and_does_not_emit_tokens(self):
        save=Mock()
        modules={
            'hermes_cli.auth':types.SimpleNamespace(_save_codex_tokens=save,_utc_now_z=lambda:'now',get_codex_auth_status=lambda:{'logged_in':True}),
            'hermes_cli.auth_codex':types.SimpleNamespace(
                CODEX_OAUTH_CLIENT_ID='client',
                _codex_request_device_code=lambda *a:{'user_code':'ABCD-1234','device_auth_id':'private-device','interval':1},
                _codex_poll_authorization_code=lambda *a,**k:{'code':'private-code'},
                _codex_exchange_authorization_code=lambda *a:{'access_token':'private-access','refresh_token':'private-refresh'}),
        }
        out=io.StringIO()
        with patch.dict(sys.modules,modules),redirect_stdout(out):helper.login()
        events=[json.loads(line) for line in out.getvalue().splitlines()]
        self.assertEqual(events[0],{'event':'device','url':'https://auth.openai.com/codex/device','code':'ABCD-1234'})
        self.assertTrue(events[1]['loggedIn'])
        for secret in ('private-device','private-code','private-access','private-refresh'):
            self.assertNotIn(secret,out.getvalue())
        save.assert_called_once()
        self.assertEqual(save.call_args.args[0]['refresh_token'],'private-refresh')
        self.assertFalse(save.call_args.kwargs['set_active'])

    def test_login_errors_are_sanitized(self):
        out=io.StringIO()
        with patch.object(sys,'argv',['auth','login']),patch.object(helper,'login',side_effect=RuntimeError('private-access')),redirect_stdout(out):helper.main()
        self.assertNotIn('private-access',out.getvalue())
        self.assertFalse(json.loads(out.getvalue())['ok'])

if __name__=='__main__':unittest.main()
