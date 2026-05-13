"""
post_stream_report.py — 直播后全套复盘数据分析报告
读取全部监控 jsonl 生成结构化复盘: 走势、异常、违规、技术、平台对比
用法: python post_stream_report.py --target <目录> [--output <报告.md>]
"""
import json, re, sys, os, argparse
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
parser.add_argument("--output", default="")
args = parser.parse_args()
TARGET = Path(args.target)
OUTPUT = Path(args.output) if args.output else TARGET / "复盘报告.md"

sys.stdout.reconfigure(encoding="utf-8")

def load_jsonl(path):
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S") if ts else "?"

def fmt_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h{minutes:02d}m{secs:02d}s"

def build_metadata(target_name, report_type, start_ts, end_ts, data_sources, extra_tags=None):
    """标准化元数据头 — 归档/检索用"""
    lines = ["---"]
    lines.append(f"report_type: {report_type}")
    lines.append(f"target: {target_name}")
    stream_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d") if start_ts else "N/A"
    lines.append(f"stream_date: {stream_date}")
    lines.append(f"stream_time: {fmt_time(start_ts)} → {fmt_time(end_ts)}")
    duration_s = end_ts - start_ts if end_ts > start_ts else 0
    lines.append(f"duration: {fmt_duration(duration_s)}")
    lines.append(f"generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("source_files:")
    for name, count in data_sources:
        lines.append(f"  - {name} ({count})")
    if extra_tags:
        lines.append(f"top_tags: [{', '.join(extra_tags)}]")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

# Load all data
print("[复盘] 加载数据...")
ocr_su = load_jsonl(TARGET / "live_data_SuSu.jsonl")
ocr_dy = load_jsonl(TARGET / "live_data_DouYin.jsonl")
tri_su = load_jsonl(TARGET / "triage_log_SuSu.jsonl")
tri_dy = load_jsonl(TARGET / "triage_log_DouYin.jsonl")
stt = load_jsonl(TARGET / "stt.jsonl")
sh = load_jsonl(TARGET / "stream_health.jsonl")
sys_health = load_jsonl(TARGET / "system_health.jsonl")
v3 = load_jsonl(TARGET / "v3_events.jsonl")
ac_data = None
if (TARGET / "audience_classification.json").is_file():
    with open(TARGET / "audience_classification.json", encoding="utf-8") as f:
        ac_data = json.load(f)

# Time range
all_ts = []
for e in ocr_su + ocr_dy + stt + tri_su + tri_dy + sh:
    ts = e.get("timestamp", 0)
    if ts:
        all_ts.append(ts)

start_ts = min(all_ts) if all_ts else 0
end_ts = max(all_ts) if all_ts else 0
duration_s = end_ts - start_ts if end_ts > start_ts else 0

# Dynamic default filename: date_target_type.md
stream_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d") if start_ts else "nodata"
if not args.output:
    OUTPUT = TARGET / f"{stream_date}_{TARGET.name}_复盘报告.md"

# ---- Build report ----
print("[复盘] 生成报告...")

target_name = TARGET.name

# Build data source summary
data_sources = [
    ("live_data_SuSu.jsonl", f"{len(ocr_su)} frames"),
    ("live_data_DouYin.jsonl", f"{len(ocr_dy)} frames"),
    ("triage_log_SuSu.jsonl", f"{len(tri_su)} entries"),
    ("triage_log_DouYin.jsonl", f"{len(tri_dy)} entries"),
    ("stt.jsonl", f"{len(stt)} entries"),
]
if sh:
    data_sources.append(("stream_health.jsonl", f"{len(sh)} entries"))
if sys_health:
    data_sources.append(("system_health.jsonl", f"{len(sys_health)} entries"))
if v3:
    data_sources.append(("v3_events.jsonl", f"{len(v3)} entries"))

# Compute top tags from compliance/sentiment/anomalies
top_tags = []
if any(e.get("sentiment") for e in v3):
    top_tags.append("情感分析")
if any(e.get("compliance_hits") for e in v3):
    top_tags.append("合规检测")
if any(e.get("platform_sync_diffs") for e in v3):
    top_tags.append("平台同步")
if any(e.get("stream_anomalies") for e in v3):
    top_tags.append("流异常")
if sys_health:
    top_tags.append("技术环境")

metadata = build_metadata(target_name, "复盘报告", start_ts, end_ts, data_sources, top_tags)

report = [metadata]
report.append(f"# {target_name} · 直播复盘报告")
report.append(f"")
report.append(f"**日期:** {datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d') if start_ts else 'N/A'}")
report.append(f"**时段:** {fmt_time(start_ts)} → {fmt_time(end_ts)}")
report.append(f"**时长:** {fmt_duration(duration_s)}")
report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"")

