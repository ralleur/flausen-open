"""Verify private profile edits and stale-form protection in an isolated profile."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import yaml

spec=importlib.util.spec_from_file_location('settings_helper',Path(__file__).resolve().parents[1]/'helpers/hermes_settings.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

class HermesSettingsTests(unittest.TestCase):
    def setUp(self):
        mock=patch.object(helper,'codex_status',return_value=False);mock.start();self.addCleanup(mock.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        helper.PROFILE=Path(self.temp.name)
        (helper.PROFILE/'config.yaml').write_text('model:\n  default: deepseek-flash\n  reasoning_effort: high\nagent:\n  max_turns: 10\n')
        self.key='sk-'+('A'*32)
        (helper.PROFILE/'.env').write_text('OTHER_VALUE=preserved\nDEEPSEEK_API_KEY='+self.key+'\n')
    def request(self,**values):
        return dict(action='save',revision=helper.revision(),model='lfm3:1.7b-hermes',thinking=False,apiKey='',**values)
    def test_save_preserves_credentials_and_other_settings(self):
        result=helper.save(self.request())
        self.assertEqual(result['model'],'lfm3:1.7b-hermes');self.assertFalse(result['thinking'])
        self.assertNotIn(self.key,json.dumps(result))
        self.assertIn(self.key,(helper.PROFILE/'.env').read_text())
        self.assertEqual(yaml.safe_load((helper.PROFILE/'config.yaml').read_text())['agent']['max_turns'],10)
        self.assertEqual((helper.PROFILE/'config.yaml').stat().st_mode & 0o777,0o600)
    def test_stale_forms_cannot_overwrite_changes(self):
        request=self.request();helper.save(request)
        with self.assertRaisesRegex(ValueError,'inzwischen'):helper.save(request)
    def test_chatgpt_api_key_is_private_and_keeps_deepseek_key(self):
        request=self.request();request.update(model='chatgpt',chatgptAuth='api',openaiApiKey='sk-proj-'+('C'*90))
        result=helper.save(request)
        self.assertEqual(result['model'],'chatgpt');self.assertEqual(result['chatgptAuth'],'api')
        self.assertNotIn(request['openaiApiKey'],json.dumps(result))
        env=helper.dotenv_values(helper.PROFILE/'.env')
        self.assertEqual(env['DEEPSEEK_API_KEY'],self.key)
        self.assertEqual(env['OPENAI_API_KEY'],request['openaiApiKey'])
        model=yaml.safe_load((helper.PROFILE/'config.yaml').read_text())['model']
        self.assertEqual(model['provider'],'openai');self.assertEqual(model['default'],'gpt-6.1-sol')
        self.assertEqual(model['api_mode'],'codex_responses')
    def test_subscription_requires_own_login_and_does_not_fall_back_to_api(self):
        request=self.request();request.update(model='chatgpt',chatgptAuth='codex')
        before=helper.revision()
        with self.assertRaisesRegex(ValueError,'anmelden'):helper.save(request)
        self.assertEqual(helper.revision(),before)
        with patch.object(helper,'codex_status',return_value=True):result=helper.save(request)
        self.assertEqual(result['chatgptAuth'],'codex')
        model=yaml.safe_load((helper.PROFILE/'config.yaml').read_text())['model']
        self.assertEqual(model['provider'],'openai-codex')
        self.assertNotIn('OPENAI_API_KEY',helper.dotenv_values(helper.PROFILE/'.env'))
    def test_qwen_uses_private_llama_endpoint_and_preserves_credentials(self):
        request=self.request();request.update(model='qwen3.8:27b-hermes',thinking=True)
        result=helper.save(request)
        model=yaml.safe_load((helper.PROFILE/'config.yaml').read_text())['model']
        self.assertEqual(result['model'],'qwen3.8:27b-hermes')
        self.assertEqual(model['base_url'],'http://127.0.0.1:18038/v1')
        self.assertEqual(model['context_length'],90112)
        self.assertEqual(helper.dotenv_values(helper.PROFILE/'.env')['DEEPSEEK_API_KEY'],self.key)
    def test_key_replace_is_private_and_preserves_other_values(self):
        request=self.request();request.update(apiKey='sk-'+('B'*32),model='deepseek-flash',thinking=True)
        result=helper.save(request)
        self.assertNotIn(request['apiKey'],json.dumps(result))
        self.assertEqual(helper.dotenv_values(helper.PROFILE/'.env')['OTHER_VALUE'],'preserved')
        self.assertEqual((helper.PROFILE/'.env').stat().st_mode & 0o777,0o600)
    def test_endpoint_roundtrip_preserves_secret_and_other_models(self):
        request=self.request();request.update(model='local-endpoint',endpointUrl='http://models.lan:1234/v1/',endpointModel='org/model:Q4',endpointApiKey='lan.secret-token')
        result=helper.save(request)
        self.assertEqual(result['model'],'local-endpoint')
        self.assertEqual(result['endpointUrl'],'http://models.lan:1234/v1')
        self.assertEqual(result['endpointModel'],'org/model:Q4')
        self.assertTrue(result['endpointKeyConfigured'])
        self.assertNotIn('lan.secret-token',json.dumps(result))
        self.assertEqual(helper.dotenv_values(helper.PROFILE/'.env')['DEEPSEEK_API_KEY'],self.key)
        helper.save(self.request())
        self.assertEqual(helper.status()['endpointModel'],'org/model:Q4')
        request.update(revision=helper.revision(),endpointApiKey='')
        helper.save(request)
        self.assertEqual(helper.dotenv_values(helper.PROFILE/'.env')['LOCAL_ENDPOINT_API_KEY'],'lan.secret-token')
        self.assertEqual((helper.PROFILE/'.env').stat().st_mode & 0o777,0o600)
        self.assertEqual(yaml.safe_load((helper.PROFILE/'config.yaml').read_text())['model']['provider'],'custom')

    def test_invalid_endpoints_do_not_modify_profile(self):
        before=helper.revision()
        for url,model in [('file:///etc/passwd','model'),('http://user:pass@host/v1','model'),('http://host:bad/v1','model'),('http://host/v1?key=secret','model'),('http://host/v1',''),('http://host/v1','bad model')]:
            request=self.request();request.update(model='local-endpoint',endpointUrl=url,endpointModel=model)
            with self.assertRaises(ValueError):helper.save(request)
        self.assertEqual(helper.revision(),before)

    def test_invalid_requests_do_not_write(self):
        before=helper.revision()
        for field,value in [('model','arbitrary'),('thinking','yes'),('apiKey','key\nINJECT=1')]:
            request=self.request();request[field]=value
            with self.assertRaises(ValueError):helper.save(request)
        self.assertEqual(before,helper.revision())

class VramTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(helper,'QWEN_ROOT',Path('/nonexistent-hermes-test-runtime')).start()
        patch.object(helper,'qwen_loaded',return_value=False).start()

    def test_qwen_estimate_uses_gpu_split_and_accounts_for_overhead(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'profile.json').write_text('{"context_tokens":90112,"gpu_layers":44}')
            output=type('Result',(),{'stdout':'CUDA0 8341 1188 698\nHost 3850 549 128\n'})()
            with patch.object(helper,'QWEN_ROOT',root),patch.object(helper.subprocess,'run',return_value=output) as execute:
                plan=helper.qwen_preview()
            configured=next(c for c in plan['contexts'] if c['tokens']==90112)
            self.assertEqual(configured['modelBytes'],8341*1048576)
            self.assertEqual(configured['bytes'],1188*1048576)
            self.assertEqual(configured['runtimeBytes'],(698+978+282+462)*1048576)
            self.assertEqual(plan['gpuLayers'],44)
            argv=execute.call_args.args[0]
            self.assertEqual(argv[argv.index('-ngl')+1],'44')
            self.assertIn('llama-fit-params',argv[0])

    def test_qwen_preview_available_without_ollama_and_running_model_not_counted_twice(self):
        plan={'name':'qwen3.8:27b-hermes'}
        with patch.object(helper,'qwen_preview',return_value=plan),patch.object(helper,'qwen_loaded',return_value=True),patch.object(helper,'gpu_snapshot',return_value=[]),patch.object(helper,'ollama_read',side_effect=OSError()):
            result=helper.resources()
        self.assertEqual(result['locals'][plan['name']],plan)
        self.assertIsNone(result['loadedVram'])

    def test_hybrid_cache_counts_only_attention_layers(self):
        info={'general.architecture':'hybrid','hybrid.block_count':3,'hybrid.attention.head_count_kv':[0,4,0],
              'hybrid.attention.key_length':128,'hybrid.attention.value_length':128}
        self.assertEqual(helper.kv_budget(info,65536),4*256*2*65536)
        self.assertEqual(helper.kv_budget(info,131072),2*helper.kv_budget(info,65536))
        self.assertIsNone(helper.kv_budget({},65536))
    def test_gpu_readings_remain_separate(self):
        output='GPU-a, Card A, 8192, 1024\nGPU-b, Card B, 16384, 2048\n'
        with patch.object(helper.subprocess,'run',return_value=type('Result',(),{'stdout':output})()):
            gpus=helper.gpu_snapshot()
        nvidia=[g for g in gpus if g['id'].startswith('GPU-')]
        self.assertEqual([g['total'] for g in nvidia],[8192*1048576,16384*1048576])
    def test_model_metadata_and_cpu_configuration(self):
        responses=[{'models':[]},{'models':[{'name':'lfm3:1.7b-hermes','size':1000}]},
                   {'parameters':'num_gpu 0\nnum_ctx 65536','model_info':{}}]
        with patch.object(helper,'gpu_snapshot',return_value=[]),patch.object(helper,'ollama_read',side_effect=responses):
            result=helper.resources()
        self.assertTrue(result['local']['cpuOnly'])
        self.assertEqual(result['local']['modelBytes'],1000)
        self.assertEqual(result['loadedVram'],0)
        self.assertTrue(all(c['bytes'] is None for c in result['local']['contexts']))
    def test_offline_ollama_is_unknown_not_zero(self):
        with patch.object(helper,'gpu_snapshot',return_value=[]),patch.object(helper,'ollama_read',side_effect=OSError()):
            result=helper.resources()
        self.assertIsNone(result['loadedVram']);self.assertFalse(result['ollamaAvailable'])

if __name__=='__main__':unittest.main()
