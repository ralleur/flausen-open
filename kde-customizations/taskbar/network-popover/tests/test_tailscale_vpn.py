import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('tailscale_vpn', Path(__file__).parents[1] / 'tailscale-vpn.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class TailscaleTests(unittest.TestCase):
    def test_backend_state_not_peer_activity_determines_connection(self):
        status = adapter.status_from_result(0, '{"BackendState":"Running","Self":{"Active":false},"Peer":{}}', '')
        self.assertTrue(status['connected'])
        self.assertEqual(status['detail'], 'Connected')
        self.assertNotIn('Peer', status)
        self.assertNotIn('Self', status)

    def test_disconnected_and_auth_states_remain_visible(self):
        for state in ['Stopped', 'NeedsLogin', 'NeedsMachineAuth', 'Starting']:
            with self.subTest(state=state):
                status = adapter.status_from_result(1, '{"BackendState":"' + state + '"}', '')
                self.assertTrue(status['installed'])
                self.assertFalse(status['connected'])
                self.assertNotEqual(status['detail'], 'Connected')

    def test_daemon_or_status_errors_never_report_connected(self):
        for output in ['', '{}', 'not json', '[]']:
            self.assertFalse(adapter.status_from_result(1, output, 'daemon unavailable')['connected'])
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(args[0], 5)
        self.assertEqual(adapter.execute('status', '/usr/bin/tailscale', timeout)['state'], 'Unavailable')

    def test_absent_binary_does_not_create_phantom_vpn(self):
        with patch.object(adapter.shutil, 'which', return_value=None):
            self.assertFalse(adapter.execute('status')['installed'])

    def test_actions_preserve_settings_and_propagate_permission_failure(self):
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 1, '', 'Access denied')
        for action, cmd in [('connect', 'up'), ('disconnect', 'down')]:
            result = adapter.execute(action, '/usr/bin/tailscale', run)
            self.assertEqual(calls[-1], ['/usr/bin/tailscale', cmd])
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], 'Access denied')


if __name__ == '__main__':
    unittest.main()
