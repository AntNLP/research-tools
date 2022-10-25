#!/usr/bin/env python3

import os
import sys
import time

from rich.live import Live
from rich.table import Table

def get_gpu(phys_machs):
    gpu = []
    for mach in phys_machs:
        res = os.popen(f"ssh {mach} -T 'nvidia-smi --query-gpu=name,memory.free,utilization.gpu,utilization.memory --format=csv,nounits,noheader'")
        res = res.readlines()
        for i in range(len(res)):
            gpu_name, free_mem, gpu_util, mem_util = res[i].split(', ')
            gpu_name = gpu_name.replace('NVIDIA', '')
            gpu_name = gpu_name.replace('GeForce', '')
            gpu_name = gpu_name.strip()
            gpu.append((mach,  i, gpu_name, int(free_mem), int(gpu_util), int(mem_util)))
    # Sort by free memory in descending order.
    gpu.sort(key=lambda x: -x[3])
    return gpu

def generate_table(phys_machs):
    table = Table(title="[bold]AntNLP GPU List", title_justify='center', caption_justify='center')
    table.add_column("IP")
    table.add_column("ID")
    table.add_column("Card", justify='center')
    table.add_column("FreeMem", justify='right')
    table.add_column("GPU%", justify='right')
    table.add_column("Mem%", justify='right')
    gpu = get_gpu(phys_machs)
    for i in range(len(gpu)):
        gpu_now = list(map(lambda x:str(x), gpu[i]))
        h = (max(gpu[i][-1], gpu[i][-2]))/100
        r, g, b = int(h*255), int((1 - 0.7*h)*255), int(0.4*h*255)
        table.add_row(
            f"[bold rgb({r},{g},{b})]{gpu_now[0]}",
            f"[bold rgb({r},{g},{b})]{gpu_now[1]}",
            f"[bold rgb({r},{g},{b})]{gpu_now[2]}",
            f"[bold rgb({r},{g},{b})]{gpu_now[3]} MB",
            f"[bold rgb({r},{g},{b})]{gpu_now[4]}",
            f"[bold rgb({r},{g},{b})]{gpu_now[5]}",)
    return table

n_phys_machs = len(sys.argv)
assert n_phys_machs != 1, "No physical machine arguments."
phys_machs = sys.argv[1:]

with Live(generate_table(phys_machs), refresh_per_second=1) as live:
    for i in range(10):
        live.update(generate_table(phys_machs))
        time.sleep(5)
