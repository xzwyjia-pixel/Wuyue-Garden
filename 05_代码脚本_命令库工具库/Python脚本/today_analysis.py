"""today_analysis.py — 今日监控全量分析报告"""
import json, re, sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

target = Path("E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
sys.stdout.reconfigure(encoding="utf-8")

print("=" * 70)
print("  清晨烟火小厨 · 直播监控全量分析报告")
print(f'  生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print("=" * 70)

# load data
stt_lines = [json.loads(l) for l in open(target / "stt.jsonl", encoding="utf-8")]
ocr_su = [json.loads(l) for l in open(target / "live_data_SuSu.jsonl", encoding="utf-8")]
ocr_dy = [json.loads(l) for l in open(target / "live_data_DouYin.jsonl", encoding="utf-8")]
tri_su = [json.loads(l) for l in open(target / "triage_log_SuSu.jsonl", encoding="utf-8")]
tri_dy = [json.loads(l) for l in open(target / "triage_log_DouYin.jsonl", encoding="utf-8")]

all_ts = []
for e in ocr_su + ocr_dy + stt_lines + tri_su + tri_dy:
    ts = e.get("timestamp", 0)
    if ts:
        all_ts.append(ts)

print()
print("── 1. 数据概览 ─────────────────────────")

if all_ts:
    start_dt = datetime.fromtimestamp(min(all_ts))
    end_dt = datetime.fromtimestamp(max(all_ts))
    duration = (max(all_ts) - min(all_ts)) / 3600
    print(f"  直播时段: {start_dt.strftime('%H:%M')} → {end_dt.strftime('%H:%M')}")
    print(f"  直播时长: {duration:.1f}小时")

all_texts_su = [t for r in ocr_su for t in r.get("texts", [])]
all_texts_dy = [t for r in ocr_dy for t in r.get("texts", [])]
print(f"  视频号OCR: {len(ocr_su)}帧, {len(all_texts_su)}条评论")
print(f"  抖音OCR:   {len(ocr_dy)}帧, {len(all_texts_dy)}条评论")
print(f"  STT语音:   {len(stt_lines)}条")
print(f"  Triage视觉: 视频号{len(tri_su)}次 + 抖音{len(tri_dy)}次")

# === 2. 评论分析 ===
print()
print("── 2. 评论分析 ─────────────────────────")

def parse_comments(texts):
    users = Counter()
    msgs = []
    for t in texts:
        m = re.split(r"[:：]\s*", t, maxsplit=1)
        if len(m) == 2 and m[1].strip():
            users[m[0].strip()] += 1
            msgs.append((m[0].strip(), m[1].strip()))
        elif m[0].strip():
            users[m[0].strip()] += 1
    return users, msgs

users_su, msgs_su = parse_comments(all_texts_su)
users_dy, msgs_dy = parse_comments(all_texts_dy)
all_users = Counter()
for u, c in users_su.items():
    all_users[u] += c
for u, c in users_dy.items():
    all_users[u] += c
all_msgs = msgs_su + msgs_dy

print(f"  总互动用户: {len(all_users)}人")
print(f"  视频号: {len(users_su)}人 / 抖音: {len(users_dy)}人")

print()
print("  ── 活跃用户 Top 10 ──")
for i, (u, c) in enumerate(all_users.most_common(10), 1):
    su_cnt = users_su.get(u, 0)
    dy_cnt = users_dy.get(u, 0)
    print(f"  {i:>2}. {u:<16} {c:>3}条 (视频号{su_cnt}/抖音{dy_cnt})")

both = set(users_su.keys()) & set(users_dy.keys())
only_su = set(users_su.keys()) - set(users_dy.keys())
only_dy = set(users_dy.keys()) - set(users_su.keys())
print(f"  双平台用户: {len(both)}人  仅视频号: {len(only_su)}人  仅抖音: {len(only_dy)}人")

msg_counter = Counter(m[1] for m in all_msgs)
print()
print("  ── 高频消息 Top 10 ──")
for msg, cnt in msg_counter.most_common(10):
    print(f"  {cnt:>3}x {msg[:55]}")

# Topic analysis
keywords = {
    "价格讨论": ["多少", "贵", "便宜", "价格", "三千", "送"],
    "地域讨论": ["武夷山", "福建", "闽北", "上饶", "千岛湖", "闽南", "辣"],
    "食材讨论": ["笋", "熏鹅", "鱼", "鸡", "梅干菜", "馒头", "面", "南瓜"],
    "烹饪讨论": ["怎么", "做法", "炒", "炸", "煮", "晒", "焯"],
    "互动聊天": ["早上好", "来了", "拜拜", "早早早", "在的"],
    "家庭情感": ["老婆", "老公", "宝贝", "小宝贝", "大宝贝", "我家"],
    "支持反馈": ["好吃", "不错", "喜欢", "支持", "吃货"],
}
print()
print("  ── 话题热度 ──")
topic_msgs = defaultdict(int)
topic_users = defaultdict(set)
for u, msg in all_msgs:
    for topic, kws in keywords.items():
        if any(kw in msg for kw in kws):
            topic_msgs[topic] += 1
            topic_users[topic].add(u)
            break
for topic, cnt in sorted(topic_msgs.items(), key=lambda x: -x[1]):
    bar = "#" * min(cnt // 3, 20)
    print(f"  {topic:<12} {cnt:>3}条 {len(topic_users[topic]):>2}人 {bar}")

# === 3. STT ===
print()
print("── 3. 语音识别分析 ─────────────────────")

total_stt_dur = 0
stt_texts = []
speaker_set = set()
for r in stt_lines:
    segs = r.get("segments", []) or []
    for seg in segs:
        total_stt_dur += seg.get("end", 0) - seg.get("start", 0)
        spk = seg.get("speaker", "")
        if spk:
            speaker_set.add(spk)
    txt = r.get("text", "")
    if txt.strip():
        stt_texts.append(txt)

print(f"  语音识别总时长: {total_stt_dur:.0f}秒 ({total_stt_dur/60:.1f}分钟)")
print(f"  转写文本量: {sum(len(t) for t in stt_texts)}字")
print(f"  发言者: {len(speaker_set)}人 {speaker_set}")

stt_kws = ["苏苏", "海燕", "好吃", "宝宝", "这个", "怎么", "我们", "大家", "来", "谢谢"]
stt_kw_counter = Counter()
for txt in stt_texts:
    for kw in stt_kws:
        if kw in txt:
            stt_kw_counter[kw] += 1
print("  语音高频出现:")
for kw, cnt in stt_kw_counter.most_common(10):
    bar = "#" * min(cnt // 5, 20)
    print(f"    {kw:<6} {cnt:>3}次 {bar}")

print("  语音片段(最后3条):")
for r in stt_lines[-3:]:
    txt = r.get("text", "")[:100]
    t = r.get("time", "")
    if txt.strip():
        print(f"    [{t}] {txt}")

# Speaker word count
spk_word_count = Counter()
for r in stt_lines:
    spk = r.get("speakers", [])
    txt = r.get("text", "")
    for s in spk:
        spk_word_count[s] += len(txt)
if spk_word_count:
    print("  发言者字数:")
    for spk, wc in spk_word_count.most_common():
        print(f"    {spk}: {wc}字")

# === 4. Triage ===
print()
print("── 4. 视觉质量分析 ─────────────────────")

for plat_label, tri_data in [("视频号", tri_su), ("抖音", tri_dy)]:
    if not tri_data:
        continue
    brightness_vals = [r.get("brightness", 0) for r in tri_data if r.get("brightness")]
    face_counts = [r.get("face", {}).get("count", 0) for r in tri_data]
    face_bright = [
        r.get("face", {}).get("avg_brightness", 0)
        for r in tri_data
        if r.get("face", {}).get("avg_brightness")
    ]
    warm_vals = [r.get("warm_ratio", 0) for r in tri_data]
    food_sat_vals = [r.get("food_saturation", 0) for r in tri_data if r.get("food_saturation")]

    print(f"  [{plat_label}]")
    if brightness_vals:
        bavg = sum(brightness_vals) / len(brightness_vals)
        print(f"    亮度: avg={bavg:.0f} min={min(brightness_vals):.0f} max={max(brightness_vals):.0f}")
    if face_counts:
        face_total = sum(1 for c in face_counts if c > 0)
        pct = face_total / len(face_counts) * 100
        print(f"    人脸检测: {face_total}/{len(face_counts)}帧 ({pct:.0f}%)")
        if face_bright:
            fbg = sum(face_bright) / len(face_bright)
            print(f"    面部亮度: avg={fbg:.0f}")
    if warm_vals:
        wavg = sum(warm_vals) / len(warm_vals) * 100
        print(f"    暖色比: avg={wavg:.1f}%")
    if food_sat_vals:
        favg = sum(food_sat_vals) / len(food_sat_vals)
        print(f"    食物饱和度: avg={favg:.1f}")
    zb_left = [r.get("zone_brightness", {}).get("left", 0) for r in tri_data if r.get("zone_brightness")]
    zb_ctr = [r.get("zone_brightness", {}).get("center", 0) for r in tri_data if r.get("zone_brightness")]
    zb_right = [r.get("zone_brightness", {}).get("right", 0) for r in tri_data if r.get("zone_brightness")]
    if zb_left:
        lavg = sum(zb_left) / len(zb_left)
        cavg = sum(zb_ctr) / len(zb_ctr)
        ravg = sum(zb_right) / len(zb_right)
        print(f"    分区亮度: 左{lavg:.0f} 中{cavg:.0f} 右{ravg:.0f}")

# === 5. Timeline ===
print()
print("── 5. 时间线概览 ───────────────────────")

if tri_su:
    print(f"  视频号Triage: {datetime.fromtimestamp(tri_su[0]['timestamp']).strftime('%H:%M')} → {datetime.fromtimestamp(tri_su[-1]['timestamp']).strftime('%H:%M')}")
if tri_dy:
    print(f"  抖音Triage:   {datetime.fromtimestamp(tri_dy[0]['timestamp']).strftime('%H:%M')} → {datetime.fromtimestamp(tri_dy[-1]['timestamp']).strftime('%H:%M')}")
if ocr_su:
    print(f"  视频号OCR:   {ocr_su[0].get('time','?')} → {ocr_su[-1].get('time','?')}")
if ocr_dy:
    print(f"  抖音OCR:     {ocr_dy[0].get('time','?')} → {ocr_dy[-1].get('time','?')}")

# === 6. Segment ===
print()
print("── 6. 客群分类 ─────────────────────────")

segments = Counter()
for u, msg in all_msgs:
    classified = False
    for topic, kws in keywords.items():
        if any(kw in msg for kw in kws):
            segments[topic] += 1
            classified = True
            break
    if not classified:
        segments["其他"] += 1

total_seg = sum(segments.values())
for seg, cnt in segments.most_common():
    pct = cnt / total_seg * 100 if total_seg else 0
    bar = "#" * int(pct / 2) + "-" * (20 - int(pct / 2))
    print(f"  {seg:<12} {cnt:>3}条 ({pct:5.1f}%) [{bar}]")

# === 7. Insights ===
print()
print("── 7. 核心洞察与建议 ────────────────────")
print()

# User insight
print("  ▸ 用户活跃度:")
if len(only_su) > len(only_dy):
    print(f"    视频号独占用户更多({len(only_su)}人), 建议视频号侧重拉新话术")
else:
    print(f"    抖音独占用户更多({len(only_dy)}人), 建议抖音侧重互动转化")

print(f"    双平台用户{len(both)}人, 属于核心粉丝, 可针对性维护")

# Topic insight
print()
print("  ▸ 内容方向建议:")
sorted_topics = sorted(topic_msgs.items(), key=lambda x: -x[1])
rank = 1
for t, c in sorted_topics[:4]:
    print(f"    {rank}. {t}({c}条) — 观众关注度高, 可增加相关话术")
    rank += 1

# Visual insight
print()
print("  ▸ 画面质量:")
if tri_su:
    last_b = tri_su[-1].get("brightness", 0)
    first_b = tri_su[0].get("brightness", 0)
    trend = "上升" if last_b > first_b else "下降"
    print(f"    视频号亮度趋势: {trend} ({first_b:.0f}→{last_b:.0f})")
    face_total_su = sum(1 for r in tri_su if r.get("face", {}).get("count", 0) > 0)
    print(f"    人脸出镜率: {face_total_su}/{len(tri_su)} ({face_total_su/len(tri_su)*100:.0f}%)")
    if face_total_su / len(tri_su) > 0.8:
        print(f"    ✔ 正面出镜率高, 利于粉丝建立信任")
    else:
        print(f"    ❌ 出镜率偏低, 建议增加主播正面镜头")

# STT insight
print()
print("  ▸ 语音表现:")
print(f"    {total_stt_dur:.0f}秒语音被识别, 直播互动内容丰富")
if spk_word_count:
    for spk, wc in spk_word_count.most_common():
        if wc > 1000:
            print(f"    {spk}发言{wc}字 — 主要发言者")
if stt_kw_counter.get("苏苏", 0) > stt_kw_counter.get("海燕", 0) * 2:
    print("    苏苏为主要发言者, 可增加与海燕互动对话")
else:
    print("    海燕参与度较高, 双人互动模式有效")

print()
print("=" * 70)
print("  分析报告结束")
print("=" * 70)
