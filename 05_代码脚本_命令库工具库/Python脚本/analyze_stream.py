"""
直播评论分析 — 读取 chat_log.json → 关键词频率统计
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

KEYWORDS = {"多少钱", "怎么买", "哈哈", "海燕", "姐"}


def load(path="chat_log.json"):
    p = Path(path)
    if not p.exists():
        print(f"[错误] {path} 不存在")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("[错误] JSON 格式错误，需要数组")
        sys.exit(1)
    return data


def analyze(entries):
    if not entries:
        return {"total": 0, "duration_min": 0, "msg_per_min": 0, "keywords": {}}

    timestamps = [e["timestamp"] for e in entries if "timestamp" in e]
    duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0
    dur_min = duration / 60 if duration > 0 else 0
    freq = round(len(entries) / dur_min, 2) if dur_min > 0 else 0

    kw_counts = {k: 0 for k in KEYWORDS}
    mentions = []
    for e in entries:
        texts = "".join(e.get("texts", []))
        matched = False
        for kw in KEYWORDS:
            c = texts.count(kw)
            if c:
                kw_counts[kw] += c
                matched = True
        if matched:
            mentions.append({"time": e.get("time", ""), "texts": e.get("texts", [])})

    return {
        "total": len(entries),
        "duration_sec": round(duration, 1),
        "duration_min": round(dur_min, 1),
        "msg_per_min": freq,
        "keywords": dict(sorted(kw_counts.items(), key=lambda x: -x[1])),
        "total_mentions": sum(kw_counts.values()),
        "mentions": mentions[-20:],  # 最近20条
    }


def print_report(r):
    sep = "=" * 50
    print(sep)
    print("  直播评论分析报告")
    print(sep)
    print(f"  总条目:    {r['total']}")
    print(f"  监控时长:  {r['duration_min']} min ({r['duration_sec']}s)")
    print(f"  互动频率:  {r['msg_per_min']} 条/min")
    print()
    print("  [关键词统计]")
    for kw, c in r["keywords"].items():
        bar = "█" * min(c, 40)
        print(f"    {kw}: {c} 次 {bar}")
    print(f"  总提及:    {r['total_mentions']} 次")
    print()
    # 热度评级
    rate = r["msg_per_min"]
    if rate >= 30:
        level = "🔥🔥🔥 高热"
    elif rate >= 10:
        level = "🔥🔥 中热"
    elif rate >= 3:
        level = "🔥 低热"
    else:
        level = "❄️ 冷场"
    print(f"  热度评级:  {level}")
    print()

    if r["mentions"]:
        print("  [近期提及明细]")
        for m in r["mentions"][-5:]:
            print(f"    [{m['time']}] {' | '.join(m['texts'][:3])}")

    print(sep)
    print(f"  报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="chat_log.json")
    args = parser.parse_args()
    print_report(analyze(load(args.input)))


if __name__ == "__main__":
    main()
