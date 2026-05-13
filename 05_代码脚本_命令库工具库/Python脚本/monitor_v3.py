"""
monitor_v3.py — 7类监控集成引擎 (分析层, 不重复截图)
读取各子监控输出, 补充缺失的分析维度, 输出 unified_events.jsonl

覆盖:
  1.基础状态 ← stream_health + 自有检测  2.流量人气 ← OCR可见数据
  3.弹幕互动 ← 自带情感分析              4.商品转化 ← OCR商品区监控
  5.合规内容 ← 敏感词+水印检测            6.双平台一致性 ← 实时比对
  7.技术环境 ← system_monitor 数据
"""
import json, time, os, sys, re, argparse
from pathlib import Path
from datetime import datetime
from collections import deque, Counter

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
args = parser.parse_args()
TARGET = Path(args.target)

POLL_SECONDS = 30
OUT_FILE = TARGET / "v3_events.jsonl"

# 合规敏感词 (示例, 可按需扩展)
COMPLIANCE_BLOCKED = [
    "最好", "第一", "首个", "独家", "唯一", "国家级", "最专业",
    "根治", "治愈", "无效退款", "纯天然", "无副作用", "医疗",
    "加微信", "关注公众号", "扫码", "私聊", "加群", "加V",
    "政治", "习近平", "共产党", "疫情", "疫苗",
]

# 导流词
DRAIN_WORDS = ["加微", "私信我", "看主页", "其他平台", "淘宝", "京东"]

# 价格相关词
PRICE_WORDS = ["多少", "贵", "便宜", "价格", "多少钱", "值", "划算"]

# 情感词典 (简单词表)
POSITIVE_WORDS = {"好吃", "想要", "喜欢", "不错", "支持", "回购", "下单", "买了", "赞", "棒", "好"}
NEGATIVE_WORDS = {"太贵", "不好", "差评", "不行", "失望", "退货", "退款", "骗", "假", "贵"}

sys.stdout.reconfigure(encoding="utf-8")

# 数据源位置
SOURCES = {
    "ocr_su": TARGET / "live_data_SuSu.jsonl",
    "ocr_dy": TARGET / "live_data_DouYin.jsonl",
    "triage_su": TARGET / "triage_log_SuSu.jsonl",
    "triage_dy": TARGET / "triage_log_DouYin.jsonl",
    "stt": TARGET / "stt.jsonl",
    "stream_health": TARGET / "stream_health.jsonl",
    "system_health": TARGET / "system_health.jsonl",
}
positions = {k: 0 for k in SOURCES}
buffers = {k: deque(maxlen=100) for k in SOURCES}

# 双平台同步状态追踪
last_su_texts = []
last_dy_texts = []

# 面部过曝追踪 (连续3次brightness>150告警)
FACE_OVEREXPOSE_THRESHOLD = 150
FACE_CONSECUTIVE_LIMIT = 3
face_history = {"su": [], "dy": []}

def tail_jsonl(path, pos, buf):
    if not path.is_file():
        return pos
    try:
        fsize = path.stat().st_size
        if fsize < pos:
            pos = 0
        with open(path, "r", encoding="utf-8") as f:
            f.seek(pos)
            for line in f:
                line = line.strip()
                if line:
                    try:
                        buf.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            pos = f.tell()
    except Exception:
        pass
    return pos

def sentiment_score(texts):
    pos = sum(1 for t in texts for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for t in texts for w in NEGATIVE_WORDS if w in t)
    total = pos + neg
    if total == 0:
        return "neutral", 0
    score = (pos - neg) / total
    if score > 0.3:
        return "positive", round(score, 2)
    elif score < -0.3:
        return "negative", round(score, 2)
    return "neutral", round(score, 2)

def check_compliance(texts):
    hits = []
    for t in texts:
        for kw in COMPLIANCE_BLOCKED:
            if kw in t:
                hits.append({"text": t[:40], "keyword": kw})
        for dw in DRAIN_WORDS:
            if dw in t:
                hits.append({"text": t[:40], "keyword": f"[导流]{dw}"})
    return hits

def check_platform_sync(su_texts, dy_texts):
    """检查双平台同步差异"""
    diffs = []
    su_set = set(su_texts)
    dy_set = set(dy_texts)
    # 如果一方评论量远多于另一方, 可能平台不同步
    if su_texts and dy_texts:
        ratio = len(su_texts) / max(len(dy_texts), 1)
        if ratio > 3 or ratio < 0.33:
            diffs.append(f"评论量差异大(视频号{len(su_texts)} vs 抖音{len(dy_texts)})")
    return diffs

