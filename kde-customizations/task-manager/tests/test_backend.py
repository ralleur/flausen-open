import importlib.util
import os
import json
import sys
from pathlib import Path
import subprocess
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location('monitor', Path(__file__).resolve().parents[1]/'backend.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class BackendTest(unittest.TestCase):
    def setUp(self):
        self.monitor = backend.Monitor()

    def test_real_snapshot_and_selected_process(self):
        child = subprocess.Popen(['sleep', '20'])
        try:
            snapshot = self.monitor.snapshot()
            self.assertGreater(snapshot['count'], 0)
            self.assertEqual([c['kind'] for c in snapshot['cards'][:3]], ['cpu', 'memory', 'gpu'])
            self.assertGreaterEqual(sum(c['kind']=='disk' for c in snapshot['cards']),1)
            self.assertEqual(snapshot['cards'][-1]['kind'], 'network')
            self.assertTrue(all('device' in c and 'nicht auslesbar' not in c['device'] for c in snapshot['cards']))
            self.assertEqual(len({c['id'] for c in snapshot['cards']}),len(snapshot['cards']))
            created = backend.psutil.Process(child.pid).create_time()
            self.monitor.action(dict(action='select', identity=dict(pid=child.pid, created=created)))
            snapshot = self.monitor.snapshot()
            self.assertEqual(snapshot['detail']['pid'], child.pid)
            self.assertIn('sleep', snapshot['detail']['path'])
            self.monitor.action(dict(action='terminate', identity=dict(pid=child.pid, created=created)))
            child.wait(timeout=3)
            self.assertTrue(self.monitor.snapshot()['detail']['exited'])
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait()

    def test_multiple_physical_disks_exclude_partitions_and_virtual_devices(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('nvme0n1', 'sda', 'nvme0n1p1', 'zram0', 'loop0', 'dm-0', 'sdb'):
                device = root/name
                (device/'device').mkdir(parents=True)
                (device/'device/model').write_text('Model '+name)
                (device/'size').write_text('0' if name=='sdb' else '2000000')
                (device/'diskseq').write_text('1')
                if name=='nvme0n1p1':
                    (device/'partition').write_text('1')
            devices = backend.physical_disks(root)
            self.assertEqual([d['name'] for d in devices], ['nvme0n1', 'sda'])
            self.assertEqual(devices[0]['capacity'],2000000*512)

    def test_disk_rates_are_independent_and_replug_starts_a_new_sample(self):
        devices = [dict(name=name,id='disk:'+name+':1',device='Model '+name,capacity=10**12) for name in ('nvme0n1', 'sda')]
        before = dict(nvme0n1=SimpleNamespace(read_bytes=100,write_bytes=200,busy_time=100),
                      sda=SimpleNamespace(read_bytes=500,write_bytes=300,busy_time=200))
        after = dict(nvme0n1=SimpleNamespace(read_bytes=1100,write_bytes=600,busy_time=300),
                     sda=SimpleNamespace(read_bytes=6500,write_bytes=1100,busy_time=1700))
        with patch.object(backend,'physical_disks',return_value=devices), patch.object(backend.psutil,'disk_io_counters',return_value=before) as io:
            first = self.monitor.disk_cards(2)
            self.assertTrue(all(c['percent'] is None for c in first))
            io.return_value=after
            cards=self.monitor.disk_cards(2)
            self.assertEqual([c['percent'] for c in cards],[10,75])
            self.assertIn('500 B/s',cards[0]['detail'])
            self.assertIn('2.9 KB/s',cards[1]['detail'])
            self.assertEqual([c['name'] for c in cards],['Disk · nvme0n1','Disk · sda'])
            devices[1]['id']='disk:sda:2'
            replugged=self.monitor.disk_cards(2)
            self.assertIsNone(replugged[1]['percent'])
            self.assertNotIn('disk:sda:1',self.monitor.previous_disks)

    def test_disk_histories_survive_process_selection_and_removed_disks_are_pruned(self):
        devices = [dict(name=name,id='disk:'+name+':1',device='Model '+name,capacity=10**12) for name in ('nvme0n1', 'sda')]
        counters = {name:SimpleNamespace(read_bytes=100,write_bytes=200,busy_time=100) for name in ('nvme0n1','sda')}
        self.monitor.action(dict(action='select',identity=dict(pid=os.getpid(),created=backend.psutil.Process().create_time())))
        with patch.object(backend,'physical_disks',return_value=devices), patch.object(backend.psutil,'disk_io_counters',return_value=counters):
            self.monitor.snapshot()
            cards=self.monitor.snapshot()['cards']
            self.assertTrue(all(len(c['history'])==2 for c in cards if c['kind']=='disk'))
            devices.pop()
            self.monitor.snapshot()
            self.assertNotIn('disk:sda:1',self.monitor.histories)
        self.assertEqual(backend.size(4000787030016,base=1000),'4.0 TB')

    def test_memory_uses_cached_configured_rate_not_nominal_speed(self):
        fields='\n'.join(f'MEMORY_DEVICE_{i}_{key}={value}' for i in range(2) for key,value in {
            'SIZE':str(32*1024**3),'TYPE':'DDR5','SPEED_MTS':'4800','CONFIGURED_SPEED_MTS':'6000',
            'MANUFACTURER':'Corsair','PART_NUMBER':'ExampleDIMM'}.items())
        with patch.object(backend,'run',return_value=SimpleNamespace(returncode=0,stdout=fields)) as command:
            label=backend.ram_model()
        self.assertIn('DDR5 · 6000 MT/s',label)
        self.assertIn('2 × 32.0 GB Corsair ExampleDIMM',label)
        self.assertNotIn('4800',label)
        self.assertEqual(command.call_args.args[0][0],'udevadm')

    def test_unreadable_memory_is_empty_and_dmidecode_fallback_includes_type_and_speed(self):
        with patch.object(backend,'run',side_effect=FileNotFoundError):
            self.assertEqual(backend.ram_model(),'')
        self.assertEqual(backend.memory_label([dict(type='Unknown',configured='Unknown',manufacturer='Unknown',part='Not Specified')]),'')
        firmware='Memory Device\n Size: 16 GB\n Type: DDR4\n Speed: 2400 MT/s\n Configured Memory Speed: 3200 MT/s\n'
        with patch.object(backend,'run',side_effect=[FileNotFoundError(),SimpleNamespace(returncode=0,stdout=firmware)]):
            self.assertEqual(backend.ram_model(),'DDR4 · 3200 MT/s')

    def test_integrated_gpu_is_a_separate_device_with_its_own_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            devices=[]
            for i,(vendor,identifier,integrated) in enumerate((('0x10de','0x2c02',False),('0x1002','0x164e',True))):
                path=root/f'0000:0{i+1}:00.0'
                path.mkdir()
                devices.append(dict(id='gpu:'+path.name,address=path.name,path=path,vendor=vendor,device='Integrated Radeon' if integrated else 'Discrete NVIDIA',integrated=integrated))
            path=devices[1]['path']
            for name,value in {'gpu_busy_percent':'7','mem_info_vram_total':str(512*1024**2),'mem_info_vram_used':str(16*1024**2)}.items():
                (path/name).write_text(value)
            hwmon=path/'hwmon/hwmon1'
            hwmon.mkdir(parents=True)
            (hwmon/'temp1_input').write_text('49000')
            (hwmon/'freq1_input').write_text('600000000')
            self.monitor.gpu_time=10
            self.monitor.nvidia={devices[0]['address']:dict(name='Discrete NVIDIA',percent=40,used=2048,total=16384,temperature=55)}
            with patch.object(backend,'graphics_devices',return_value=devices):
                cards=self.monitor.gpu_cards(11)
                self.assertEqual([c['percent'] for c in cards],[40,7])
                self.assertEqual(cards[1]['name'],'GPU · Integrated')
                self.assertIn('600 MHz · 49 °C',cards[1]['detail'])
                self.assertEqual(cards[0]['processors'][0]['value'],40)
                self.assertEqual(cards[1]['processors'][0]['value'],7)
                self.assertEqual(cards[1]['processors'][0]['id'],'graphics')
                self.assertIn('reserved',cards[1]['detail'])
                (path/'gpu_busy_percent').unlink()
                self.assertEqual(self.monitor.gpu_cards(11)[1]['value'],'')

    def test_cpu_meters_follow_physical_topology_and_average_smt_threads(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for logical,(package,core) in enumerate(((0,0),(0,1),(0,0),(1,0))):
                topology=root/f'cpu{logical}'/'topology'
                topology.mkdir(parents=True)
                (topology/'physical_package_id').write_text(str(package))
                (topology/'core_id').write_text(str(core))
            units=backend.cpu_processors([20,70,40,90],root)
            self.assertEqual([unit['value'] for unit in units],[30,70,90])
            self.assertEqual(units[0]['threads'],[0,2])
            self.assertEqual(len({unit['id'] for unit in units}),3)
            unknown=backend.cpu_processors([20,70],root/'absent')
            self.assertEqual([unit['name'] for unit in unknown],['Thread 1','Thread 2'])

    def test_per_unit_histories_continue_with_selected_process_and_do_not_mix(self):
        self.monitor.action(dict(action='select',identity=dict(pid=os.getpid(),created=backend.psutil.Process().create_time())))
        self.monitor.snapshot()
        snapshot=self.monitor.snapshot()
        units=[(card,unit) for card in snapshot['cards'] for unit in card.get('processors',[])]
        self.assertGreater(len(units),0)
        self.assertEqual(len({('unit:'+card['id']+':'+unit['id']) for card,unit in units}),len(units))
        for card,unit in units:
            self.assertEqual(len(unit['history']),2)
            self.assertEqual(unit['history'][-1],unit['value'])
            self.assertIn('unit:'+card['id']+':'+unit['id'],self.monitor.histories)

    def test_batched_requests_are_all_processed(self):
        result = subprocess.run([sys.executable, str(Path(backend.__file__))],
                                input='{"action":"startup"}\n{"action":"startup"}\n',
                                capture_output=True, text=True, timeout=8, check=True)
        messages = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(sum(message['type'] == 'startup' for message in messages), 2)

    def test_stale_identity_does_not_signal_process(self):
        child = subprocess.Popen(['sleep', '20'])
        try:
            created = backend.psutil.Process(child.pid).create_time()
            with self.assertRaises(ValueError):
                self.monitor.action(dict(action='kill', identity=dict(pid=child.pid, created=created-1)))
            self.assertIsNone(child.poll())
        finally:
            child.terminate()
            child.wait()

    def test_monitor_is_protected(self):
        with self.assertRaises(ValueError):
            self.monitor.action(dict(action='terminate', identity=dict(pid=os.getpid(), created=backend.psutil.Process().create_time())))

    def test_history_is_bounded_and_unknown_is_not_zero(self):
        for i in range(100):
            self.monitor.history('test', i)
        self.assertEqual(len(self.monitor.histories['test']), 60)
        self.assertEqual(backend.size(None), '—')


if __name__ == '__main__':
    unittest.main()
