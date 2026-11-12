#!/usr/bin/env python3
"""Verify independent spectra on an inaudible, temporary null sink."""
import argparse
import asyncio
import importlib.util
import json
import math
from pathlib import Path
import struct
import subprocess
import time

spec = importlib.util.spec_from_file_location('app_visualiser', Path(__file__).parents[1] / 'overlay/scripts/app-visualiser.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def pactl(*args):
    return subprocess.check_output(['pactl', *args], text=True).strip()


async def check(live_ui=False):
    sink = 'flausen_spectrum_test_' + str(time.time_ns())
    module_id = pactl('load-module', 'module-null-sink', f'sink_name={sink}')
    procs, writers, taps = [], [], []
    enabled = [True] * module.MAX_APPS
    try:
        async def write(proc, side, hz):
            offset = 0
            while True:
                data = struct.pack('<512h', *(int(8000 * math.sin(2 * math.pi * hz * (offset + i) / module.RATE)) if enabled[side] else 0 for i in range(512)))
                proc.stdin.write(data)
                await proc.stdin.drain()
                offset += 512
                await asyncio.sleep(512 / module.RATE)

        for side, hz in enumerate((100, 300, 900, 2700, 7000)):
            proc = await asyncio.create_subprocess_exec('pacat', '--playback', '--raw',
                '--format=s16le', f'--rate={module.RATE}', '--channels=1',
                f'--device={sink}', f'--property=application.name=SpectrumTest{side}',
                stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            procs.append(proc)
            writers.append(asyncio.create_task(write(proc, side, hz)))
        await asyncio.sleep(.6)
        streams = await module.pactl('sink-inputs')
        for side in range(module.MAX_APPS):
            stream = next(s for s in streams if module.app_key(s) == f'SpectrumTest{side}')
            taps.append(module.Tap(stream, sink + '.monitor'))
        await asyncio.sleep(2)
        frames = [t.frame() for t in taps]
        peaks = [max(range(module.BARS), key=f.__getitem__) for f in frames]
        assert all(max(f) > .005 for f in frames), frames
        assert all(b > a for a, b in zip(peaks, peaks[1:])), peaks
        live = None
        if live_ui:
            shell = str(Path.home() / '.config/quickshell/caelestia')
            live = json.loads(subprocess.check_output(['quickshell', 'ipc', '-p', shell,
                'call', 'ralleurAppVisualiser', 'inspect'], text=True))
            assert live['split'] and len(live['apps']) == 5, live
            assert len({app['color'] for app in live['apps']}) == 5, live
            subprocess.run(['spectacle', '-b', '-n', '-f', '-o', '/tmp/ralleur-five-app-visualiser.png'], check=True)
        enabled[0] = False
        await asyncio.sleep(.8)
        levels = [max(t.frame()) for t in taps]
        assert levels[0] == 0 and all(v > .005 for v in levels[1:]), levels
        selected, groups = module.choose_apps(streams, [])
        one = [{'index': 1, 'properties': {'application.name': 'Chromium'}}]
        assert module.choose_apps(one, [])[0] == ['Chromium']
        pair = one + [{'index': 2, 'properties': {'application.name': 'World of Warcraft'}}]
        assert module.choose_apps(pair, [])[0] == ['Chromium', 'World of Warcraft']
        assert module.choose_apps(pair[::-1], ['Chromium', 'World of Warcraft'])[0] == ['Chromium', 'World of Warcraft']
        six = [{'index': i, 'properties': {'application.name': f'App{i}'}} for i in range(6)]
        names, _ = module.choose_apps(six[:5], [])
        colors = module.assign_colors(names, {})
        assert len(names) == len(set(colors.values())) == 5
        assert module.choose_apps(six, names)[0] == names
        survivors, _ = module.choose_apps(six[1:], names)
        next_colors = module.assign_colors(survivors, colors)
        assert survivors == ['App1', 'App2', 'App3', 'App4', 'App5']
        assert all(next_colors[n] == colors[n] for n in names[1:])
        assert next_colors['App5'] == colors['App0']
        remaining, _ = module.choose_apps(six[4:5], survivors)
        assert len(remaining) == 1  # QML returns to its orange combined spectrum.
        assert len(module.choose_apps([six[0], dict(six[0], index=10)], [])[0]) == 1
        assert module.choose_apps([dict(six[0], corked=True)], [])[0] == []
        print(json.dumps({'independentFrequencyPeaks': peaks, 'firstSilenced': levels[0],
                          'othersStillActive': levels[1:], 'singleAppFallback': True,
                          'sixthAppWaits': True, 'stableColorsAfterRemoval': True,
                          'waitingAppPromoted': True, 'liveUI': live, 'audibleTestOutput': False}, indent=2))
    finally:
        for writer in writers:
            writer.cancel()
        await asyncio.gather(*writers, return_exceptions=True)
        for tap in taps:
            await tap.close()
        for proc in procs:
            if proc.returncode is None:
                proc.terminate()
            await proc.wait()
        pactl('unload-module', module_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live-ui', action='store_true')
    asyncio.run(check(parser.parse_args().live_ui))
