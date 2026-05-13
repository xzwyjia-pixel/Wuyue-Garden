import ast, re, sys, os, time
from pathlib import Path

LOG = Path("E:/MyCodeProjects/04-宝妈直播诊断系统/苏苏在浙里/monitor_susu.log")
LOG.parent.mkdir(parents=True, exist_ok=True)

# Redirect stdout/stderr to log file
log_fh = open(LOG, "w", encoding="utf-8")
sys.stdout = log_fh
sys.stderr = log_fh

os.chdir(os.path.dirname(os.path.abspath(__file__)))

text = open('instructions.md', encoding='utf-8').read()
m = re.search(r"Live_Profiles\s*=\s*(\{.+?\n\})", text, re.DOTALL)
profiles = ast.literal_eval(m.group(1))
profile = profiles['苏苏在浙里']
profile['_slug'] = '苏苏在浙里'
profile['chat_region'] = (1470, 300, 450, 500)  # calibrated from test comment

# Clean old frames
frame_dir = Path("E:/MyCodeProjects/06-存档中心/temp_frames/SuSu")
frame_dir.mkdir(parents=True, exist_ok=True)
for f in frame_dir.iterdir():
    f.unlink()
print(f"[{time.strftime('%H:%M:%S')}] 苏苏在浙里 monitor engine starting", flush=True)

from monitor_engine import LiveMonitorEngine
engine = LiveMonitorEngine(profile)
try:
    engine.run()
except Exception as e:
    print(f"[FATAL] {e}", flush=True)
    import traceback
    traceback.print_exc()
finally:
    log_fh.close()
