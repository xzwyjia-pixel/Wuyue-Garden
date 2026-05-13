"""Start monitor_susu_pro.py as background hidden process"""
import subprocess, sys

# Use --no-bg to skip audio/STT (they'd need separate GPU/audio devices)
# Use --auto to skip interactive calibration
cmd = [
    "powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command",
    f'cd "E:\\MyCodeProjects\\审计工具"; '
    f'python monitor_susu_pro.py --auto --no-bg '
    f'>> "E:\\MyCodeProjects\\06-存档中心\\logs\\monitor.log" 2>>&1'
]
proc = subprocess.Popen(
    cmd,
    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
print(f"monitor_susu_pro.py started, PID: {proc.pid}")
