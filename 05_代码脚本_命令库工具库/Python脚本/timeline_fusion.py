"""
timeline_fusion.py — v2.0 多数据源融合时间线
合并: OCR评论区 + STT语音 + Triage评分
输出: timeline.jsonl + 终端摘要 (首次即时, 之后每30s)
"""
import json, time, os, sys, argparse
from pathlib import Path
from datetime import datetime

DEFAULT_BASE = Path("E:/MyCodeProjects/05-参考案例/农村小琪")
POLL_SECONDS = 30

def load_jsonl(path):
    if not path.is_file():
        return []
    data = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                pass
    return data

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M")

def build_timeline(base):
    ocr_su = load_jsonl(base / "live_data_SuSu.jsonl")
    ocr_dy = load_jsonl(base / "live_data_DouYin.jsonl")
    triage_su = load_jsonl(base / "triage_log_SuSu.jsonl")
    triage_dy = load_jsonl(base / "triage_log_DouYin.jsonl")
    stt = load_jsonl(base / "stt.jsonl")

    events = []

    for r in ocr_su + ocr_dy:
        texts = r.get("texts", [])
        chat_lines = [t for t in texts if ":" in t or "：" in t]
        events.append({
            "t": r.get("timestamp", 0),
            "type": "chat",
            "summary": "; ".join(chat_lines[:3]) if chat_lines else "",
            "hits": r.get("keyword_hits", []),
        })

    for r in stt:
        events.append({
            "t": r.get("timestamp", 0),
            "type": "speech",
            "summary": r.get("text", "")[:120],
        })

    for r in triage_su + triage_dy:
        events.append({
            "t": r.get("timestamp", 0),
            "type": "visual",
            "brightness": round(r.get("brightness", 0), 1),
            "warm": round(r.get("warm_ratio", 0) * 100, 1),
            "food_sat": round(r.get("food_saturation", 0), 1),
            "authentic": r.get("score_authentic", 0),
        })

    events.sort(key=lambda e: e["t"])

    out = base / "timeline.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    return events

def print_summary(events, label):
    if not events:
        print("[时间线] 暂无数据")
        return
    print(f"\n{'='*60}")
    print(f"  {label} · 直播时间线 (共{len(events)}条事件)")
    print(f"{'='*60}")
    for e in events:
        ts = format_time(e["t"])
        t = e["type"]
        if t == "chat" and e["summary"]:
            print(f"  {ts} [CHAT] {e['summary'][:60]}")
        elif t == "speech":
            text = e["summary"][:80]
            if text.strip():
                print(f"  {ts} [SPEECH] {text}")
        elif t == "visual":
            print(f"  {ts} [VISUAL] 亮度{e['brightness']} 暖色{e['warm']}% "
                  f"食Sat{e['food_sat']} 真实{e['authentic']}/85")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="", help="数据目录, 默认农村小琪")
    args = parser.parse_args()
    base = Path(args.target) if args.target else DEFAULT_BASE
    label = base.name

    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    print(f"[时间线] 监控 {base.name}/, 每{POLL_SECONDS}s更新")
    cycle = 0
    while True:
        events = build_timeline(base)
        # Count by type for progress display
        chats = sum(1 for e in events if e["type"] == "chat")
        speeches = sum(1 for e in events if e["type"] == "speech")
        visuals = sum(1 for e in events if e["type"] == "visual")
        if cycle == 0 or cycle % 4 == 0:
            print(f"[时间线] [{datetime.now().strftime('%H:%M:%S')}] "
                  f"CHAT:{chats} SPEECH:{speeches} VISUAL:{visuals} 总计:{len(events)}条")
        if events:
            print_summary(events[-20:], label)  # last 20 events
        cycle += 1
        time.sleep(POLL_SECONDS)
