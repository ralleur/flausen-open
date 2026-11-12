"""The desktop executor must reject injected commands and invalid volume values."""
import importlib.util
import json
import queue
import tempfile
import threading
import types
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location('hermes_bridge', Path(__file__).with_name('bridge.py'))
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class ToolBoundaryTests(unittest.TestCase):
    def test_qwen_switch_releases_its_server(self):
        with patch.object(bridge, 'configured_model', return_value=bridge.QWEN_MODEL):
            session=bridge.Bridge()
        with patch.object(bridge, 'configured_model', return_value='lfm3:1.7b-hermes'), patch.object(bridge, 'emit'), patch.object(bridge.subprocess, 'run') as execute:
            session.handle({'action':'reset'})
        execute.assert_called_once_with(['systemctl','--user','stop','ralleur-hermes-qwen.service'],capture_output=True,timeout=15)

    def test_new_conversation_reloads_configured_model(self):
        with patch.object(bridge, 'configured_model', return_value='deepseek-flash'):
            session=bridge.Bridge()
        with patch.object(bridge, 'configured_model', return_value='lfm3:1.7b-hermes'), patch.object(bridge, 'emit') as emitted:
            session.handle({'action':'reset'})
        self.assertEqual(session.model,'lfm3:1.7b-hermes')
        emitted.assert_any_call('ready', model='lfm3:1.7b-hermes', location='local')

    def test_provider_errors_hide_credentials(self):
        token = 'sk-' + 'A' * 32
        self.assertNotIn(token, bridge.safe_error('Authentication failed: ' + token))
        self.assertIn('API key hidden', bridge.safe_error(token))
        self.assertNotIn('secret-token',bridge.safe_error('Authorization: Bearer secret-token'))
        self.assertNotIn('eyJtest.payload.signature',bridge.safe_error('JWT eyJtest.payload.signature'))

    def test_app_command_injection_is_rejected(self):
        with patch.object(bridge.subprocess, 'run') as execute:
            self.assertIn('error', json.loads(bridge.open_app({'app': 'steam; touch /tmp/injected'})))
            self.assertIn('error', json.loads(bridge.open_app({'app': 'steam', 'command': 'reboot'})))
            execute.assert_not_called()

    def test_volume_is_bounded_and_strictly_typed(self):
        with patch.object(bridge.subprocess, 'run') as execute:
            for value in (-1, 101, True, '50; reboot', 0.5):
                self.assertIn('error', json.loads(bridge.set_volume({'percent': value})))
            execute.assert_not_called()

    def test_volume_uses_an_argument_list_and_verifies(self):
        with patch.object(bridge, 'command', side_effect=['', 'Volume: 0.40']) as execute:
            self.assertEqual(json.loads(bridge.set_volume({'percent': 40})), {'volume': 'Volume: 0.40'})
            self.assertEqual(execute.call_args_list[0].args[0], ['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '40%'])
            self.assertEqual(execute.call_args_list[1].args[0], ['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'])

    def test_inspection_does_not_accept_commands(self):
        with patch.object(bridge.subprocess, 'run') as execute:
            self.assertIn('error', json.loads(bridge.inspect_system({'topic': 'services; reboot'})))
            self.assertIn('error', json.loads(bridge.inspect_system({'topic': 'services', 'command': 'reboot'})))
            execute.assert_not_called()


class QwenProviderTests(unittest.TestCase):
    def test_chatgpt_api_and_subscription_use_distinct_credentials(self):
        for provider in ('openai','openai-codex'):
            with self.subTest(provider=provider):
                factory=Mock();resolve=Mock(return_value={'api_key':'subscription-token'})
                modules={
                    'run_agent':types.SimpleNamespace(AIAgent=factory),
                    'tools.registry':types.SimpleNamespace(registry=Mock()),
                    'toolsets':types.SimpleNamespace(TOOLSETS={}),
                    'hermes_cli.config':types.SimpleNamespace(load_config_readonly=lambda:{'model':{'provider':provider,'reasoning_effort':'high'}}),
                    'hermes_cli.auth':types.SimpleNamespace(resolve_codex_runtime_credentials=resolve),
                    'dotenv':types.SimpleNamespace(dotenv_values=lambda path:{'OPENAI_API_KEY':'api-key'}),
                }
                with patch.dict(bridge.sys.modules,modules),patch.dict(bridge.os.environ,{'RALLEUR_HERMES_MODEL':bridge.CHATGPT_MODEL}):
                    session=bridge.Bridge();session.make_agent()
                args=factory.call_args.kwargs
                self.assertEqual(args['provider'],provider)
                self.assertEqual(args['api_mode'],'codex_responses')
                self.assertEqual(args['model'],'gpt-6.1-sol')
                self.assertEqual(bridge.model_location(session.model),'cloud')
                self.assertNotIn('reasoning_effort',args['request_overrides'])
                if provider=='openai':
                    resolve.assert_not_called();self.assertEqual(args['api_key'],'api-key')
                    self.assertEqual(args['base_url'],'https://api.openai.com/v1')
                else:
                    self.assertEqual(resolve.call_args_list[0].kwargs,{'read_only':True})
                    self.assertEqual(args['api_key'],'subscription-token')
                    self.assertEqual(args['base_url'],'https://chatgpt.com/backend-api/codex')

    def test_network_endpoint_routes_model_without_local_runtime_or_vendor_options(self):
        for key in ('lan-secret',''):
            factory=Mock()
            config={'model':{'default':'local-endpoint'},'local_endpoint':{'base_url':'http://models.lan:1234/v1','model':'served-model'}}
            modules={
                'run_agent':types.SimpleNamespace(AIAgent=factory),
                'tools.registry':types.SimpleNamespace(registry=Mock()),
                'toolsets':types.SimpleNamespace(TOOLSETS={}),
                'hermes_cli.config':types.SimpleNamespace(load_config_readonly=lambda:config),
                'dotenv':types.SimpleNamespace(dotenv_values=lambda path:{'LOCAL_ENDPOINT_API_KEY':key}),
            }
            with patch.dict(bridge.sys.modules,modules),patch.dict(bridge.os.environ,{'RALLEUR_HERMES_MODEL':'local-endpoint'}),patch.object(bridge,'ensure_qwen') as ensure:
                bridge.Bridge().make_agent()
            ensure.assert_not_called()
            args=factory.call_args.kwargs
            self.assertEqual(args['provider'],'custom')
            self.assertEqual(args['model'],'served-model')
            self.assertEqual(args['base_url'],'http://models.lan:1234/v1')
            self.assertEqual(args['api_key'],key or 'local')
            self.assertEqual(args['api_mode'],'chat_completions')
            self.assertEqual(args['request_overrides'],{})
            self.assertFalse(args['reasoning_config']['enabled'])

    def test_qwen_routing_and_thinking_do_not_use_ollama_options(self):
        for reasoning in ('none','high'):
            with self.subTest(reasoning=reasoning):
                agent_factory=Mock()
                modules={
                    'run_agent':types.SimpleNamespace(AIAgent=agent_factory),
                    'tools.registry':types.SimpleNamespace(registry=Mock()),
                    'toolsets':types.SimpleNamespace(TOOLSETS={}),
                    'hermes_cli.config':types.SimpleNamespace(load_config_readonly=lambda:{'model':{'reasoning_effort':reasoning}}),
                }
                with patch.dict(bridge.sys.modules,modules), patch.dict(bridge.os.environ,{'RALLEUR_HERMES_MODEL':bridge.QWEN_MODEL}), patch.object(bridge,'ensure_qwen') as ensure:
                    session=bridge.Bridge();session.make_agent()
                ensure.assert_called_once_with(session.cancelled)
                args=agent_factory.call_args.kwargs
                self.assertEqual(args['base_url'],bridge.QWEN_URL)
                self.assertEqual(args['max_tokens'],8192)
                extra=args['request_overrides']['extra_body']
                self.assertNotIn('keep_alive',extra)
                self.assertEqual(extra['chat_template_kwargs']['enable_thinking'],reasoning!='none')
                self.assertEqual(extra['chat_template_kwargs']['reasoning_effort'],'none' if reasoning=='none' else 'medium')


class AutostartTests(unittest.TestCase):
    def test_user_disabled_override_wins_without_executing_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            user, system = root/'user', root/'system'
            for base in (user, system): (base/'autostart').mkdir(parents=True)
            (system/'autostart/same.desktop').write_text('[Desktop Entry]\nName=System App\nType=Application\nExec=touch /tmp/should-never-run\n')
            (user/'autostart/same.desktop').write_text('[Desktop Entry]\nHidden=true\nName=Disabled Override\n')
            (system/'autostart/gnome.desktop').write_text('[Desktop Entry]\nName=GNOME App\nOnlyShowIn=GNOME;\n')
            (system/'autostart/visible.desktop').write_text('[Desktop Entry]\nName=Hidden from menus only\nNoDisplay=true\nOnlyShowIn=KDE;\n')
            (system/'autostart/conditional.desktop').write_text('[Desktop Entry]\nName=Conditional\nX-KDE-autostart-condition=some-config:Group:Key:true\n')
            with patch.object(bridge.subprocess, 'run') as execute:
                rows, errors = bridge.collect_autostart(user, [system], 'KDE')
                execute.assert_not_called()
            self.assertFalse(errors)
            statuses = {row['name']: row['status'] for row in rows}
            self.assertEqual(statuses, {'Disabled Override': 'deaktiviert', 'GNOME App': 'deaktiviert',
                                        'Hidden from menus only': 'aktiviert', 'Conditional': 'bedingt'})


class CommandApprovalTests(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.runner = bridge.Bridge()
        self.terminal = types.ModuleType('tools.terminal_tool')
        from unittest.mock import Mock
        self.terminal.terminal_tool = Mock(return_value='{"output":"ok"}')

    def proposal(self):
        self.result = self.runner.system_command({'command': 'printf ok', 'reason': 'Prüfausgabe anzeigen'})

    def test_exact_request_id_and_explicit_approval_required(self):
        with patch.object(bridge, 'emit', side_effect=lambda event, **values: self.events.put((event, values))), patch.dict(bridge.sys.modules, {'tools.terminal_tool': self.terminal}):
            thread = threading.Thread(target=self.proposal)
            thread.start()
            event, values = self.events.get(timeout=2)
            self.assertEqual(event, 'approval')
            self.terminal.terminal_tool.assert_not_called()
            self.runner.handle({'action': 'approve', 'id': 'wrong-id', 'allowed': True})
            self.assertFalse(self.runner.approval['event'].is_set())
            self.runner.handle({'action': 'approve', 'id': values['id'], 'allowed': 'true'})
            self.assertFalse(self.runner.approval['event'].is_set())
            self.runner.handle({'action': 'approve', 'id': values['id'], 'allowed': True})
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.terminal.terminal_tool.assert_called_once()
            self.assertEqual(self.terminal.terminal_tool.call_args.args[0], 'printf ok')
            self.assertTrue(json.loads(self.result)['approved_by_user'])

    def test_cancel_never_executes_the_command(self):
        with patch.object(bridge, 'emit', side_effect=lambda event, **values: self.events.put((event, values))), patch.dict(bridge.sys.modules, {'tools.terminal_tool': self.terminal}):
            thread = threading.Thread(target=self.proposal)
            thread.start()
            self.events.get(timeout=2)
            self.runner.handle({'action': 'cancel'})
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.terminal.terminal_tool.assert_not_called()
            self.assertIn('error', json.loads(self.result))

    def test_denial_never_executes_the_command(self):
        with patch.object(bridge, 'emit', side_effect=lambda event, **values: self.events.put((event, values))), patch.dict(bridge.sys.modules, {'tools.terminal_tool': self.terminal}):
            thread = threading.Thread(target=self.proposal)
            thread.start()
            _, values = self.events.get(timeout=2)
            self.runner.handle({'action': 'approve', 'id': values['id'], 'allowed': False})
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.terminal.terminal_tool.assert_not_called()
            self.assertIn('error', json.loads(self.result))


if __name__ == '__main__':
    unittest.main()
