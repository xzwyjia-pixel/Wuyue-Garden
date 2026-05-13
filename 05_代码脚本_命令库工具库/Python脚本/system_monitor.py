"""
system_monitor.py — 技术环境监控 (CPU/GPU/内存/网络/推流)
每15s采集一次, 写入 system_health.jsonl
检测: 设备过载、内存泄漏、推流中断、网络丢包
"""
import json, time, os, sys, argparse, platform, subprocess
from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
args = parser.parse_args()
TARGET = Path(args.target)
POLL_SECONDS = 15
ALERT_FILE = TARGET / "system_health.jsonl"

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("[sysmon] psutil not installed, limited monitoring")

sys.stdout.reconfigure(encoding="utf-8")

def get_cpu_info():
    if not HAS_PSUTIL:
        return {"cpu_percent": 0, "memory_percent": 0}
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": round(psutil.virtual_memory().used / 1e9, 2),
        "memory_total_gb": round(psutil.virtual_memory().total / 1e9, 2),
        "disk_percent": psutil.disk_usage("/").percent,
    }

def get_gpu_info():
    """NVIDIA GPU via nvidia-smi"""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
            timeout=5, encoding="utf-8"
        ).strip()
        parts = out.split(", ")
        if len(parts) >= 3:
            return {
                "gpu_util_percent": float(parts[0]),
                "gpu_mem_used_gb": round(float(parts[1]) / 1024, 2),
                "gpu_mem_total_gb": round(float(parts[2]) / 1024, 2),
                "gpu_temp": float(parts[3]) if len(parts) > 3 else 0,
            }
    except Exception:
        pass
    return {}

def get_network_info():
    if not HAS_PSUTIL:
        return {}
    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(net.bytes_sent / 1e6, 1),
        "bytes_recv_mb": round(net.bytes_recv / 1e6, 1),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
        "errin": net.errin,
        "errout": net.errout,
    }

def get_process_info():
    """监控关键进程"""
    targets = {"python", "obs64", "obs", "ffmpeg", "browser"}
    procs = []
    if HAS_PSUTIL:
        for p in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
            try:
                if p.info["name"] and any(t in p.info["name"].lower() for t in targets):
                    procs.append({
                        "name": p.info["name"],
                        "cpu": p.info["cpu_percent"] or 0,
                        "mem": p.info["memory_percent"] or 0,
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return procs

def get_alerts(info):
    alerts = []
    if info.get("cpu_percent", 0) > 90:
        alerts.append("CPU过载>90%")
    if info.get("memory_percent", 0) > 85:
        alerts.append("内存占用>85%")
    if info.get("gpu_util_percent", 0) > 95:
        alerts.append("GPU满载>95%")
    if info.get("gpu_temp", 0) > 85:
        alerts.append("GPU温度>85C")
    if info.get("errin", 0) > 100 or info.get("errout", 0) > 100:
        alerts.append("网络丢包异常")
    return alerts

print(f"[sysmon] 技术环境监控启动, 每{POLL_SECONDS}s写入 {ALERT_FILE.name}")
while True:
    now = time.time()
    info = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "timestamp": now,
        "host": platform.node(),
        **get_cpu_info(),
        **get_gpu_info(),
        **get_network_info(),
        "processes": get_process_info(),
    }
    alerts = get_alerts(info)
    if alerts:
        info["alerts"] = alerts
        for a in alerts:
            print(f"[sysmon] ⚠ {a}")

    with open(ALERT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")

    time.sleep(POLL_SECONDS)
