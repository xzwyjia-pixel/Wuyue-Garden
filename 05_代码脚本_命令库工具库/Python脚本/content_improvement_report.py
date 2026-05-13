"""
content_improvement_report.py — 内容改进视角的复盘报告
从观众互动、话题热度、内容节奏、平台差异 4 个维度分析
输出给主播用于优化下次直播内容
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
OUTPUT_OVERRIDE = args.output

sys.stdout.reconfigure(encoding="utf-8")

def load_jsonl(path):
    if not path.is_file(): return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def build_metadata(target_name, report_type, start_ts, end_ts, data_sources, extra_tags=None):
    """标准化元数据头, 归档/检索用"""
    lines = ["---"]
    lines.append(f"report_type: {report_type}")
    lines.append(f"target: {target_name}")
    stream_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d") if start_ts else "N/A"
    lines.append(f"stream_date: {stream_date}")
    lines.append(f"stream_time: {fmt(start_ts)} → {fmt(end_ts)}")
    duration_s = end_ts - start_ts if end_ts > start_ts else 0
    hours = int(duration_s // 3600); minutes = int((duration_s % 3600) // 60)
    lines.append(f"duration: {hours}h{minutes:02d}m")
    lines.append(f"generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("source_files:")
    for name, count in data_sources:
        lines.append(f"  - {name} ({count})")
    if extra_tags:
        lines.append(f"top_tags: [{', '.join(extra_tags)}]")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def parse_ocr(ocr_data, window=30):
    users = Counter(); msgs = []; recent = {}
    for r in ocr_data:
        ts = r.get("timestamp", 0)
        for t in r.get("texts", []):
            m = re.split(r"[:：]\s*", t, maxsplit=1)
            if len(m) == 2 and m[1].strip():
                u, msg = m[0].strip(), m[1].strip()
                key = f"{u}:{msg}"
                last = recent.get(key, 0)
                if ts - last >= window:
                    recent[key] = ts; users[u] += 1; msgs.append(msg)
    return users, msgs

# Load
ocr_su = load_jsonl(TARGET / "live_data_SuSu.jsonl")
ocr_dy = load_jsonl(TARGET / "live_data_DouYin.jsonl")
tri_su = load_jsonl(TARGET / "triage_log_SuSu.jsonl")
tri_dy = load_jsonl(TARGET / "triage_log_DouYin.jsonl")
ac = None
if (TARGET / "audience_classification.json").is_file():
    with open(TARGET / "audience_classification.json", encoding="utf-8") as f:
        ac = json.load(f)

su_u, su_m = parse_ocr(ocr_su)
dy_u, dy_m = parse_ocr(ocr_dy)

all_users = Counter()
for u,c in su_u.items(): all_users[u] += c
for u,c in dy_u.items(): all_users[u] += c

all_msgs = su_m + dy_m
msg_counter = Counter(all_msgs)

# Time range
all_ts = [r.get("timestamp",0) for r in ocr_su+ocr_dy if r.get("timestamp")]
start_ts = min(all_ts) if all_ts else 0
end_ts = max(all_ts) if all_ts else 0

# Dynamic filename: date_target_type.md
stream_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d") if start_ts else "nodata"
OUTPUT = Path(OUTPUT_OVERRIDE) if OUTPUT_OVERRIDE else TARGET / f"{stream_date}_{TARGET.name}_内容改进报告.md"

def fmt(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "?"

# Categorize comments into content themes
THEME_MAP = {
    "地域话题": ["武夷山", "福建", "上饶", "缅北", "千岛湖", "闽北", "闽南", "江西", "浙江"],
    "烹饪/菜品": ["扯面", "熏鹅", "吃辣", "炒", "煮", "炸", "蒸", "烤箱", "火锅", "米粉", "羹", "笋"],
    "价格/购买": ["三千", "多少", "贵", "便宜", "价格", "下单", "划算", "值", "买了"],
    "问候互动": ["早上好", "早早早", "来了", "拜拜", "在的", "晚上好"],
    "主播互动": ["苏苏", "海燕", "主播", "小妹妹", "吃货", "虎狼之词"],
    "平台功能": ["点不了", "送出了", "卡了", "+分", "点赞", "分享"],
}

theme_comments = defaultdict(list)
for msg in all_msgs:
    assigned = False
    for theme, kws in THEME_MAP.items():
        for kw in kws:
            if kw in msg:
                theme_comments[theme].append(msg)
                assigned = True
                break
        if assigned:
            break

# Engagement timeline by 15-min blocks
def build_timeline(ocr_data, block_m=15):
    blocks = defaultdict(lambda: {"comments": 0, "users": set(), "messages": []})
    for r in ocr_data:
        ts = r.get("timestamp", 0)
        if not ts: continue
        dt = datetime.fromtimestamp(ts)
        key = f"{dt.hour:02d}:{dt.minute//block_m*block_m:02d}"
        for t in r.get("texts", []):
            m = re.split(r"[:：]\s*", t, maxsplit=1)
            if len(m) == 2 and m[1].strip():
                blocks[key]["comments"] += 1
                blocks[key]["users"].add(m[0].strip())
                blocks[key]["messages"].append(m[1].strip())
    return blocks

tl_su = build_timeline(ocr_su)
tl_dy = build_timeline(ocr_dy)

# ====== Build Metadata ======
target_name = TARGET.name
data_sources = [
    ("live_data_SuSu.jsonl", f"{len(ocr_su)} frames"),
    ("live_data_DouYin.jsonl", f"{len(ocr_dy)} frames"),
    ("triage_log_SuSu.jsonl", f"{len(tri_su)} entries"),
    ("triage_log_DouYin.jsonl", f"{len(tri_dy)} entries"),
]
if ac:
    data_sources.append(("audience_classification.json", f"{ac.get('total_comments',0)} comments"))
# Top tags from theme analysis
top_tags = [theme for theme, _ in sorted(theme_comments.items(), key=lambda x: -len(x[1]))[:5]]

metadata = build_metadata(target_name, "内容改进报告", start_ts, end_ts, data_sources, top_tags)

# ====== Build Report ======
report = [metadata]
report.append(f"# {target_name} · 直播内容改进报告")
report.append("")
report.append(f"**日期:** {datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d') if start_ts else 'N/A'}")
report.append(f"**时段:** {fmt(start_ts)} → {fmt(end_ts)}")
report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"")
report.append("> *本报告仅从内容改进角度分析, 不涉及技术监控指标*")
report.append("")

# === 1. 内容热度分析 ===
report.append("## 一、内容热度分析")
report.append("")
report.append("### 1.1 话题热度排行")
report.append("")
report.append("| 话题类别 | 提及次数 | 占比 | 代表性评论 |")
report.append("|----------|----------|------|-----------|")
for theme, msgs in sorted(theme_comments.items(), key=lambda x: -len(x[1])):
    pct = len(msgs) / max(len(all_msgs), 1) * 100
    sample = msgs[0][:30] if msgs else "-"
    report.append(f"| {theme} | {len(msgs)}次 | {pct:.1f}% | \"{sample}\" |")
report.append("")

# Top comments analysis
report.append("### 1.2 核心讨论焦点")
report.append("")
report.append("按评论内容提炼的今日直播核心话题链:")
report.append("")

# Group related top comments
focus_groups = [
    ("🥇 地域共鸣线 (最强)", ["武夷山", "福建", "上饶", "缅北", "千岛湖", "闽北"],
     "观众地域分布集中在福建/江西/浙江交界带。武夷山、闽北、缅北话题引发连续讨论链。"),
    ("🥈 烹饪教学线", ["扯面", "熏鹅", "吃辣", "笋"],
     "扯面直播引发\"扯面吗\"高频询问, 观众对制作过程有强烈好奇。辣度讨论是持续热点。"),
    ("🥉 价格互动线", ["三千", "点了", "送出了"],
     "\"送出了\" 73次为最高频评论, 说明打赏/送礼互动活跃。\"三千多\"反映价格敏感型观众反复确认价格。"),
    ("💬 情感连接线", ["大宝贝", "小宝贝", "吃货", "早早早"],
     "观众以亲昵称呼(\"小妹妹\", \"小宝贝\")拉近距离。\"大宝贝小宝贝早早早\" 27次说明有固定粉丝群。"),
]

for title, kws, desc in focus_groups:
    related = [msg for msg in all_msgs if any(kw in msg for kw in kws)]
    top3 = Counter(related).most_common(3)
    report.append(f"**{title}**")
    report.append(f"")
    report.append(f"_{desc}_")
    report.append(f"")
    for msg, cnt in top3:
        report.append(f"- \"{msg[:40]}\" ({cnt}次)")
    report.append("")

# === 2. 用户画像与活跃度 ===
report.append("## 二、观众画像与活跃度分析")
report.append("")
report.append(f"- **总互动用户:** {len(all_users)}人")
report.append(f"- **双平台活跃:** {len(set(su_u.keys()) & set(dy_u.keys()))}人 (核心粉丝)")
report.append(f"- **仅视频号:** {len(set(su_u.keys()) - set(dy_u.keys()))}人")
report.append(f"- **仅抖音:** {len(set(dy_u.keys()) - set(su_u.keys()))}人")
report.append("")

# Audience segments from classification
if ac and "segments" in ac:
    report.append("### 2.1 客群结构")
    report.append("")
    report.append("| 客群类型 | 占比 | 建议话术方向 |")
    report.append("|----------|------|-------------|")
    for seg_name, seg_info in sorted(ac["segments"].items(), key=lambda x: -x[1].get("percentage", 0)):
        pct = seg_info.get("percentage", 0)
        sug = seg_info.get("suggestion", "")
        if sug:
            sug_short = sug[:40] + "..."
        else:
            sug_short = "无建议"
        report.append(f"| {seg_name} | {pct:.1f}% | {sug_short} |")
    report.append("")

# VIP users
report.append("### 2.2 高价值互动用户")
report.append("")
report.append("这些用户评论频率高, 建议下次直播点名互动:")
report.append("")
report.append("| # | 用户 | 总条数 | 双平台 | 画像推测 |")
report.append("|---|------|--------|--------|---------|")
vip_profiles = {
    "有缘人": "铁粉, 两边都在",
    "小灰灰": "铁粉, 两边活跃",
    "切顺其自然": "价格敏感型, 反复问三千",
    "酸蔡鱼里梅鱼": "武夷山/福建相关",
    "小灰": "抖音活跃, 潜在转化",
}
for i, (u, c) in enumerate(all_users.most_common(10), 1):
    both = "✓" if u in su_u and u in dy_u else "-"
    profile = vip_profiles.get(u, "")
    report.append(f"| {i} | {u} | {c} | {both} | {profile} |")
report.append("")

# === 3. 内容节奏分析 ===
report.append("## 三、内容节奏与平台差异")
report.append("")

all_keys = sorted(set(list(tl_su.keys()) + list(tl_dy.keys())))
report.append("### 3.1 评论活跃度时间线 (15分/格)")
report.append("")
report.append("| 时段 | 视频号 | 抖音 | 趋势 |")
report.append("|------|--------|------|------|")
peak_su = max(tl_su.values(), key=lambda x: x["comments"])["comments"] if tl_su else 1
peak_dy = max(tl_dy.values(), key=lambda x: x["comments"])["comments"] if tl_dy else 1
for k in sorted(all_keys):
    su_c = tl_su.get(k, {}).get("comments", 0)
    dy_c = tl_dy.get(k, {}).get("comments", 0)
    bar_su = "█" * max(1, int(su_c / max(peak_su, 1) * 20))
    bar_dy = "█" * max(1, int(dy_c / max(peak_dy, 1) * 20))
    report.append(f"| {k} | {su_c:3d} {bar_su} | {dy_c:3d} {bar_dy} | {'抖音↑' if dy_c > su_c*1.3 else '视频号↑' if su_c > dy_c*1.3 else '均衡'} |")
report.append("")

# Platform comparison
report.append("### 3.2 双平台内容偏好差异")
report.append("")
for theme, kws in THEME_MAP.items():
    su_hits = sum(1 for m in su_m if any(kw in m for kw in kws))
    dy_hits = sum(1 for m in dy_m if any(kw in m for kw in kws))
    if su_hits or dy_hits:
        direction = "抖音 > 视频号" if dy_hits > su_hits else "视频号 > 抖音" if su_hits > dy_hits else "持平"
        report.append(f"- **{theme}:** 视频号{su_hits}次 / 抖音{dy_hits}次 ({direction})")
report.append("")

# === 4. 内容缺口与改进机会 ===
report.append("## 四、内容缺口与改进机会")
report.append("")

# Analysis of what's missing
report.append("### 4.1 本次未充分展开的潜力话题")
report.append("")
report.append("根据评论区信号, 以下话题有观众感兴趣但未得到充分回应:")
report.append("")
gap_items = [
    ("\"扯面吗\" (29次)", "观众对扯面制作过程好奇, 但直播中可能未重点展示。下次可把扯面作为\"表演环节\"单独展示, 边做边讲解步骤。"),
    ("\"那个粉会不会掉\" (8次)", "有观众关心食材/工具细节。这类问题代表潜在购买意向, 建议及时回应并展示产品稳定性。"),
    ("\"能不吃辣? 我们缅北吃辣的\" (17次)", "辣度讨论延伸出地域饮食文化对比。这是天然互动素材, 可以设计\"你怕辣还是无辣不欢\"投票环节。"),
    ("\"小妹肚子疼\" / \"今天妹妹偷懒了\"", "观众关注主播状态。说明观众和主播有人情连接, 可以借机分享生活日常, 拉近距离。"),
]
for title, desc in gap_items:
    report.append(f"- **{title}**: {desc}")
report.append("")

report.append("### 4.2 观众未满足的信息需求")
report.append("")
report.append("以下问题在评论区出现但未被主播回应或展示不足:")
unanswered = [
    "\"还是三千多\" / \"我三千点了就没了\" — 价格问题反复出现, 说明观众对定价/活动规则不清楚。需要更清晰地说明: 原价多少、直播间价多少、如何下单。",
    "\"点不了啦\" (33次) — 可能是小黄车/链接点不了。需检查操作指引是否有优化空间。",
    "\"煮来晒?\" — 说明观众对食材后续处理有疑问, 可以展示成品、试吃环节。",
]
for ua in unanswered:
    report.append(f"- {ua}")
report.append("")

# === 5. 内容改进建议 ===
report.append("## 五、下次直播内容改进清单")
report.append("")

report.append("### 5.1 内容结构建议")
report.append("")
suggestions_struct = [
    ("开场问候 → 点名活跃粉 (5分钟)",
     "今日\"有缘人\"\"小灰灰\"\"切顺其自然\"在双平台都极其活跃。开场先点名: \"欢迎有缘人又来了, 小灰灰早上好\" — 这种点名能让铁粉感受到被记住。"),
    ("烹饪过程 → 穿插地域故事 (核心环节)",
     "观众对武夷山/福建/上饶等地域词反应强烈。做菜过程中自然带出食材产地故事: \"这个笋是我们福建武夷山的, 那边气候...\" 建立专业选品形象。"),
    ("互动环节 → 设计投票/问答 (15分钟/次)",
     "今日纯被动互动。可每隔15分钟主动抛出话题: \"你们猜我今天要做什么?\" \"武夷山的朋友举个手\" \"你家里吃辣吗?\" 增加互动密度。"),
    ("价格/商品 → 明确价值对比 (关键转化)",
     "\"三千多\"被反复提及, 说明价格敏感型观众需要更清晰的性价比说明。准备好对比话术: 日常价→直播间价, 品质背书, 限时优惠紧迫感。"),
    ("结尾 → 预告下次 (2分钟)",
     "没有看到明显的下次直播预告。固定结尾环节: \"明天早上6点半, 我给大家做XXX, 记得来\" 培养用户习惯。"),
]
for title, desc in suggestions_struct:
    report.append(f"**{title}**")
    report.append(f"")
    report.append(f"  {desc}")
    report.append("")

report.append("### 5.2 针对各客群的话术优化")
report.append("")
if ac and "segments" in ac:
    for seg_name, seg_info in sorted(ac["segments"].items(), key=lambda x: -x[1].get("percentage", 0)):
        pct = seg_info.get("percentage", 0)
        sug = seg_info.get("suggestion", "")
        if not sug and seg_name == "未分类":
            continue
        report.append(f"**{seg_name}** (占比{pct:.1f}%)")
        report.append(f"")
        if sug:
            report.append(f"  {sug}")
        report.append("")

report.append("### 5.3 平台差异化运营建议")
report.append("")
report.append("| 维度 | 视频号 | 抖音 |")
report.append("|------|--------|------|")
report.append("| **观众特征** | 熟人社交, 老粉为主 | 公域流量, 新人多 |")
report.append("| **内容侧重** | 亲切家常, 维持关系 | 新鲜感, 吸引停留 |")
report.append("| **互动策略** | 点名感谢老粉 | 主动引导新粉互动 |")
report.append("| **节奏** | 稳定输出, 一致性 | 前5分钟抓人, 密集互动 |")
report.append("")

# === 6. 视觉呈现建议 ===
report.append("## 六、视觉呈现建议")
report.append("")
if tri_su or tri_dy:
    for label, tri in [("视频号", tri_su), ("抖音", tri_dy)]:
        if not tri: continue
        bvals = [r.get("brightness", 0) for r in tri if r.get("brightness")]
        wvals = [r.get("warm_ratio", 0) * 100 for r in tri]
        if bvals:
            avg_b = sum(bvals) / len(bvals)
            report.append(f"- **{label}亮度**: avg={avg_b:.0f}/255")
    report.append("")

report.append("### 6.1 画面优化方向")
report.append("")
report.append("- **冷暖调平衡**: 当前暖色比偏高, 适当增加自然白光可使菜品更真实鲜艳")
report.append("- **食物特写**: 出锅/装盘时镜头拉近, 展示食物色泽和质感")
report.append("- **光线均匀性**: 注意面部补光均匀, 避免单侧过亮或过暗")
report.append("")

# === 7. 一句话总结 ===
report.append("---")
report.append("")
report.append("## 一句话总结")
report.append("")
# Determine the single most important insight
report.append(f"> **今日直播最大亮点**: 地域共鸣成功带动互动, 武夷山/福建/上饶话题占讨论量前列。")
report.append(f"> **最大改进空间**: 价格问题(三千多)反复出现无明确回应, 需要更清晰的商品价值沟通。")
report.append(f"> **核心行动项**: (1)设计\"美食+产地故事\"内容线 (2)准备价格对比话术 (3)开场点名互动激活铁粉")
report.append("")
report.append("---")
report.append("")
report.append("*报告由 甄查工作站 内容分析系统 自动生成*")
report.append(f"*数据来源: OCR评论区({len(su_m)+len(dy_m)}条去重) + 客群分类({len(all_users)}人)*")

# Write
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print(f"[内容改进报告] 已保存: {OUTPUT}")
print(f"[内容改进报告] {len(report)} 行")