# ---- 1. 基础状态 ----
report.append(f"## 1. 直播基础状态")
report.append(f"")

# Parse stream health
if sh:
    black_events = [e for e in sh for a in e.get("anomalies", []) if "黑屏" in a]
    freeze_events = [e for e in sh for a in e.get("anomalies", []) if "冻结" in a or "恢复" in a]
    audio_events = [e for e in sh for a in e.get("anomalies", []) if "音频" in a]

    # Brightness timeline
    brightness_data = []
    for e in sh:
        for key in e:
            if "_brightness" in key:
                brightness_data.append((e["timestamp"], key, e[key]))
    if brightness_data:
        b_su = [(fmt_time(t), v) for t, k, v in brightness_data if "su" in k and v and v > 0]
        b_dy = [(fmt_time(t), v) for t, k, v in brightness_data if "dy" in k and v and v > 0]
        if b_su:
            avg = sum(v for _, v in b_su) / len(b_su)
            report.append(f"- **视频号亮度:** avg={avg:.0f}/255 min={min(v for _,v in b_su):.0f} max={max(v for _,v in b_su):.0f}")
        if b_dy:
            avg = sum(v for _, v in b_dy) / len(b_dy)
            report.append(f"- **抖音亮度:** avg={avg:.0f}/255 min={min(v for _,v in b_dy):.0f} max={max(v for _,v in b_dy):.0f}")

    report.append(f"- **黑屏事件:** {len(black_events)}次")
    for e in black_events[:5]:
        t = fmt_time(e.get("timestamp", 0))
        report.append(f"  - [{t}] {e['anomalies']}")

    report.append(f"- **画面冻结:** {len(freeze_events)}次")
    for e in freeze_events[:5]:
        t = fmt_time(e.get("timestamp", 0))
        report.append(f"  - [{t}] {e['anomalies']}")

    report.append(f"- **音频异常:** {len(audio_events)}次")
    for e in audio_events[:5]:
        t = fmt_time(e.get("timestamp", 0))
        report.append(f"  - [{t}] {e['anomalies']}")

    # Audio RMS timeline
    audio_rms = [(fmt_time(e["timestamp"]), e.get("audio_rms", 0)) for e in sh if e.get("audio_rms")]
    if audio_rms:
        avg_rms = sum(r for _, r in audio_rms) / len(audio_rms)
        report.append(f"- **音频RMS:** avg={avg_rms:.4f} (正常>0.001)")
else:
    report.append(f"- *无流健康监测数据*")
report.append(f"")

# ---- 2. 流量人气 ----
report.append(f"## 2. 流量人气数据")
report.append(f"")
report.append(f"- **直播总时长:** {fmt_duration(duration_s)}")
report.append(f"- **各平台OCR巡检:** 视频号{len(ocr_su)}次 / 抖音{len(ocr_dy)}次")
report.append(f"- **Triage视觉巡检:** 视频号{len(tri_su)}次 / 抖音{len(tri_dy)}次")
# V3 metrics
if v3:
    v3_metrics = [e.get("visible_metrics", {}) for e in v3 if e.get("visible_metrics")]
    total_price_mentions = sum(m.get("price_mentions", 0) for m in v3_metrics)
    if total_price_mentions:
        report.append(f"- **价格讨论热度:** {total_price_mentions}次被提及")
