import psutil
import time

def collect_process_data():

    """Collect real CPU% and memory usage after warm-up and delay."""

    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1.0)

    processes = []
    for p in psutil.process_iter(attrs=["pid", "ppid", "name", "memory_info"]):
        try:
            with p.oneshot():
                processes.append({
                    "pid": p.pid,
                    "ppid": p.ppid(),
                    "name": p.name(),
                    "cpu_percent": p.cpu_percent(interval=None),
                    "rss_bytes": p.memory_info().rss//10000
                })
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes
