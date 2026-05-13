"""
save_convo.py — 保存对话内容到项目目录
用法: python save_convo.py <主题词> <标题.md>
  or: python save_convo.py <标题.md>  (自动从父文件夹取主题)
写入: 04-宝妈直播诊断系统/清晨烟火小厨/{YYYY-MM-DD}_{主题}/{标题}
"""
import sys
from pathlib import Path
from datetime import datetime

TARGET_ROOT = Path("E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
today = datetime.now().strftime("%Y-%m-%d")

if len(sys.argv) == 3:
    topic, title = sys.argv[1], sys.argv[2]
elif len(sys.argv) == 2:
    title = sys.argv[1]
    # Auto-detect topic from existing today folder
    existing = sorted(TARGET_ROOT.glob(f"{today}_*"))
    topic = existing[0].name.split("_", 1)[1] if existing else "直播策略"
else:
    print("Usage: python save_convo.py <主题词> <标题.md>")
    print("   or: python save_convo.py <标题.md> (复用当天主题)")
    sys.exit(1)

content = sys.stdin.read()
folder_name = f"{today}_{topic}"
target = TARGET_ROOT / folder_name
target.mkdir(parents=True, exist_ok=True)
(target / title).write_text(content, encoding="utf-8")
print(f"Saved: {target / title}")
