#!/usr/bin/env python3
"""Unprivileged, line-delimited JSON system monitor. No shell command execution."""
import configparser
import csv
import re
import datetime as dt
import json
import os
from pathlib import Path
import selectors
import shlex
import subprocess
import sys
import time
import psutil
from i18n import language, t, desktop_value


def run(args):
    env = dict(os.environ)
    if args[0] == 'systemctl' and env.get('FLAUSEN_SESSION_RUNTIME'):
        env['XDG_RUNTIME_DIR'] = env['FLAUSEN_SESSION_RUNTIME']
    return subprocess.run(args, capture_output=True, text=True, timeout=2, check=False, env=env)


def size(value, base=1024):
    if value is None:
        return '—'
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if abs(value) < base or unit == 'TB':
            return f'{value:.1f} {unit}' if unit != 'B' else f'{value:.0f} B'
        value /= base


def read_text(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return ''


def cpu_model(path='/proc/cpuinfo'):
    for line in read_text(path).splitlines():
        key, _, value = line.partition(':')
        if key.strip() in ('model name', 'Hardware') and value.strip():
            return value.strip()
    return ''


def cpu_processors(loads, root=Path('/sys/devices/system/cpu')):
    groups = {}
    online = sorted((int(path.name[3:]) for path in root.glob('cpu[0-9]*') if path.name[3:].isdigit() and read_text(path/'online')!='0'))
    ids = online if len(online)==len(loads) else list(range(len(loads)))
    for logical, load in zip(ids, loads):
        topology = root/f'cpu{logical}'/'topology'
        package, die, core = (read_text(topology/name) for name in ('physical_package_id','die_id','core_id'))
        known = bool(package and core)
        key = (package, die, core) if known else ('thread', str(logical))
        group = groups.setdefault(key, dict(physical=known, threads=[], loads=[]))
        group['threads'].append(logical)
        group['loads'].append(load)
    return [dict(id='cpu-core:'+':'.join(key), name=t('Core {number}' if group['physical'] else 'Thread {number}',number=index+1),
                 value=round(sum(group['loads'])/len(group['loads']),1),
                 detail=' · '.join(f'CPU {cpu}: {load:.1f}%' for cpu,load in zip(group['threads'],group['loads'])),
                 threads=group['threads']) for index,(key,group) in enumerate(groups.items())]


def memory_label(modules):
    def known(value):
        return value.strip() if value and value.strip().lower() not in ('unknown', 'not specified', 'none', 'other') else ''
    types, rates, models = [], [], []
    for fields in modules:
        kind = known(fields.get('type', ''))
        if kind:
            types.append(kind)
        rate = known(fields.get('configured', '')) or known(fields.get('speed', ''))
        if rate and rate.split()[0].isdigit() and int(rate.split()[0])>0:
            # SMBIOS describes transfer rate; legacy dmidecode labels may say MHz.
            rates.append(rate.split()[0]+' MT/s')
        model = ' '.join(filter(None, (known(fields.get('manufacturer', '')), known(fields.get('part', '')))))
        if model:
            capacity = fields.get('capacity', '')
            models.append((capacity+' ' if capacity else '')+model)
    counts = {model:models.count(model) for model in dict.fromkeys(models)}
    parts = list(dict.fromkeys(types))+list(dict.fromkeys(rates))+[f'{count} × {name}' for name, count in counts.items()]
    return ' · '.join(parts)


def ram_model():
    # udev's cached memory_id data is readable without access to raw SMBIOS tables.
    try:
        result = run(['udevadm', 'info', '--query=property', '--path=/sys/devices/virtual/dmi/id'])
        fields = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line) if result.returncode==0 else {}
        indices = sorted({match.group(1) for key in fields if (match:=re.fullmatch(r'MEMORY_DEVICE_(\d+)_SIZE', key))}, key=int)
        modules = []
        for index in indices:
            prefix = 'MEMORY_DEVICE_'+index+'_'
            capacity = fields.get(prefix+'SIZE', '')
            if not capacity.isdigit() or int(capacity)<=0:
                continue
            modules.append(dict(type=fields.get(prefix+'TYPE', ''), configured=fields.get(prefix+'CONFIGURED_SPEED_MTS', ''),
                                speed=fields.get(prefix+'SPEED_MTS', ''), manufacturer=fields.get(prefix+'MANUFACTURER', ''),
                                part=fields.get(prefix+'PART_NUMBER', ''), capacity=size(int(capacity))))
        label = memory_label(modules)
        if label:
            return label
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        result = run(['dmidecode', '--type', '17'])
        if result.returncode:
            return ''
        modules = []
        for block in result.stdout.split('Memory Device')[1:]:
            fields = dict(line.strip().split(': ', 1) for line in block.splitlines() if ': ' in line)
            if fields.get('Size') in ('No Module Installed', '0 MB'):
                continue
            modules.append(dict(type=fields.get('Type', ''), configured=fields.get('Configured Memory Speed', fields.get('Configured Clock Speed', '')),
                                speed=fields.get('Speed', ''), manufacturer=fields.get('Manufacturer', ''), part=fields.get('Part Number', ''), capacity=fields.get('Size', '')))
        return memory_label(modules)
    except (OSError, subprocess.TimeoutExpired):
        return ''