report.append(f"")
report.append(f"> ⚠ *注: 实时在线人数/场观/GMV等平台内部数据需通过对应开放API获取, 当前为屏幕侧检测数据*")
report.append(f"")

# ---- 3. 弹幕互动 ----
all_su_texts = [t for r in ocr_su for t in r.get("texts", [])]
all_dy_texts = [t for r in ocr_dy for t in r.get("texts", [])]

# Parse user:msg
def parse_all_ocr(ocr_data):
    """OCR帧去重: 同用户同消息在30秒窗口内算1次"""
    users = Counter()
    msgs = []
    recent = {}  # user:msg -> last_seen_timestamp
    window = 30  # seconds
    for r in ocr_data:
        ts = r.get("timestamp", 0)
        for t in r.get("texts", []):
            m = re.split(r"[:：]\s*", t, maxsplit=1)
            if len(m) == 2 and m[1].strip():
                user = m[0].strip()
                msg = m[1].strip()
                key = f"{user}:{msg}"
                last = recent.get(key, 0)
                if ts - last >= window:
                    recent[key] = ts
                    users[user] += 1
                    msgs.append(msg)
            elif m[0].strip():
                users[m[0].strip()] += 1
    print(f"[复盘] 去重后: {len(msgs)}条有效评论 (原始{sum(len(r.get('texts',[])) for r in ocr_data)}条)")
    return users, msgs

users_su, msgs_su = parse_all_ocr(ocr_su)
users_dy, msgs_dy = parse_all_ocr(ocr_dy)
all_users = Counter()
for u, c in users_su.items():
    all_users[u] += c
for u, c in users_dy.items():
    all_users[u] += c
both = set(users_su.keys()) & set(users_dy.keys())
total_comments = len(msgs_su) + len(msgs_dy)

report.append(f"## 3. 弹幕互动监控")
report.append(f"")
report.append(f"- **总评论量(去重):** {total_comments}条 (视频号{len(msgs_su)} / 抖音{len(msgs_dy)})")
report.append(f"- **总互动用户:** {len(all_users)}人")
report.append(f"- **双平台活跃用户:** {len(both)}人")
report.append(f"- **仅视频号用户:** {len(set(users_su.keys()) - both)}人")
report.append(f"- **仅抖音用户:** {len(set(users_dy.keys()) - both)}人")
report.append(f"")

report.append(f"### 活跃用户 Top 10")
report.append(f"")
report.append(f"| # | 用户 | 总条数 | 视频号 | 抖音 |")
report.append(f"|---|------|--------|--------|------|")
for i, (u, c) in enumerate(all_users.most_common(10), 1):
    su_c = users_su.get(u, 0)
    dy_c = users_dy.get(u, 0)
    report.append(f"| {i} | {u} | {c} | {su_c} | {dy_c} |")
report.append(f"")

# Top messages
msg_counter = Counter(msgs_su + msgs_dy)
report.append(f"### 高频评论 Top 15")
report.append(f"")
report.append(f"| 次数 | 内容 |")
report.append(f"|------|------|")
for msg, cnt in msg_counter.most_common(15):
    report.append(f"| {cnt} | {msg[:50]} |")
report.append(f"")

# Sentiment from v3
if v3:
    sentiments = [e.get("sentiment", "neutral") for e in v3 if e.get("sentiment")]
    if sentiments:
        pos_pct = sentiments.count("positive") / len(sentiments) * 100
        neg_pct = sentiments.count("negative") / len(sentiments) * 100
        neutral_pct = sentiments.count("neutral") / len(sentiments) * 100
        report.append(f"### 弹幕情绪分析")
        report.append(f"")
        report.append(f"- **正向情绪:** {pos_pct:.0f}%")
        report.append(f"- **中立情绪:** {neutral_pct:.0f}%")
        report.append(f"- **负面情绪:** {neg_pct:.0f}%")
        report.append(f"")

