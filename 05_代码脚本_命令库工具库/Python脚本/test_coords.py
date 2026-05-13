"""
截图测试：验证 CHAT_AREA 坐标。
截图 → check.png → OCR 打印第一行文字。
"""

from pathlib import Path

import pyautogui
import easyocr

# 从 monitor_view.py 读取 CHAT_AREA
ns = {}
exec(compile(Path("monitor_view.py").read_text(encoding="utf-8"),
             "monitor_view.py", "exec"), ns)
left, top, w, h = ns["CHAT_AREA"]

print("=" * 50)
print(f"CHAT_AREA = ({left}, {top}, {w}, {h})")
print(f"右下角    = ({left + w}, {top + h})")

# 截图
img = pyautogui.screenshot(region=(left, top, w, h))
img.save("check.png")
print(f"已保存 → check.png  ({img.size[0]}×{img.size[1]})")

# OCR
reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
results = reader.readtext("check.png")

if not results:
    print("[无文字] 坐标可能不对")
else:
    first = results[0]
    print(f"首行文字: {first[1]}  (置信度 {first[2]:.2f})")
    if len(results) > 1:
        print(f"共 {len(results)} 段，首行如上。更多见 check.png")

print("=" * 50)
