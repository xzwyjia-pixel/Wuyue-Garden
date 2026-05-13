"""
实时分析器 — 监控 chat_log.json, 统计近 3min 关键词频率, 显示热度条
"""

import json
import time
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

KEYWORDS = {"哈哈", "多少钱", "想要", "海燕", "姐"}
WINDOW_SEC = 180         # 3 分钟滑动窗口
POLL_INTERVAL = 5        # 每 5 秒刷新
LOG_PATH = "chat_log.json"


def load_entries():
    p = Path(LOG_PATH)
    if not p.exists():
        return []
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def analyze_window(entries, now):
    """统计过去 WINDOW_SEC 秒内的关键词."""
    cutoff = now - WINDOW_SEC
    recent = [e for e in entries if e.get("timestamp", 0) >= cutoff]

    kw_counts = {k: 0 for k in KEYWORDS}
    for e in recent:
        texts = "".join(e.get("texts", []))
        for kw in KEYWORDS:
            kw_counts[kw] += texts.count(kw)

    total = sum(kw_counts.values())
    # 按频次排序输出
    sorted_kw = sorted(kw_counts.items(), key=lambda x: -x[1])

    return {
        "window_min": WINDOW_SEC / 60,
        "chat_count": len(recent),
        "keywords": dict(sorted_kw),
        "total_mentions": total,
    }


def draw_heatbar(total, max_bar=20):
    """热度条: 按提及次数分档."""
    if total >= 50:
        level = "🔥🔥🔥 爆热"
        fill = max_bar
    elif total >= 20:
        level = "🔥🔥 高热"
        fill = int(max_bar * 0.7)
    elif total >= 8:
        level = "🔥 中热"
        fill = int(max_bar * 0.4)
    elif total >= 2:
        level = "微温"
        fill = int(max_bar * 0.15)
    else:
        level = "❄️ 冷场"
        fill = 0

    bar = "█" * fill + "░" * (max_bar - fill)
    return f"{bar} {level} ({total}次)"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def display(result):
    clear_screen()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    w = result["window_min"]

    print("=" * 55)
    print(f"  实时直播分析  (近 {w:.0f}min 滑动窗口)")
    print(f"  刷新时间: {now_str}")
    print("=" * 55)
    print()

    print(f"  评论条数:  {result['chat_count']}")
    print()
    print(f"  热度总览:  {draw_heatbar(result['total_mentions'])}")
    print()

    print("  [关键词明细]")
    for kw, c in result["keywords"].items():
        bar = "█" * min(c, 30)
        print(f"    {kw}: {c:>4} 次  {bar}")
    print()
    print("  Ctrl+C 停止")
    print("=" * 55)


def main():
    print("实时分析器启动... 等待 chat_log.json 数据...")
    time.sleep(2)

    while True:
        entries = load_entries()
        if entries:
            result = analyze_window(entries, time.time())
            display(result)
        else:
            clear_screen()
            print("等待 chat_log.json 生成数据...")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n分析器已停止")
