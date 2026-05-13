"""
直播热度分析报告 — 读取 chat_log.json → 互动频率 + 关键词识别
"""

import json
import sys
from collections import Counter
from pathlib import Path

# ── 配置 ───────────────────────────────────────────────────

KEYWORDS = {"多少钱", "怎么买", "海燕", "南瓜", "姐"}
REPORT_HEADER = "=" * 50
SEP = "-" * 50


# ── 数据加载 ──────────────────────────────────────────────

def load_chat_log(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        print(f"[错误] 文件不存在: {path}")
        sys.exit(1)
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("[错误] JSON 格式错误: 需要数组")
        sys.exit(1)
    return data


# ── 分析函数 ──────────────────────────────────────────────

def calc_interaction_frequency(entries: list[dict]) -> dict:
    """计算互动频率：每分钟消息数。"""
    if not entries:
        return {"total_entries": 0, "duration_min": 0, "msg_per_min": 0.0}

    timestamps = [e["timestamp"] for e in entries if "timestamp" in e]
    if not timestamps:
        return {"total_entries": len(entries), "duration_min": 0, "msg_per_min": 0.0}

    duration_sec = timestamps[-1] - timestamps[0]
    duration_min = duration_sec / 60 if duration_sec > 0 else 0

    return {
        "total_entries": len(entries),
        "duration_sec": round(duration_sec, 1),
        "duration_min": round(duration_min, 1),
        "msg_per_min": round(len(entries) / duration_min, 2) if duration_min > 0 else 0,
    }


def calc_keyword_hits(entries: list[dict]) -> dict:
    """统计关键词出现频次。"""
    keyword_counter: dict[str, int] = {kw: 0 for kw in KEYWORDS}
    mention_entries: list[dict] = []

    for entry in entries:
        texts = entry.get("texts", [])
        full_text = "".join(texts)
        matched = False
        for kw in KEYWORDS:
            if kw in full_text:
                keyword_counter[kw] += full_text.count(kw)
                matched = True
        if matched:
            mention_entries.append({
                "time": entry.get("time_human", ""),
                "matched_texts": [t for t in texts if any(kw in t for kw in KEYWORDS)],
            })

    return {
        "keyword_counts": dict(sorted(keyword_counter.items(), key=lambda x: -x[1])),
        "total_mentions": sum(keyword_counter.values()),
        "mention_entries": mention_entries,
    }


# ── 报告生成 ──────────────────────────────────────────────

def generate_report(entries: list[dict]) -> str:
    freq = calc_interaction_frequency(entries)
    kw = calc_keyword_hits(entries)

    lines = []
    lines.append(REPORT_HEADER)
    lines.append("  直播热度分析报告")
    lines.append(REPORT_HEADER)
    lines.append("")

    # 基本统计
    lines.append("[基本统计]")
    lines.append(f"  数据条目:      {freq['total_entries']}")
    lines.append(f"  监控时长:      {freq['duration_min']} 分钟 ({freq['duration_sec']} 秒)")
    lines.append(f"  互动频率:      {freq['msg_per_min']} 条/分钟")
    lines.append("")

    # 关键词分析
    lines.append("[关键词分析]")
    lines.append(f"  总提及次数:    {kw['total_mentions']}")
    lines.append(f"  关键词分布:")
    for keyword, count in kw["keyword_counts"].items():
        bar = "█" * min(count, 50)
        lines.append(f"    {keyword}: {count} 次 {bar}")
    lines.append("")

    # 热度评级
    rate = freq["msg_per_min"]
    if rate >= 30:
        heat_level = "🔥🔥🔥 高热直播间 — 互动密集，人气旺盛"
    elif rate >= 10:
        heat_level = "🔥🔥 中热直播间 — 互动活跃，持续有观众参与"
    elif rate >= 3:
        heat_level = "🔥 低热直播间 — 偶有互动，需引导话术提升活跃度"
    else:
        heat_level = "❄️ 冷场直播间 — 互动稀少，建议调整直播内容或引流策略"

    lines.append("[热度评级]")
    lines.append(f"  {heat_level}")
    lines.append("")

    # 详细提及记录
    if kw["mention_entries"]:
        lines.append("[关键词提及明细]")
        for m in kw["mention_entries"]:
            lines.append(f"  [{m['time']}] {' | '.join(m['matched_texts'])}")
        lines.append("")

    lines.append(SEP)
    lines.append("报告生成时间: " + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append(REPORT_HEADER)

    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="直播热度分析报告")
    parser.add_argument("input", nargs="?", default="chat_log.json",
                        help="chat_log.json 路径, 默认当前目录")
    parser.add_argument("--output", "-o", help="输出报告到文件 (可选)")
    args = parser.parse_args()

    entries = load_chat_log(args.input)
    report = generate_report(entries)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"报告已保存 → {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