# Compliance from v3
if v3:
    all_compliance = []
    for e in v3:
        hits = e.get("compliance_hits", [])
        if hits:
            for h in hits:
                all_compliance.append((e["time"], h))

    if all_compliance:
        report.append(f"### 合规风险记录")
        report.append(f"")
        report.append(f"| 时间 | 触发词 | 原文 |")
        report.append(f"|------|--------|------|")
        for t, h in all_compliance:
            report.append(f"| {t} | {h.get('keyword','?')} | {h.get('text','?')} |")
        report.append(f"")

# ---- 4. 商品转化 ----
report.append(f"## 4. 商品转化监控")
report.append(f"")
# Price mentions over time
price_time = []
for r in ocr_su + ocr_dy:
    ts = r.get("timestamp", 0)
    for t in r.get("texts", []):
        if any(w in t for w in ["多少", "贵", "便宜", "价格", "三千"]):
            price_time.append((fmt_time(ts), t[:40]))
if price_time:
    report.append(f"- **价格讨论:** {len(price_time)}次, 分布在全时段")
    for t, txt in price_time[:10]:
        report.append(f"  - [{t}] {txt}")
else:
    report.append(f"- *无商品转化相关数据*")
report.append(f"")
report.append(f"> ⚠ *注: GMV/订单/退款等需平台电商API, 当前仅通过评论中的价格讨论侧面反映*")
report.append(f"")

# ---- 5. 合规 ----
report.append(f"## 5. 合规内容监控")
report.append(f"")
all_compliance_hits = []
for d in v3:
    hits = d.get("compliance_hits", [])
    if hits:
        all_compliance_hits.extend(hits)

# Also scan OCR for compliance
ocr_compliance = []
seen_kws = set()
for t in all_su_texts + all_dy_texts:
    for kw in ["最", "第一", "独家", "微信", "公众号", "加V", "扫码"]:
        if kw in t and kw not in seen_kws:
            ocr_compliance.append((kw, t[:40]))
            seen_kws.add(kw)
            break

report.append(f"- **V3引擎检测合规触发:** {len(all_compliance_hits)}次")
report.append(f"- **OCR直接扫描潜在敏感词:** {len(ocr_compliance)}次")
if ocr_compliance:
    report.append(f"")
    report.append(f"| 时间 | 触发词 | 内容 |")
    report.append(f"|------|--------|------|")
    for kw, txt in ocr_compliance[:10]:
        report.append(f"| - | {kw} | {txt} |")
report.append(f"")

# ---- 6. 双平台一致性 ----
report.append(f"## 6. 双平台一致性")
report.append(f"")

def count_keywords(texts, kws):
    return sum(1 for t in texts for kw in kws if kw in t)

su_price = count_keywords(all_su_texts, ["多少", "贵", "便宜", "价格", "三千"])
dy_price = count_keywords(all_dy_texts, ["多少", "贵", "便宜", "价格", "三千"])
su_food = count_keywords(all_su_texts, ["笋", "熏鹅", "鱼", "鸭", "鸡", "梅干菜"])
dy_food = count_keywords(all_dy_texts, ["笋", "熏鹅", "鱼", "鸭", "鸡", "梅干菜"])
su_interact = count_keywords(all_su_texts, ["早上好", "来了", "拜拜", "在的", "早早早"])
dy_interact = count_keywords(all_dy_texts, ["早上好", "来了", "拜拜", "在的", "早早早"])

report.append(f"| 维度 | 视频号 | 抖音 | 差异 |")
report.append(f"|------|--------|------|------|")
report.append(f"| 评论量 | {len(all_su_texts)} | {len(all_dy_texts)} | {'抖音'+str(len(all_dy_texts)-len(all_su_texts))+'条更活跃' if len(all_dy_texts)>len(all_su_texts) else '视频号更活跃'} |")
report.append(f"| 用户数 | {len(users_su)} | {len(users_dy)} | {'抖音多'+str(len(users_dy)-len(users_su))+'人' if len(users_dy)>len(users_su) else ''} |")
report.append(f"| 价格讨论 | {su_price} | {dy_price} | {'抖音更关注价格' if dy_price>su_price else '视频号更关注价格'} |")
report.append(f"| 食材讨论 | {su_food} | {dy_food} | {'抖音' if dy_food>su_food else '视频号'}更多 |")
report.append(f"| 互动聊天 | {su_interact} | {dy_interact} | {'抖音' if dy_interact>su_interact else '视频号'}更活跃 |")
report.append(f"")

