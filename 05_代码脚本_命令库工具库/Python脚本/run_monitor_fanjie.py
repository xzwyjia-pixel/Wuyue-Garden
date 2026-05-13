"""
run_monitor_fanjie.py — 凡姐走乡村 独立启动器
用绝对路径绕过 CWD / 转义问题
"""
import sys, ast, re
from pathlib import Path

BASE = Path(__file__).parent.parent.resolve()  # E:\MyCodeProjects
sys.path.insert(0, str(BASE / "02-审计工具"))

text = (BASE / "instructions.md").read_text(encoding="utf-8")
m = re.search(r"Live_Profiles\s*=\s*(\{.+?\n\})", text, re.DOTALL)
profiles = ast.literal_eval(m.group(1))
profile = profiles["凡姐走乡村"]
profile["_slug"] = "凡姐走乡村"
alias = profile.get("_alias", "FanJie")

# 清理旧帧
d = BASE / "02-审计工具" / "temp_frames" / alias
if d.exists():
    for f in d.iterdir():
        f.unlink()
else:
    d.mkdir(parents=True)

from monitor_engine import LiveMonitorEngine

print(f"[启动] 凡姐走乡村 (alias={alias})", flush=True)
engine = LiveMonitorEngine(profile)
engine.run()
