#!/usr/bin/env python3
"""Read-only per-application spectrum taps; never changes audio routing or volume."""
import asyncio
import contextlib
import ctypes
import json
import math
import signal
import struct
import sys
import time

MAX_APPS = 5
# Orange, blue, petrol, yellow and red from the Ralleur accent palette.
ACCENTS = ("#E56D2F", "#2563C9", "#278F8B", "#E4AD22", "#DF493F")
BARS = 32
RATE = 22050
ZERO = [0.0] * BARS


def app_key(stream):
    props = stream.get('properties', {})
    return props.get('application.name') or props.get('application.process.binary') or str(stream['index'])


def choose_apps(streams, previous):
    groups = {}
    for stream in streams:
        if stream.get('corked'):
            continue
        groups.setdefault(app_key(stream), []).append(stream)
    # Stable side assignment, with the requested browser/game pairing preferred.
    names = sorted(groups, key=lambda n: (0 if 'chromium' in n.lower() else 1 if 'warcraft' in n.lower() else 2, n.lower()))
    selected = [name for name in previous if name in groups]
    selected.extend(name for name in names if name not in selected)
    return selected[:MAX_APPS], groups


def assign_colors(selected, previous):
    colors = {name: previous[name] for name in selected if name in previous}
    available = [color for color in ACCENTS if color not in colors.values()]
    for name in selected:
        if name not in colors:
            colors[name] = available.pop(0)
    return colors


async def pactl(kind):
    proc = await asyncio.create_subprocess_exec('pactl', '-f', 'json', 'list', kind,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), 3)
        if proc.returncode:
            raise RuntimeError('pactl unavailable')
        return json.loads(out)
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()


class Cava:
    def __init__(self):
        self.lib = ctypes.CDLL('libcava.so')
        self.lib.cava_init.argtypes = [ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.cava_init.restype = ctypes.c_void_p
        self.lib.cava_execute.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_double), ctypes.c_void_p]
        self.lib.cava_destroy.argtypes = [ctypes.c_void_p]
        self.plan = self.lib.cava_init(BARS, RATE, 1, 1, .85, 50, 10000, 0)
        if not self.plan:
            raise RuntimeError('cava_init failed')
        self.output = (ctypes.c_double * BARS)()

    def process(self, data):
        samples = struct.unpack('<' + 'h' * (len(data) // 2), data)
        buf = (ctypes.c_double * len(samples))(*(v / 32768 for v in samples))
        self.lib.cava_execute(buf, len(samples), self.output, self.plan)
        # Keep exact silence silent, despite Cava's release/sensitivity history.
        if max(map(abs, samples), default=0) < 2:
            return ZERO[:]
        return [min(1., max(0., v)) if math.isfinite(v) else 0. for v in self.output]

    def close(self):
        self.lib.cava_destroy(self.plan)


class Tap:
    def __init__(self, stream, monitor):
        self.stream = stream
        self.monitor = monitor
        self.values = ZERO[:]
        self.updated = 0
        self.proc = None
        self.task = asyncio.create_task(self.run())

    async def run(self):
        cava = None
        try:
            cava = Cava()
            self.proc = await asyncio.create_subprocess_exec('parec', '--raw', '--format=s16le',
                f'--rate={RATE}', '--channels=1', '--latency-msec=30',
                '--client-name=flausen-app-visualiser', '--stream-name=App spectrum',
                f'--device={self.monitor}', f'--monitor-stream={self.stream["index"]}',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            while True:
                data = await self.proc.stdout.readexactly(1024)
                self.values = cava.process(data)
                self.updated = time.monotonic()
        except (asyncio.IncompleteReadError, OSError, RuntimeError) as error:
            print(f'app-visualiser: {error}', file=sys.stderr)
        finally:
            if self.proc and self.proc.returncode is None:
                self.proc.terminate()
                await self.proc.wait()
            if cava:
                cava.close()
            self.values = ZERO[:]

    async def close(self):
        self.task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self.task

    def frame(self):
        if self.stream.get('mute') or time.monotonic() - self.updated > .3:
            return ZERO[:]
        return self.values


async def main():
    taps, selected, groups, colors = {}, [], {}, {}
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    async def discover():
        nonlocal selected, groups, colors
        while not stop.is_set():
            try:
                streams, sinks = await asyncio.gather(pactl('sink-inputs'), pactl('sinks'))
                selected, groups = choose_apps(streams, selected)
                colors = assign_colors(selected, colors)
                monitors = {s['index']: s['monitor_source'] for s in sinks}
                wanted = {s['index']: s for name in selected for s in groups[name]
                          if s['sink'] in monitors}
                for idx in list(taps):
                    tap = taps[idx]
                    if idx not in wanted or tap.monitor != monitors[wanted[idx]['sink']] or tap.task.done():
                        await taps.pop(idx).close()
                for idx, stream in wanted.items():
                    if idx not in taps:
                        taps[idx] = Tap(stream, monitors[stream['sink']])
                    taps[idx].stream = stream
            except (OSError, RuntimeError, ValueError, asyncio.TimeoutError) as error:
                print(f'app-visualiser discovery: {error}', file=sys.stderr)
                selected, groups = [], {}
                for tap in list(taps.values()):
                    await tap.close()
                taps.clear()
            try:
                await asyncio.wait_for(stop.wait(), .75)
            except asyncio.TimeoutError:
                pass

    discovery = asyncio.create_task(discover())
    try:
        while not stop.is_set():
            apps = []
            for name in selected:
                frames = [taps[s['index']].frame() for s in groups.get(name, []) if s['index'] in taps]
                values = [max(v) for v in zip(*frames)] if frames else ZERO[:]
                apps.append({'name': name, 'color': colors[name], 'values': [round(v, 4) for v in values]})
            print(json.dumps({'apps': apps}, separators=(',', ':')), flush=True)
            try:
                await asyncio.wait_for(stop.wait(), 1 / 30)
            except asyncio.TimeoutError:
                pass
    finally:
        discovery.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await discovery
        for tap in list(taps.values()):
            await tap.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except BrokenPipeError:
        pass