if ocr_su and ocr_dy:
    su_ts_span = ocr_su[-1].get("timestamp", 0) - ocr_su[0].get("timestamp", 0)
    dy_ts_span = ocr_dy[-1].get("timestamp", 0) - ocr_dy[0].get("timestamp", 0)
    report.append(f"- **视频号有效监控时长:** {fmt_duration(su_ts_span)}")
    report.append(f"- **抖音有效监控时长:** {fmt_duration(dy_ts_span)}")
    report.append(f"- **时差:** {abs(su_ts_span - dy_ts_span):.0f}秒")

report.append(f"")

if v3:
    sync_events = []
    for e in v3:
        diffs = e.get("platform_sync_diffs", [])
        if diffs:
            sync_events.append((e["time"], diffs))
    if sync_events:
        report.append(f"### 同步差异事件")
        report.append(f"")
        for t, diffs in sync_events[:5]:
            for d in diffs:
                report.append(f"- [{t}] {d}")
        report.append(f"")

# ---- 7. 技术环境 ----
report.append(f"## 7. 技术环境监控")
report.append(f"")

if sys_health:
    cpu_vals = [e.get("cpu_percent", 0) for e in sys_health if e.get("cpu_percent")]
    mem_vals = [e.get("memory_percent", 0) for e in sys_health if e.get("memory_percent")]
    gpu_util = [e.get("gpu_util_percent", 0) for e in sys_health if e.get("gpu_util_percent")]
    gpu_temp = [e.get("gpu_temp", 0) for e in sys_health if e.get("gpu_temp")]

    if cpu_vals:
        report.append(f"- **CPU:** avg={sum(cpu_vals)/len(cpu_vals):.0f}% max={max(cpu_vals)}%")
    if mem_vals:
        report.append(f"- **内存:** avg={sum(mem_vals)/len(mem_vals):.0f}% max={max(mem_vals)}%")
    if gpu_util:
        report.append(f"- **GPU:** avg={sum(gpu_util)/len(gpu_util):.0f}% max={max(gpu_util)}%")
    if gpu_temp:
        report.append(f"- **GPU温度:** avg={sum(gpu_temp)/len(gpu_temp):.0f}C max={max(gpu_temp)}C")

    # Alerts
    sys_alerts = []
    for e in sys_health:
        alerts = e.get("alerts", [])
        if alerts:
            for a in alerts:
                sys_alerts.append((fmt_time(e["timestamp"]), a))
    if sys_alerts:
        report.append(f"- **系统告警:** {len(sys_alerts)}次")
        for t, a in sys_alerts[:10]:
            report.append(f"  - [{t}] {a}")

    # Process info
    all_procs = Counter()
    for e in sys_health:
        for p in e.get("processes", []):
            all_procs[p.get("name", "?")] += 1
    if all_procs:
        report.append(f"- **检测到的进程:** {', '.join(all_procs.keys())}")
else:
    report.append(f"- *无系统监控数据*")
report.append(f"")

# ---- 视觉质量汇总 ----
report.append(f"## 附: 视觉质量汇总")
report.append(f"")