def number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def vulkan_gpu_types():
    devices = {}
    try:
        result = run(['vulkaninfo', '--summary'])
        for block in re.split(r'GPU\d+:', result.stdout)[1:]:
            fields = dict(line.strip().split('=', 1) for line in block.splitlines() if '=' in line)
            fields = {key.strip():value.strip() for key, value in fields.items()}
            if fields.get('deviceType') not in ('PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU', 'PHYSICAL_DEVICE_TYPE_DISCRETE_GPU'):
                continue
            devices[(int(fields['vendorID'], 16), int(fields['deviceID'], 16))] = fields['deviceType']=='PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU'
    except (OSError, KeyError, ValueError, subprocess.TimeoutExpired):
        pass
    return devices


def graphics_devices(pci, types, root=Path('/sys/class/drm')):
    devices = []
    seen = set()
    for card in root.glob('card*'):
        if not re.fullmatch(r'card\d+', card.name) or not (card/'device').exists():
            continue
        device = (card/'device').resolve()
        address = device.name
        if address in seen:
            continue
        seen.add(address)
        vendor, identifier = read_text(device/'vendor'), read_text(device/'device')
        integrated = types.get((int(vendor, 16), int(identifier, 16))) if vendor and identifier else None
        devices.append(dict(id='gpu:'+address, address=address, path=device, vendor=vendor,
                            device=pci.get(address, {}).get('name', ''), integrated=integrated))
    return sorted(devices, key=lambda d:(d['integrated'] is True, d['address']))


def pci_devices():
    try:
        result = run(['lspci', '-Dmm'])
        rows = [shlex.split(line) for line in result.stdout.splitlines()]
        return {row[0]: dict(kind=row[1], name=' '.join(row[2:4])) for row in rows if len(row) >= 4}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {}


def physical_disks(root=Path('/sys/block')):
    """Whole physical block devices, including USB/virtio; no partitions or stacks."""
    result = []
    for path in sorted(root.glob('*')):
        if (path/'partition').exists() or '/virtual/' in str(path.resolve()) or path.name.startswith(('loop', 'ram', 'zram', 'dm-', 'md')):
            continue
        try:
            capacity = int(read_text(path/'size'))*512
        except ValueError:
            continue
        if capacity <= 0:
            continue
        model = read_text(path/'device/model') or read_text(path/'device/name')
        vendor = read_text(path/'device/vendor')
        label = ' '.join(part for part in (vendor if vendor and vendor not in model else '', model) if part)
        result.append(dict(name=path.name, id='disk:'+path.name+':'+read_text(path/'diskseq'),
                           device=label or path.name, capacity=capacity))
    return result