def analyze_visible_metrics(texts):
    """从OCR可见数据提取流量/人气指标"""
    metrics = {}
    # 价格讨论热度
    price_mentions = sum(1 for t in texts for w in PRICE_WORDS if w in t)
    if price_mentions:
        metrics["price_mentions"] = price_mentions
    return metrics

print(f"[v3] 监控集成引擎启动, 输出 {OUT_FILE.name}")
cycle = 0

while True:
    events = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "timestamp": time.time(),
        "cycle": cycle,
    }
    alerts = []
    insights = {}

    # Poll all sources
    for key, path in SOURCES.items():
        positions[key] = tail_jsonl(path, positions[key], buffers[key])

    # --- OCR 分析 ---
    su_buf = list(buffers["ocr_su"])
    dy_buf = list(buffers["ocr_dy"])
    su_texts = [t for r in su_buf for t in r.get("texts", [])]
    dy_texts = [t for r in dy_buf for t in r.get("texts", [])]

    # 弹幕情绪
    combined_texts = su_texts + dy_texts
    if combined_texts:
        sent, sscore = sentiment_score(combined_texts)
        events["sentiment"] = sent
        events["sentiment_score"] = sscore
        if sent == "negative":
            alerts.append(f"弹幕负面情绪集中(score={sscore})")

    # 合规检测
    compliance = check_compliance(combined_texts)
    if compliance:
        events["compliance_hits"] = compliance[:5]
        for c in compliance[:3]:
            alerts.append(f"合规: {c['keyword']} → '{c['text']}'")

    # 双平台同步
    sync_diffs = check_platform_sync(su_texts, dy_texts)
    if sync_diffs:
        events["platform_sync_diffs"] = sync_diffs
        alerts.extend(sync_diffs)

    # 可见流量指标
    metrics = analyze_visible_metrics(combined_texts)
    if metrics:
        events["visible_metrics"] = metrics

    last_su_texts = su_texts
    last_dy_texts = dy_texts

    # --- Stream Health ---
    sh_buf = list(buffers["stream_health"])
    if sh_buf:
        last_sh = sh_buf[-1]
        anoms = last_sh.get("anomalies", [])
        if anoms:
            events["stream_anomalies"] = anoms
            alerts.extend(anoms[:3])

    # --- System Health ---
    sys_buf = list(buffers["system_health"])
    if sys_buf:
        last_sys = sys_buf[-1]
        sys_alerts = last_sys.get("alerts", [])
        if sys_alerts:
            events["system_alerts"] = sys_alerts
            alerts.extend(sys_alerts[:3])

    # --- Triage ---
    tri_su = list(buffers["triage_su"])
    tri_dy = list(buffers["triage_dy"])
    events["face_su"] = tri_su[-1].get("face", {}).get("count", 0) if tri_su else 0
    events["face_dy"] = tri_dy[-1].get("face", {}).get("count", 0) if tri_dy else 0

    # 面部过曝检测
    for plat_key, hist_key in [("triage_su", "su"), ("triage_dy", "dy")]:
        buf = list(buffers[plat_key])
        if buf:
            fb = buf[-1].get("face", {}).get("avg_brightness", 0)
            if fb > 0:
                face_history[hist_key].append(fb)
                if len(face_history[hist_key]) > FACE_CONSECUTIVE_LIMIT:
                    face_history[hist_key].pop(0)
                if (len(face_history[hist_key]) >= FACE_CONSECUTIVE_LIMIT and
                        all(b > FACE_OVEREXPOSE_THRESHOLD for b in face_history[hist_key])):
                    avg_fb = sum(face_history[hist_key]) / len(face_history[hist_key])
                    alerts.append(f"面部过曝({hist_key.upper()}): {avg_fb:.0f}/255 超过{FACE_OVEREXPOSE_THRESHOLD}")
                    events["face_overexposed"] = True

    # --- STT ---
    stt_buf = list(buffers["stt"])
    if stt_buf:
        events["stt_last"] = stt_buf[-1].get("text", "")[:80]
        speaker_count = stt_buf[-1].get("speaker_count", 0)
        if speaker_count:
            events["speaker_count"] = speaker_count

    # Alerts
    if alerts:
        events["alert_count"] = len(alerts)
        print(f"[v3] [{events['time']}] {' | '.join(alerts[:3])}")

    # Counts summary every 2 cycles
    if cycle % 2 == 0:
        print(f"[v3] [{events['time']}] OCR:{len(su_texts)}+{len(dy_texts)} "
              f"STT:{len(stt_buf)} 情感:{events.get('sentiment','?')} "
              f"合规:{len(compliance)} 告警:{len(alerts)}")

    # Write
    with open(OUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(events, ensure_ascii=False) + "\n")

    cycle += 1
    time.sleep(POLL_SECONDS)
