#!/usr/bin/env python3
"""One shared sampler: CPU/RAM every 3s, filesystem every 30s, JSON lines."""
import json
import os
import time


def cpu_stat():
    with open('/proc/stat') as f:
        values = list(map(int, f.readline().split()[1:9]))
    return sum(values), values[3] + values[4]


def memory_stat():
    with open('/proc/meminfo') as f:
        values = {line.split(':')[0]: int(line.split()[1]) for line in f}
    return 100 * (1 - values['MemAvailable'] / values['MemTotal'])


def disk_stat(path='/'):
    s = os.statvfs(path)
    used = s.f_blocks - s.f_bfree
    denominator = used + s.f_bavail
    return 100 * used / denominator if denominator else None


def sample(previous):
    current = cpu_stat()
    total, idle = current[0]-previous[0], current[1]-previous[1]
    cpu = max(0, min(100, 100 * (1-idle/total))) if total > 0 else None
    return current, cpu


def run():
    previous = cpu_stat()
    disk, last_disk = None, -30
    while True:
        time.sleep(3)
        try:
            previous, cpu = sample(previous)
            memory = memory_stat()
        except (OSError, ValueError, KeyError):
            cpu, memory = None, None
        if time.monotonic()-last_disk >= 30:
            try:
                disk = disk_stat(os.environ.get('RALLEUR_DISK', '/'))
            except OSError:
                disk = None
            last_disk = time.monotonic()
        print(json.dumps({'cpu': cpu, 'memory': memory, 'disk': disk}), flush=True)


if __name__ == '__main__':
    try:
        run()
    except (BrokenPipeError, KeyboardInterrupt):
        pass
