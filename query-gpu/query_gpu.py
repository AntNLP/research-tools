#!/usr/bin/env python3

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import subprocess
import sys
import time
from typing import List, Dict

from rich.live import Live
from rich.table import Table

cmd_gpu = 'nvidia-smi --query-gpu=name,memory.free,utilization.gpu,utilization.memory,uuid --format=csv,nounits,noheader'
cmd_app = 'nvidia-smi --query-compute-apps=pid,used_gpu_memory,gpu_uuid --format=csv,nounits,noheader'
cmd_ps = 'ps -up'

# run command on remote machine using ssh, return lines of output
def ssh_run(machine: str, command: str) -> List[str]:
    return subprocess.run(f"ssh {machine} -T '{command}'",
        shell=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    ).stdout.splitlines()

# get gpu data on one machine
def get_data(mach, show_user=False):
    data = []
    if show_user:
        # get app (user & mem) in each card
        app_rst = [app.strip().split(', ') for app in ssh_run(mach, cmd_app)]
        card2apps = defaultdict(list)
        if len(app_rst) > 0:
            pids = ' '.join(pid for pid, _, _ in app_rst)
            ps_rst = [ps.strip().split()[:2] for ps in ssh_run(mach, f"{cmd_ps} {pids}")[1:]]  # throw header & get first 2 cols
            pid2user = {}
            for user, pid in ps_rst:
                pid2user[pid] = user
            for pid, mem, gpu_uuid in app_rst:
                card2apps[gpu_uuid].append({
                    'username': pid2user[pid],
                    'user_mem': int(mem)
                })
        # sort per card
        for uuid in card2apps.keys():
            card2apps[uuid].sort(key=lambda x: -x['user_mem'])
    gpu_rst = [gpu.strip().split(', ') for gpu in ssh_run(mach, cmd_gpu)]
    for idx, (gpu_name, free_mem, gpu_util, mem_util, uuid) in enumerate(gpu_rst):
        gpu_name = f"[{idx}] {gpu_name.replace('NVIDIA', '').replace('GeForce', '').strip()}"
        datum = {
            'idx': idx,  # only used in sort
            'machine': mach,
            'gpu_name': gpu_name,
            'free_mem': int(free_mem),
            'gpu_util': int(gpu_util),
            'mem_util': int(mem_util),
        }
        if show_user:
            datum['apps'] = card2apps[uuid]
        data.append(datum)
    return data

def get_all(phys_machs, show_user=False):
    rst = []
    with ProcessPoolExecutor(max_workers=len(phys_machs)) as pool:
        # call get_data() concurrently using proc pool
        for data in pool.map(get_data, phys_machs, [show_user] * len(phys_machs)):
            rst += data
    # Sort by free memory in descending order, then by name in ascending order.
    rst.sort(key=lambda x: (-x['free_mem'], x['machine'], x['idx']))
    return rst

def generate_table(phys_machs, show_user=False):
    table = Table(title="[bold]AntNLP GPU List", title_justify='center', caption_justify='center')
    table.add_column("IP", justify='center')
    table.add_column("Card", justify='center')
    table.add_column("FreeMem", justify='right')
    table.add_column("GPU%", justify='right')
    table.add_column("Mem%", justify='right')
    if show_user:
        table.add_column("Users", justify='left')

    data = get_all(phys_machs, show_user)
    for gpu in data:
        h = (max(gpu['gpu_util'], gpu['mem_util']))/100
        r, g, b = int(h*255), int((1 - 0.7*h)*255), int(0.4*h*255)
        row = [
            f"[bold rgb({r},{g},{b})]{gpu['machine']}",
            f"[bold rgb({r},{g},{b})]{gpu['gpu_name']}",
            f"[bold rgb({r},{g},{b})]{gpu['free_mem']} MB",
            f"[bold rgb({r},{g},{b})]{gpu['gpu_util']} %",
            f"[bold rgb({r},{g},{b})]{gpu['mem_util']} %",
        ]
        if show_user:
            row.append(' '.join(f"[bright_black]{app['username']}[white]([yellow]{app['user_mem']}M[white])[/white]" for app in gpu['apps']))
        table.add_row(*row)
    return table

if __name__ == '__main__':
    err_msg = f"No physical machine arguments. Usage: {sys.argv[0]} [-u] host1 host2 ..."
    assert len(sys.argv) != 1, err_msg
    assert not (len(sys.argv) == 2 and sys.argv[1] == '-u'), err_msg

    if sys.argv[1] == '-u':
        phys_machs = sys.argv[2:]
        show_user = True
    else:
        phys_machs = sys.argv[1:]
        show_user = False

    with Live(generate_table(phys_machs, show_user), refresh_per_second=1) as live:
        for i in range(10):
            live.update(generate_table(phys_machs, show_user))
            time.sleep(5)
