"""Robust launcher for monitor_susu_pro.py — runs in background, captures all errors"""
import subprocess, sys, time, os

log_path = "E:/MyCodeProjects/06-存档中心/logs/monitor_launcher.log"
monitor_py = "E:/MyCodeProjects/审计工具/monitor_susu_pro.py"

# Kill any existing monitor first
subprocess.run(
    ['powershell', '-NoProfile', '-Command',
     'Get-Process -Name python* | Where-Object { $_.CommandLine -like "*monitor_susu_pro*" } | Stop-Process -Force -ErrorAction SilentlyContinue'],
    capture_output=True, timeout=10
)

# Headless mode — no rich.live, pure data collection
# --no-bg since audio/stt may already be running
cmd = f'python "{monitor_py}" --auto --no-bg --headless >> "{log_path}" 2>&1'
print(f"Running: {cmd}")
proc = subprocess.Popen(
    ['python', monitor_py, '--auto', '--no-bg', '--headless'],
    stdout=open(log_path, 'a'), stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
)
pid = proc.pid
print(f"PID: {pid}")

# Wait for startup
time.sleep(15)

# Check if alive
alive = proc.poll() is None
print(f"Alive: {alive}")
if not alive:
    print(f"Exit code: {proc.returncode}")

# Check ps
ps = subprocess.run(['powershell', '-NoProfile', '-Command',
    'Get-Process -Name python* | Where-Object { $_.CommandLine -like "*monitor_susu_pro*" } | Format-Table Id, ProcessName -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(f"Running processes:\n{ps.stdout}")

# Check log tail
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    print(f"Log tail ({len(lines)} lines total):")
    for l in lines[-20:]:
        print(l.rstrip())