for label, tri_data in [("视频号", tri_su), ("抖音", tri_dy)]:
    if not tri_data:
        continue
    bvals = [r.get("brightness", 0) for r in tri_data if r.get("brightness")]
    fcount = [r.get("face", {}).get("count", 0) for r in tri_data]
    fbright = [r.get("face", {}).get("avg_brightness", 0) for r in tri_data if r.get("face",{}).get("avg_brightness")]
    wvals = [r.get("warm_ratio", 0) * 100 for r in tri_data]
    fsat = [r.get("food_saturation", 0) for r in tri_data if r.get("food_saturation")]

    report.append(f"### {label}")
    report.append(f"")
    report.append(f"| 指标 | 均值 | 范围 |")
    report.append(f"|------|------|------|")
    if bvals:
        report.append(f"| 亮度 | {sum(bvals)/len(bvals):.0f} | {min(bvals):.0f}-{max(bvals):.0f} |")
    if fcount:
        face_pct = sum(1 for c in fcount if c > 0) / len(fcount) * 100
        report.append(f"| 人脸出镜 | {face_pct:.0f}% | {sum(1 for c in fcount if c > 0)}/{len(fcount)}帧 |")
    if fbright:
        report.append(f"| 面部亮度 | {sum(fbright)/len(fbright):.0f} | - |")
    if wvals:
        report.append(f"| 暖色比 | {sum(wvals)/len(wvals):.1f}% | - |")
    if fsat:
        report.append(f"| 食物饱和度 | {sum(fsat)/len(fsat):.1f} | - |")
    report.append(f"")

# ---- 客群分类 ----
report.append(f"## 附: 客群分类")
report.append(f"")
if ac_data and "segments" in ac_data:
    report.append(f"| 客群类型 | 占比 | 人数 |")
    report.append(f"|----------|------|------|")
    for seg_name, seg_info in ac_data["segments"].items():
        pct = seg_info.get("percentage", 0)
        users = seg_info.get("users", 0)
        bar = "█" * int(pct / 3)
        report.append(f"| {seg_name} | {pct:.1f}% {bar} | {users}人 |")
    report.append(f"")
    # Suggestions
    has_suggestions = False
    for seg_name, seg_info in ac_data["segments"].items():
        sug = seg_info.get("suggestion", "")
        if sug:
            if not has_suggestions:
                report.append(f"### 话术优化建议")
                report.append(f"")
                has_suggestions = True
            report.append(f"- **{seg_name}:** {sug}")
    report.append(f"")

# ---- 异常时间线 ----
all_anomalies = []

# From stream health
for e in sh:
    for a in e.get("anomalies", []):
        all_anomalies.append((e.get("timestamp", 0), fmt_time(e.get("timestamp", 0)), "流健康", a))
# From v3
for e in v3:
    for a in (e.get("stream_anomalies", []) or []):
        all_anomalies.append((e.get("timestamp", 0), e.get("time", "?"), "V3流", a))
    for a in (e.get("system_alerts", []) or []):
        all_anomalies.append((e.get("timestamp", 0), e.get("time", "?"), "系统", a))
# From system health
for e in sys_health:
    for a in (e.get("alerts", []) or []):
        all_anomalies.append((e.get("timestamp", 0), fmt_time(e.get("timestamp", 0)), "技术", a))

all_anomalies.sort(key=lambda x: x[0])

if all_anomalies:
    report.append(f"## 附: 异常事件时间线")
    report.append(f"")
    report.append(f"| 时间 | 类别 | 事件 |")
    report.append(f"|------|------|------|")
    for ts, t, cat, desc in all_anomalies:
        report.append(f"| {t} | {cat} | {desc[:60]} |")
    report.append(f"")
    report.append(f"**异常总计:** {len(all_anomalies)}次")
    report.append(f"")

# ---- STT sample ----
if stt:
    report.append(f"## 附: 语音识别片段 (最后10条)")
    report.append(f"")
    for r in stt[-10:]:
        txt = r.get("text", "")[:80]
        t = r.get("time", "")
        if txt.strip():
            report.append(f"- [{t}] {txt}")
    report.append(f"")

# ---- 结论 ----
report.append(f"---")
report.append(f"")
report.append(f"*报告由 甄查工作站 直播监控系统 v3.0 自动生成*")
report.append(f"*数据来源: OCR评论区 + STT语音 + Triage视觉 + Stream健康 + System监控*")

# Write report
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print(f"[复盘] 报告已保存: {OUTPUT}")
print(f"[复盘] {len(report)} 行, 覆盖全部7大类监控维度")