def network_devices(pci, root=Path('/sys/class/net')):
    devices = []
    for path in sorted(root.glob('*')):
        device = path/'device'
        if not device.exists():
            continue
        name = pci.get(device.resolve().name, {}).get('name')
        if not name:
            uevent = read_text(device/'uevent')
            driver = next((line.split('=', 1)[1] for line in uevent.splitlines() if line.startswith('DRIVER=')), '')
            name = driver or t("Network adapter")
        devices.append(dict(interface=path.name, device=name))
    return devices


class Monitor:
    def __init__(self):
        self.processes = {}
        self.previous_io = {}
        self.previous_disks = {}
        self.previous_net = psutil.net_io_counters(pernic=True)
        self.cpu_device = cpu_model()
        self.ram_device = ram_model()
        self.pci = pci_devices()
        self.gpu_types = vulkan_gpu_types()
        self.nvidia = {}
        self.last = time.monotonic()
        self.selected = None
        self.extra = ''
        self.histories = {}
        self.icons = {}
        self.desktop_names = {}
        self.applications = set()
        self.gpu = {}
        self.gpu_time = 0
        for directory in (Path('/usr/share/applications'), Path.home()/'.local/share/applications'):
            for path in directory.glob('*.desktop'):
                try:
                    config = configparser.ConfigParser(interpolation=None, strict=False)
                    config.read(path)
                    app = config['Desktop Entry']
                    executable = Path(app.get('TryExec', app.get('Exec', '').split(' ')[0])).name.lower()
                    if executable:
                        self.icons[executable] = app.get('Icon', 'application-x-executable')
                        self.desktop_names[executable] = desktop_value(app, 'Name') or executable
                        if app.get('NoDisplay', 'false').lower() != 'true' and app.get('Hidden', 'false').lower() != 'true':
                            self.applications.add(executable)
                except (OSError, configparser.Error, KeyError):
                    pass
        psutil.cpu_percent()

    def history(self, key, value):
        values = self.histories.setdefault(key, [])
        values.append(value)
        del values[:-60]
        return list(values)

    def identity(self, identity):
        process = psutil.Process(int(identity['pid']))
        if abs(process.create_time() - float(identity['created'])) > .001:
            raise ValueError(t("This process has been replaced. Select it again."))
        return process

    def action(self, request):
        action = request.get('action')
        if action == 'select':
            self.selected = request.get('identity')
            self.extra = request.get('extra', '')
        elif action in ('terminate', 'kill', 'stop', 'resume', 'priority'):
            process = self.identity(request['identity'])
            if process.pid in (1, os.getpid(), os.getppid()):
                raise ValueError(t("This process is protected by Task Manager."))
            if process.uids().real != os.getuid():
                raise PermissionError(t("Only your own processes can be changed here."))
            if action == 'priority':
                process.nice(int(request['value']))
            else:
                getattr(process, {'terminate': 'terminate', 'kill': 'kill', 'stop': 'suspend', 'resume': 'resume'}[action])()
        elif action == 'startup-toggle':
            name = Path(request['name']).name
            source = self.autostart_paths().get(name)
            if source is None or name != request['name']:
                raise ValueError(t("This startup entry no longer exists."))
            config = configparser.ConfigParser(interpolation=None, strict=False)
            config.optionxform = str
            config.read(source)
            config['Desktop Entry']['Hidden'] = 'false' if request['enabled'] else 'true'
            target = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))/'autostart'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            # Keep the complete original entry when creating a user override.
            temp = target.with_suffix('.desktop.flausen-tmp')
            with temp.open('w') as stream:
                config.write(stream, space_around_delimiters=False)
            temp.replace(target)
        elif action == 'service':
            name = request['name']
            operation = request['operation']
            if operation not in ('start', 'stop', 'restart') or not name.endswith('.service') or name.startswith('-'):
                raise ValueError(t("Invalid service action."))
            result = run(['systemctl', '--user', operation, '--', name])
            if result.returncode:
                raise ValueError(result.stderr.strip() or t("Service action failed."))

    def autostart_paths(self):
        paths = {}
        dirs = [Path(p)/'autostart' for p in os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg').split(':')]
        dirs.reverse()
        dirs.append(Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))/'autostart')
        for directory in dirs:
            paths.update({p.name: p for p in directory.glob('*.desktop')})
        return paths

    def startup(self):
        entries = []
        for name, path in self.autostart_paths().items():
            try:
                config = configparser.ConfigParser(interpolation=None, strict=False)
                config.read(path)
                app = config['Desktop Entry']
                if app.get('Type', 'Application') != 'Application':
                    continue
                entries.append(dict(id=name, name=desktop_value(app,'Name') or name, description=desktop_value(app,'Comment'),
                                    command=app.get('Exec', ''), icon=app.get('Icon', 'system-run'),
                                    enabled=app.get('Hidden', 'false').lower() != 'true',
                                    condition=app.get('OnlyShowIn', app.get('NotShowIn', ''))))
            except (OSError, KeyError, configparser.Error):
                pass
        return sorted(entries, key=lambda row: row['name'].lower())

    def services(self):
        result = run(['systemctl', '--user', 'list-units', '--type=service', '--all', '--output=json', '--no-pager'])
        if result.returncode:
            raise ValueError(result.stderr.strip())
        return [dict(name=row['unit'], description=row.get('description', ''), status=row.get('sub', ''),
                     active=row.get('active', '')) for row in json.loads(result.stdout)]

    @staticmethod
    def safe_read(getter):
        try:
            return getter()
        except psutil.AccessDenied:
            return t("Access denied")

    def disk_cards(self, elapsed):
        counters = psutil.disk_io_counters(perdisk=True) or {}
        devices = physical_disks()
        cards, previous = [], {}
        for device in devices:
            key = device['id']
            current = counters.get(device['name'])
            old = self.previous_disks.get(key)
            read = max(0, current.read_bytes-old.read_bytes)/elapsed if current and old else None
            write = max(0, current.write_bytes-old.write_bytes)/elapsed if current and old else None
            busy = min(100, max(0, current.busy_time-old.busy_time)/elapsed/10) if current and old and hasattr(current, 'busy_time') else None
            if current:
                previous[key] = current
            cards.append(dict(id=key, kind='disk', name=t("Disk")+(' · '+device['name'] if len(devices)>1 else ''),
                              device=f"{device['device']} · {size(device['capacity'], base=1000)}", path='/dev/'+device['name'],
                              value=f'{busy:.0f}%' if busy is not None else '', percent=busy,
                              detail=' · '.join(([t('Read {rate}/s',rate=size(read))] if read is not None else [])+([t('Write {rate}/s',rate=size(write))] if write is not None else [])), color='#edb751'))
        self.previous_disks = previous
        if not cards:
            cards.append(dict(id='disk-unavailable', kind='disk', name=t("Disk"), device='',
                              value='', percent=None, detail='', color='#edb751'))
        return cards

    def gpu_cards(self, now):
        if now-self.gpu_time >= 3:
            self.gpu_time = now
            self.nvidia = {}
            try:
                result = run(['nvidia-smi', '--query-gpu=pci.bus_id,name,utilization.gpu,memory.used,memory.total,temperature.gpu,utilization.memory,utilization.encoder,utilization.decoder,utilization.jpeg,utilization.ofa', '--format=csv,noheader,nounits'])
                if result.returncode:
                    result = run(['nvidia-smi', '--query-gpu=pci.bus_id,name,utilization.gpu,memory.used,memory.total,temperature.gpu', '--format=csv,noheader,nounits'])
                for row in csv.reader(result.stdout.splitlines(), skipinitialspace=True):
                    if len(row) not in (6,11):
                        continue
                    domain, bus, function = row[0].lower().split(':')
                    address = f'{int(domain,16):04x}:{bus}:{function}'
                    self.nvidia[address] = dict(name=row[1], percent=number(row[2]), used=number(row[3]), total=number(row[4]), temperature=number(row[5]), engines={key:number(value) for key,value in zip(('memory','encoder','decoder','jpeg','ofa'),row[6:])})
            except (OSError, ValueError, subprocess.TimeoutExpired):
                pass
        cards = []
        devices = graphics_devices(self.pci, self.gpu_types)
        for index, device in enumerate(devices):
            path = device['path']
            sample = self.nvidia.get(device['address'], {})
            percent = sample.get('percent') if sample else number(read_text(path/'gpu_busy_percent'))
            used = sample.get('used')*1024**2 if sample.get('used') is not None else number(read_text(path/'mem_info_vram_used'))
            total = sample.get('total')*1024**2 if sample.get('total') is not None else number(read_text(path/'mem_info_vram_total'))
            temperature = sample.get('temperature')
            frequency = None
            if temperature is None:
                for hwmon in (path/'hwmon').glob('hwmon*'):
                    temperature = number(read_text(hwmon/'temp1_input'))
                    if temperature is not None:
                        temperature /= 1000
                    frequency = number(read_text(hwmon/'freq1_input'))
                    if frequency is not None:
                        frequency /= 10**6
                    break
            parts = []
            if used is not None and total:
                parts.append(f'{size(used)} / {size(total)}'+(' '+t('reserved') if device['integrated'] else ' VRAM'))
            if frequency is not None:
                parts.append(f'{frequency:.0f} MHz')
            if temperature is not None:
                parts.append(f'{temperature:.0f} °C')
            label = sample.get('name') or device['device']
            name = t("GPU · Integrated") if device['integrated'] else ('GPU' if len(devices)==1 else f'GPU {index+1}')
            processors = []
            if percent is not None:
                processors.append(dict(id='graphics',name=t("Graphics"),value=percent,detail=t("Overall graphics utilization")))
            for key, engine_name, description in [('memory',t("Memory"),t("Memory I/O utilization")),('encoder',t("Encoder"),t("Video encoding")),('decoder',t("Decoder"),t("Video decoding")),('jpeg',t("JPEG"),t("JPEG decoding")),('ofa',t("Opt. Flow"),t("Optical flow accelerator"))]:
                value = sample.get('engines',{}).get(key)
                if value is not None:
                    processors.append(dict(id=key,name=engine_name,value=value,detail=description))
            video = number(read_text(path/'vcn_busy_percent'))
            if video is not None:
                processors.append(dict(id='vcn',name=t("Video"),value=video,detail=t("Video codec engine (VCN)")))
            cards.append(dict(id=device['id'], kind='gpu', processors=processors, name=name, device=label, integrated=device['integrated'],
                              value=f'{percent:.0f}%' if percent is not None else '', percent=percent,
                              detail=' · '.join(parts), color='#b995ed' if device['integrated'] else '#f47c69'))
        self.gpu = next((dict(name=card['device']) for card in cards if not card['integrated']), {})
        return cards

    def snapshot(self):
        language.refresh()
        now = time.monotonic()
        elapsed = max(.1, now - self.last)
        self.last = now
        alive, rows = {}, []
        threads = 0
        for process in psutil.process_iter():
            try:
                with process.oneshot():
                    pid, created = process.pid, process.create_time()
                    key = (pid, created)
                    cached = self.processes.get(key, process)
                    cpu = cached.cpu_percent() / max(1, psutil.cpu_count())
                    name = process.name()
                    exe = process.exe() if process.uids().real == os.getuid() else ''
                    try:
                        io = process.io_counters()
                        old = self.previous_io.get(key)
                        read = max(0, io.read_bytes-old[0])/elapsed if old else 0
                        write = max(0, io.write_bytes-old[1])/elapsed if old else 0
                        self.previous_io[key] = (io.read_bytes, io.write_bytes)
                    except (psutil.Error, OSError):
                        read = write = None
                    row = dict(pid=pid, created=created, ppid=process.ppid(), rawName=name,
                               name=self.desktop_names.get(Path(exe).name.lower(), name),
                               icon=self.icons.get(Path(exe).name.lower(), 'application-x-executable'),
                               cpu=round(cpu, 1), memory=process.memory_info().rss,
                               read=read, write=write, user=process.username(), status=process.status(),
                               own=process.uids().real == os.getuid(), application=process.uids().real == os.getuid() and Path(exe).name.lower() in self.applications, count=1, children=[])
                    rows.append(row)
                    threads += process.num_threads()
                    alive[key] = cached
            except (psutil.Error, OSError):
                continue
        self.processes = alive
        self.previous_io = {key: value for key, value in self.previous_io.items() if key in alive}
        by_pid = {row['pid']: row for row in rows}
        # Group related descendants of an application. Kernel/system tasks stay separate.
        groups = {}
        for row in rows:
            ancestor = row
            seen = {row['pid']}
            while ancestor['ppid'] in by_pid:
                parent = by_pid[ancestor['ppid']]
                if parent['pid'] in seen or parent['rawName'] != row['rawName']:
                    break
                seen.add(parent['pid'])
                ancestor = parent
            root = ancestor['pid']
            if root not in groups:
                groups[root] = dict(ancestor, children=[], count=0, cpu=0., memory=0, read=0., write=0.)
            group = groups[root]
            group['count'] += 1
            for metric in ('cpu', 'memory', 'read', 'write'):
                group[metric] = None if group[metric] is None or row[metric] is None else group[metric] + row[metric]
            if row['pid'] != root:
                group['children'].append(row)
        memory = psutil.virtual_memory()
        disk_cards = self.disk_cards(elapsed)
        adapters = network_devices(self.pci)
        network = psutil.net_io_counters(pernic=True)
        physical_names = [adapter['interface'] for adapter in adapters if adapter['interface'] in network]
        comparable = [name for name in physical_names if name in self.previous_net]
        down = sum(max(0, network[name].bytes_recv-self.previous_net[name].bytes_recv) for name in comparable)/elapsed if comparable else None
        up = sum(max(0, network[name].bytes_sent-self.previous_net[name].bytes_sent) for name in comparable)/elapsed if comparable else None
        self.previous_net = network
        network_label = ' · '.join(f"{adapter['device']} ({adapter['interface']})" for adapter in adapters) or ''
        cpu = psutil.cpu_percent()
        frequency = psutil.cpu_freq()
        gpu_cards = self.gpu_cards(now)
        sensors = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
        temps = [entry.current for key, entries in sensors.items() if key in ('coretemp', 'k10temp', 'cpu_thermal') for entry in entries]
        logical_loads = psutil.cpu_percent(percpu=True)
        cpu_units = cpu_processors(logical_loads)
        cards = [dict(id='cpu', kind='cpu', processors=cpu_units, name='CPU', device=self.cpu_device, value=f'{cpu:.0f}%', percent=cpu, detail=' · '.join(([f'{frequency.current/1000:.2f} GHz'] if frequency else [])+([f'{max(temps):.0f} °C'] if temps else [])), color='#479cff'),
                 dict(id='memory', kind='memory', name=t("Memory"), device=self.ram_device, value=f'{size(memory.used)} / {size(memory.total)}', percent=memory.percent, detail=t('{percent}% in use',percent=f'{memory.percent:.0f}'), color='#a7cf7c'),
                 *gpu_cards,
                 *disk_cards,
                 dict(id='network', kind='network', name=t("Network"), device=network_label, value=f'↓ {size(down)}/s' if down is not None else '', percent=None, detail=f'↑ {size(up)}/s' if up is not None else '', color='#69b5e9')]
        current_ids = {card['id'] for card in cards}
        for card in cards:
            card['history'] = self.history(card['id'], down if card['kind'] == 'network' else card['percent'])
            for unit in card.get('processors', []):
                key = 'unit:'+card['id']+':'+unit['id']
                current_ids.add(key)
                unit['history'] = self.history(key, unit['value'])
        self.histories = {key: values for key, values in self.histories.items() if key in current_ids or key.startswith(('cpu:', 'mem:'))}
        detail = None
        if self.selected:
            try:
                process = self.identity(self.selected)
                row = by_pid.get(process.pid)
                if row:
                    with process.oneshot():
                        try:
                            files = [dict(name=f.path, value=f'FD {f.fd}') for f in process.open_files()] if self.extra == 'files' else []
                            connections = [dict(name=f'{c.laddr.ip}:{c.laddr.port}' if c.laddr else '—', value=(f'{c.raddr.ip}:{c.raddr.port}' if c.raddr else '—')+' · '+c.status) for c in process.net_connections(kind='inet')] if self.extra == 'connections' else []
                            extra_error = ''
                        except (psutil.Error, OSError):
                            files, connections, extra_error = [], [], t("Access to these details is not permitted.")
                        detail = dict(row, threads=process.num_threads(), priority=process.nice(),
                                      started=dt.datetime.fromtimestamp(process.create_time()).strftime('%H:%M:%S'),
                                      path=self.safe_read(process.exe), command=self.safe_read(lambda: ' '.join(process.cmdline())), files=files, connections=connections,
                                      extraError=extra_error,
                                      cpuHistory=self.history('cpu:'+str(process.pid)+':'+str(process.create_time()), row['cpu']),
                                      memoryHistory=self.history('mem:'+str(process.pid)+':'+str(process.create_time()), row['memory']))
            except (psutil.Error, OSError, ValueError):
                detail = dict(exited=True, pid=self.selected['pid'])
        if self.selected:
            suffix = str(self.selected['pid'])+':'+str(self.selected['created'])
            self.histories = {k:v for k,v in self.histories.items() if k in current_ids or (k.startswith(('cpu:', 'mem:')) and k.endswith(suffix))}
        return dict(type='snapshot',language=language.language,locale=language.locale,translations=language.messages,processes=list(groups.values()), cards=cards, detail=detail,
                    count=len(rows), threads=threads, uptime=int(time.time()-psutil.boot_time()),
                    load=' · '.join(f'{load:.1f}' for load in os.getloadavg()),
                    cores=logical_loads, swap=psutil.swap_memory().percent,
                    gpu=self.gpu, updated=dt.datetime.now().strftime('%H:%M:%S'))


def emit(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def main():
    monitor = Monitor()
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    interval, deadline = 1., 0.
    pending = b''
    while True:
        if time.monotonic() >= deadline:
            sample_started = time.monotonic()
            try:
                emit(monitor.snapshot())
            except Exception as error:
                emit(dict(type='error', message=str(error)))
            deadline = sample_started+interval
        for key, _ in selector.select(max(0, deadline-time.monotonic())):
            chunk = os.read(key.fileobj.fileno(), 65536)
            if not chunk:
                return
            pending += chunk
            while b'\n' in pending:
                line, pending = pending.split(b'\n', 1)
                try:
                    request = json.loads(line)
                    action = request.get('action')
                    if action == 'interval':
                        interval = min(10., max(.5, float(request['value'])))
                    elif action in ('startup', 'services'):
                        emit(dict(type=action, rows=getattr(monitor, action)()))
                    else:
                        monitor.action(request)
                        if action != 'select':
                            emit(dict(type='notice', message=t("Change applied.")))
                    deadline = 0
                except Exception as error:
                    emit(dict(type='error', message=str(error)))


if __name__ == '__main__':
    main()
