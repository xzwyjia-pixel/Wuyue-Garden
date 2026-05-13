"""Bootstrap: launch headless monitor via pythonw, survives parent exit."""
import subprocess, sys, os, time

monitor_py = r"E:\MyCodeProjects\审计工具\monitor_susu_pro.py"
log_file = r"E:\MyCodeProjects\06-存档中心\logs\monitor_bootstrap.log"

# Kill any existing monitor
subprocess.run(
    ['powershell', '-NoProfile', '-Command',
     'Get-CimInstance Win32_Process -Filter "Name=\'python.exe\'" | Where-Object { $_.CommandLine -like \'*monitor_susu_pro*\' } | ForEach-Object { Stop-Process $_.ProcessId -Force }'],
    capture_output=True, timeout=10
)
time.sleep(1)

# Use pythonw (in PATH) for truly window-less background process
proc = subprocess.Popen(
    ['pythonw', monitor_py, '--auto', '--no-bg', '--headless'],
    stdout=open(log_file, 'a', encoding='utf-8'),
    stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
)
print(f"Launched via pythonw. PID: {proc.pid}")

# Wait and check
time.sleep(20)

# Check processes
ps_check = subprocess.run(
    ['powershell', '-NoProfile', '-Command',
     'Get-CimInstance Win32_Process -Filter "Name=\'python.exe\'" | Where-Object { $_.CommandLine -like \'*monitor_susu_pro*\' } | Select-Object ProcessId, CommandLine'],
    capture_output=True, text=True, timeout=10
)
print(f"Alive processes:\n{ps_check.stdout}")

if not ps_check.stdout.strip():
    print("Monitor NOT alive. Checking log tail...")
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        # Print last 500 chars safely
        safe = text[-1000:].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        print(f"Log tail:\n{safe}")
else:
    print("Monitor is alive!")
