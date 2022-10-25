#!/usr/bin/env python3

import os
import sys
import time

from rich.live import Live
from rich.table import Table

def get_gpu(phys_machs, show_user=False):
    gpu = []
    for mach in phys_machs:
        res = os.popen(f"ssh {mach} -T 'nvidia-smi --query-gpu=name,memory.free,utilization.gpu,utilization.memory,uuid --format=csv,nounits,noheader'")
        res = res.readlines()
        if show_user:
            pids = os.popen(f"ssh {mach} -T 'nvidia-smi --query-compute-apps=pid,gpu_uuid --format=csv,nounits,noheader'")
            pids = pids.readlines()
            pid_list = {}
            for pid in pids:
                pid = pid.strip().split(', ')
                if pid[1] not in pid_list:
                    pid_list[pid[1]] = [pid[0],]
                else:
                    pid_list[pid[1]].append(pid[0])
        for i in range(len(res)):
            gpu_name, free_mem, gpu_util, mem_util, uuid = res[i].strip().split(', ')
            gpu_name = gpu_name.replace('NVIDIA', '')
            gpu_name = gpu_name.replace('GeForce', '')
            gpu_name = gpu_name.strip()

            if show_user:
                gpu_user = ""
                if uuid in pid_list:
                    pids_for_uuid = ','.join(pid_list[uuid])
                    # print(pids_for_uuid)
                    users = os.popen(f"ssh {mach} -T 'ps -u -p {pids_for_uuid}'")
                    users = users.readlines()[1:]
                    uniq_users = set()
                    for u in users:
                        uniq_users.add(u.strip().split()[0])
                    gpu_user = ' '.join(uniq_users)
            if not show_user:
                gpu.append((mach,  i, gpu_name, int(free_mem), int(gpu_util), int(mem_util)))
            else:
                gpu.append((mach,  i, gpu_name, int(free_mem), int(gpu_util), int(mem_util), gpu_user))
    # Sort by free memory in descending order.
    gpu.sort(key=lambda x: -x[3])
    return gpu

def generate_table(phys_machs, show_user=False):
    table = Table(title="[bold]AntNLP GPU List", title_justify='center', caption_justify='center')
    table.add_column("IP", justify='center')
    table.add_column("ID", justify='center')
    table.add_column("Card", justify='center')
    table.add_column("FreeMem", justify='right')
    table.add_column("GPU%", justify='right')
    table.add_column("Mem%", justify='right')
    if show_user:
        table.add_column("Users", justify='left')

    gpu = get_gpu(phys_machs, show_user)
    for i in range(len(gpu)):
        gpu_now = gpu[i]
        h = (max(gpu_now[4], gpu_now[5]))/100
        r, g, b = int(h*255), int((1 - 0.7*h)*255), int(0.4*h*255)
        if show_user:
            table.add_row(
                f"[bold rgb({r},{g},{b})]{gpu_now[0]}",
                f"[bold rgb({r},{g},{b})]{gpu_now[1]}",
                f"[bold rgb({r},{g},{b})]{gpu_now[2]}",
                f"[bold rgb({r},{g},{b})]{gpu_now[3]} MB",
                f"[bold rgb({r},{g},{b})]{gpu_now[4]}%",
                f"[bold rgb({r},{g},{b})]{gpu_now[5]}%",
                f"[bold rgb({r},{g},{b})]{gpu_now[6]}")
        else:
            table.add_row(
                f"[bold rgb({r},{g},{b})]{gpu_now[0]}",
                f"[bold rgb({r},{g},{b})]{gpu_now[1]}",
                f"[bold rgb({r},{g},{b})]{gpu_now[2]}",
                f"[bold rgb({r},{g},{b})]{gpu_now[3]} MB",
                f"[bold rgb({r},{g},{b})]{gpu_now[4]}%",
                f"[bold rgb({r},{g},{b})]{gpu_now[5]}%")
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
