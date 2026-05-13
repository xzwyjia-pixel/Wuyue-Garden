"""
behavior_analyzer.py — 主播行为分析引擎
读 JSONL → 输出多维分析: 互动/视觉/语态/时刻/综合评分
"""
import json, time, re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict


PLATFORM_WEIGHTS = {
    "抖音": {"engagement": 35, "visual": 15, "speaking": 20, "authenticity": 10, "popularity": 20,
             "note": "强互动+停留, 投流放大"},
    "视频号": {"engagement": 20, "visual": 20, "speaking": 15, "authenticity": 25, "popularity": 20,
               "note": "社交推荐+真实感, 私域转化"},
}
PLATFORM_FACTORS = {
    "抖音": ["停留时长", "互动率", "付费投流", "憋单话术", "节奏快速"],
    "视频号": ["社交分享", "真实感", "私域转化", "完播率", "粉丝触达"],
}


HOST_TYPE_TIPS = {
    "chef": {"focus": "烹饪技术展示, 食材处理细节, 菜品呈现效果", "dim": "visual"},
    "friendly": {"focus": "亲切互动, 唠家常氛围, 真实感营造", "dim": "authenticity"},
    "sales": {"focus": "促单话术, 限时优惠, 高频转化引导", "dim": "speaking"},
    "educational": {"focus": "知识讲解, 食材科普, 详细步骤说明", "dim": "speaking"},
    "entertainment": {"focus": "才艺表演, 趣味互动, 氛围活跃度", "dim": "popularity"},
}


def analyze(target, live_data, triage_data, stt_data, platform="视频号", host_type="friendly"):
    """Main analysis: return structured host behavior report"""
    now = time.time()
    result = {
        "target": target,
        "overall_score": 0,
        "dimensions": {},
        "moments": [],
        "topics": [],
        "summary": "",
        "stream_duration": 0,
    }

    # ── 互动 Engagement ──
    eng = _analyze_engagement(live_data)
    result["dimensions"]["engagement"] = eng

    # ── 视觉 Visual ──
    vis = _analyze_visual(triage_data)
    result["dimensions"]["visual"] = vis

    # ── 语态 Speaking ──
    spk = _analyze_speaking(stt_data)
    result["dimensions"]["speaking"] = spk

    # ── 真实感 Authenticity ──
    auth = _analyze_authenticity(triage_data, live_data)
    result["dimensions"]["authenticity"] = auth

    # ── 场景 Scene ──
    sce = _analyze_scene(triage_data)
    result["dimensions"]["scene"] = sce

    # ── 带货分析 Sales ──
    sales = _analyze_sales(live_data, stt_data, triage_data)
    result["sales"] = sales

    # ── 观众影响因子 ──
    factors = _analyze_factors(live_data, triage_data, stt_data, eng, vis, spk, auth, sce, sales)
    result["factors"] = factors

    # ── 因子关联分析 ──
    correlations = _analyze_correlations(live_data, triage_data, stt_data)
    result["correlations"] = correlations

    # ── 人气分析 Popularity ──
    pop = _analyze_popularity(live_data, stt_data, eng, spk)
    result["dimensions"]["popularity"] = pop

    # ── 流量分析 Traffic ──
    traffic = _analyze_traffic(live_data)
    result["traffic"] = traffic

    # ── 平台算法匹配 Platform ──
    pf = _analyze_platform(platform, eng, vis, spk, auth, sce, pop, traffic)
    result["platform"] = pf

    # ── 合规风险 Compliance ──
    comp = _analyze_compliance(live_data, stt_data, platform)
    result["compliance"] = comp

    # ── 时刻 Momentum ──
    moments, stream_dur = _detect_moments(live_data, triage_data)
    result["moments"] = moments
    result["stream_duration"] = stream_dur

    # ── 话题 Topics (从 STT + 弹幕) ──
    topics = _extract_topics(live_data, stt_data)
    result["topics"] = topics[:10]

    # ── 综合评分 ──
    scores = [eng["score"], vis["score"], spk["score"], auth["score"]]
    overall = round(sum(scores) / len(scores))
    result["overall_score"] = overall

    # ── 一句话总结 ──
    result["summary"] = _generate_summary(overall, eng, vis, spk, auth, stream_dur, sales=sales, host_type=host_type)

    # ── 主播类型 ──
    ht_info = HOST_TYPE_TIPS.get(host_type, {})
    result["host_type"] = {"type": host_type, "focus": ht_info.get("focus", ""), "key_dim": ht_info.get("dim", "")}

    # ── 改进建议 ──
    dur_min = max(1, stream_dur // 60)
    result["recommendations"] = _generate_recommendations(eng, vis, spk, auth, sce, dur_min, pop, traffic, pf, comp, sales=sales, host_type=host_type)

    return result


def _analyze_engagement(live_data):
    """互动分析: 弹幕量 × 关键词密度 × 转化率"""
    if not live_data:
        return {"score": 0, "chat_volume": 0, "keyword_count": 0, "conversion_count": 0,
                "keyword_density": 0, "conversion_rate": 0}

    total = len(live_data)
    all_kw = Counter()
    conv_count = 0
    total_real = 0
    for entry in live_data:
        for h in entry.get("keyword_hits", []):
            all_kw[h] += 1
        if entry.get("conversion_hits"):
            conv_count += 1
        total_real += entry.get("text_count", 0)

    kw_total = sum(all_kw.values())
    kw_density = round(kw_total / total, 3) if total else 0
    conv_rate = round(conv_count / total, 3) if total else 0
    # Score 0-100: chat_volume (40%) + keyword_density (35%) + conversion_rate (25%)
    vol_score = min(total / 3, 40)  # 120 scans = 40 pts
    kw_score = min(kw_density * 200, 35)  # 0.175 density = 35 pts
    conv_score = min(conv_rate * 500, 25)  # 0.05 rate = 25 pts
    score = round(vol_score + kw_score + conv_score)

    return {
        "score": score,
        "chat_volume": total,
        "keyword_count": kw_total,
        "conversion_count": conv_count,
        "keyword_density": kw_density,
        "conversion_rate": conv_rate,
    }


def _analyze_visual(triage_data):
    """视觉分析: 亮度 × 食物饱和度 × 画面细节"""
    if not triage_data:
        return {"score": 0, "brightness_avg": 0, "food_sat_avg": 0, "detail_avg": 0,
                "warm_ratio_avg": 0, "green_ratio_avg": 0}

    n = len(triage_data)
    sums = Counter()
    for t in triage_data:
        for k in ("brightness", "food_saturation", "detail", "warm_ratio", "green_ratio"):
            sums[k] += t.get(k, 0)
    avg = {k: round(sums[k] / n, 1) for k in sums}

    b_score = min(avg["brightness"] / 2.0, 35)       # brightness 70/120 → 35pts
    f_score = min(avg["food_saturation"] / 3.0, 30)   # sat 45/60 → 30pts
    d_score = min(avg["detail"] / 4.0, 25)             # detail 40/100 → 25pts
    w_score = max(0, 10 - abs(avg["warm_ratio"] - 0.20) * 100)  # warm ratio near 0.20
    score = round(min(b_score + f_score + d_score + w_score, 100))

    return {
        "score": score,
        "brightness_avg": avg["brightness"],
        "food_sat_avg": avg["food_saturation"],
        "detail_avg": avg["detail"],
        "warm_ratio_avg": avg["warm_ratio"],
        "green_ratio_avg": avg["green_ratio"],
    }


CTA_PHRASES = ["关注", "点赞", "分享", "下单", "加粉丝", "小黄车", "购物车",
               "链接", "优惠", "福利", "秒杀", "便宜", "划算", "买", "带一单"]
QUESTION_MARKERS = ["吗", "呢", "吧", "是不是", "有没有", "要不要", "想不想", "大家", "你们"]
EMOTION_MARKS = ["!", "！", "真的", "超级", "太", "非常", "绝了", "太好"]

# 价格/促销关键词
PRICE_PATTERNS = [
    # 价格询问
    ("price_query", ["多少钱", "什么价", "价位", "价格", "贵不贵", "便宜吗", "怎么卖"]),
    # 优惠促销
    ("promotion", ["优惠", "打折", "特价", "限时", "秒杀", "福利", "包邮", "满减",
                   "买一送一", "第二件半价", "送赠品", "领券", "券后"]),
    # 数量/规格
    ("quantity", ["几斤", "几包", "几罐", "多少克", "多大", "几份", "怎么发货", "快递费"]),
    # 品质询问
    ("quality_query", ["新鲜吗", "保质期", "产地", "配料", "辣不辣", "甜不甜",
                       "咸淡", "肥不肥", "老不老", "嫩不嫩"]),
    # 复购信号
    ("repurchase", ["回购", "回够", "再买", "还要", "囤货", "第二次买了", "又来了", "一直买"]),
]

# 观众问题自动归类
QUESTION_CATEGORIES = {
    "菜谱_做法": ["怎么做", "怎么煮", "怎么炒", "步骤", "教程", "做法", "怎么弄", "如何做",
                  "配料", "配方", "比例", "放多少", "几分钟", "火候", "油温"],
    "食材_购买": ["哪里买", "哪里能买", "链接", "怎么买", "买不到", "有没有", "超市有吗",
                  "网购", "链接发一下", "店铺"],
    "口味_评价": ["好吃吗", "味道", "口味", "咸淡", "辣吗", "酸吗", "甜吗", "口感",
                  "嫩不嫩", "脆不脆"],
    "价格_优惠": ["多少钱", "价格", "贵", "便宜", "优惠", "划算", "值", "性价比"],
    "替代_建议": ["可以用什么代替", "可以不放", "没有", "能用", "替代", "换什么"],
}

# 带货分析常量
PRODUCT_CATEGORIES = {
    "肉禽": ["肉", "猪肉", "牛肉", "鸡肉", "鸭", "排骨", "五花肉", "瘦肉", "肉馅", "腊肉"],
    "水产": ["鱼", "虾", "蟹", "鲈鱼", "鲫鱼", "带鱼", "花蛤", "蛏子", "鲍鱼", "海参"],
    "蔬菜": ["青菜", "白菜", "萝卜", "土豆", "番茄", "黄瓜", "茄子", "豆角", "辣椒", "葱"],
    "主食": ["米", "面", "米饭", "馒头", "饺子", "面条", "米粉", "年糕", "糯米", "面粉"],
    "调味": ["油", "盐", "酱", "醋", "酱油", "料酒", "生抽", "老抽", "蚝油", "豆瓣酱"],
    "干货": ["香菇", "木耳", "红枣", "枸杞", "干贝", "虾皮", "紫菜", "海带", "粉丝"],
    "厨具": ["锅", "刀", "砧板", "铲子", "碗", "盘", "砂锅", "铁锅", "不粘锅", "蒸锅"],
    "特产": ["土", "农家", "手工", "自制", "传统", "地道", "家乡", "特色"],
}

SALES_FUNNEL = {
    "attention": {"phrases": ["大家好", "欢迎", "新来的", "开始直播", "看过来", "朋友们", "今天给"], "label": "吸引注意"},
    "interest": {"phrases": ["好吃", "香", "新鲜", "嫩", "软糯", "入味", "酥脆", "浓郁", "Q弹", "劲道"], "label": "激发兴趣"},
    "desire": {"phrases": ["限量", "限时", "仅剩", "最后", "抢", "划算", "优惠", "便宜", "特价", "打折", "福利", "赠送", "超值"], "label": "制造渴望"},
    "action": {"phrases": ["下单", "小黄车", "购物车", "链接", "拍", "点击下方", "一号链接", "二号链接", "去拍", "带一单", "购物袋"], "label": "促成行动"},
}


def _analyze_speaking(stt_data):
    """语态分析 v2: 语速/提问/CTA/情绪/停顿"""
    if not stt_data:
        return {"score": 0, "stt_count": 0, "avg_length": 0, "total_chars": 0,
                "speech_rate": 0, "question_count": 0, "question_ratio": 0,
                "cta_count": 0, "cta_density": 0, "emotion_count": 0,
                "pause_avg": 0, "pause_max": 0, "pause_count": 0}

    total = len(stt_data)
    sorted_data = sorted(stt_data, key=lambda s: s.get("timestamp", 0))
    lengths = [len(s.get("text", "")) for s in sorted_data]
    avg_len = round(sum(lengths) / total) if total else 0
    total_chars = sum(lengths)

    # Speech rate (chars per second), using duration field
    durations = [s.get("duration", 15) for s in sorted_data]
    total_dur = sum(durations)
    speech_rate = round(total_chars / max(total_dur, 1), 2)

    # Question detection
    question_count = 0
    for s in sorted_data:
        text = s.get("text", "")
        for q in QUESTION_MARKERS:
            if q in text:
                question_count += 1
                break

    # CTA phrase detection
    cta_count = 0
    for s in sorted_data:
        text = s.get("text", "")
        for c in CTA_PHRASES:
            if c in text:
                cta_count += 1
                break

    # Emotion markers
    emotion_count = 0
    for s in sorted_data:
        text = s.get("text", "")
        for e in EMOTION_MARKS:
            if e in text:
                emotion_count += 1
                break

    # Pause analysis: time gaps between consecutive entries
    pauses = []
    for i in range(1, len(sorted_data)):
        gap = sorted_data[i].get("timestamp", 0) - sorted_data[i-1].get("timestamp", 0)
        if 3 < gap < 600:  # ignore sub-3s and >10min gaps
            pauses.append(gap)
    pause_avg = round(sum(pauses) / len(pauses), 1) if pauses else 0
    pause_max = round(max(pauses), 1) if pauses else 0
    pause_count = len(pauses)

    question_ratio = round(question_count / total, 3)
    cta_density = round(cta_count / total, 3)
    has_speech_data = total_chars > 0

    # ── 价格/促销信号检测 ──
    price_query_count = 0
    promotion_count = 0
    quantity_count = 0
    quality_query_count = 0
    repurchase_count = 0
    for s in sorted_data:
        text = s.get("text", "")
        for label, patterns in PRICE_PATTERNS:
            for p in patterns:
                if p in text:
                    if label == "price_query": price_query_count += 1
                    elif label == "promotion": promotion_count += 1
                    elif label == "quantity": quantity_count += 1
                    elif label == "quality_query": quality_query_count += 1
                    elif label == "repurchase": repurchase_count += 1
                    break  # one match per text per label

    # ── 观众问题自动归类 ──
    question_categories = {}
    for s in sorted_data:
        text = s.get("text", "")
        for category, patterns in QUESTION_CATEGORIES.items():
            for p in patterns:
                if p in text:
                    question_categories[category] = question_categories.get(category, 0) + 1
                    break

    # Score v2: talk amount(25%) + quality(30%) + engagement(25%) + fluency(20%)
    count_score = min(total * 6, 25)       # 4+ entries → 25pts
    len_score = min(avg_len / 4, 15)       # 60 chars avg → 15pts
    q_score = min(question_ratio * 100, 15)  # 15% questions → 15pts
    cta_score = min(cta_density * 100, 15)   # 15% CTA → 15pts
    e_score = min(emotion_count * 5, 10)      # 2+ emotion → 10pts
    rate_score = 10 if speech_rate > 1.0 else 5  # >1 char/sec → 10pts
    pause_penalty = max(0, 10 - min(pause_avg / 10, 10))  # pauses >20s penalize
    # 价格/促销信号加分 (2分/种)
    price_signal_score = min((price_query_count + promotion_count) * 2, 10)
    score = round(count_score + len_score + q_score + cta_score + e_score + rate_score + pause_penalty + price_signal_score)
    score = min(score, 100)

    return {
        "score": score,
        "stt_count": total,
        "avg_length": avg_len,
        "total_chars": total_chars,
        "speech_rate": speech_rate,
        "question_count": question_count,
        "question_ratio": question_ratio,
        "cta_count": cta_count,
        "cta_density": cta_density,
        "emotion_count": emotion_count,
        "pause_avg": pause_avg,
        "pause_max": pause_max,
        "pause_count": pause_count,
        # 新增
        "price_query_count": price_query_count,
        "promotion_count": promotion_count,
        "quantity_count": quantity_count,
        "quality_query_count": quality_query_count,
        "repurchase_count": repurchase_count,
        "question_categories": question_categories,
    }


def _analyze_authenticity(triage_data, live_data):
    """真实感: triage authentic vs staged score"""
    if not triage_data:
        return {"score": 50, "authentic_avg": 0, "staged_avg": 0, "diff_avg": 0}

    n = len(triage_data)
    sums = Counter()
    for t in triage_data:
        sums["auth"] += t.get("score_authentic", 0)
        sums["staged"] += t.get("score_staged", 0)
        sums["diff"] += t.get("diff", 0)
        sums["color_entropy"] += t.get("color_entropy", 0)
        sums["contrast"] += t.get("contrast", 0)

    avg_auth = round(sums["auth"] / n, 1)
    avg_staged = round(sums["staged"] / n, 1)
    avg_diff = round(sums["diff"] / n, 1)
    avg_ce = round(sums["color_entropy"] / n, 2)

    # Score: authentic - staged, normalized to 0-100
    raw = avg_diff  # diff > 0 = authentic
    score = round(min(max(raw + 50, 0), 100))

    return {
        "score": score,
        "authentic_avg": avg_auth,
        "staged_avg": avg_staged,
        "diff_avg": avg_diff,
        "color_entropy_avg": avg_ce,
        "contrast_avg": round(sums["contrast"] / n, 1),
    }


SCENE_LABELS = {
    "kitchen": "厨房场景", "dining": "餐桌场景", "outdoor": "户外场景",
    "food_prep": "备菜场景", "freeze": "画面静止", "general": "直播场景",
}


def _classify_scene(t):
    """Multi-dim scoring → best scene type match"""
    b = t.get("brightness", 0)
    fs = t.get("food_saturation", 0)
    d = t.get("detail", 0)
    wr = t.get("warm_ratio", 0)
    gr = t.get("green_ratio", 0)
    auth = t.get("score_authentic", 50)
    ce = t.get("color_entropy", 0)
    freeze = t.get("freeze_detected", False)

    # Normalize each metric to ~100 scale, weight per scene
    scores = {
        "kitchen":   (b / 120 * 30 + wr / 0.5 * 25 + d / 100 * 25 + fs / 60 * 20) * (0 if freeze else 1),
        "dining":    (wr / 0.5 * 30 + fs / 60 * 30 + b / 120 * 20 + d / 100 * 20) * (0 if freeze else 1),
        "outdoor":   (gr / 0.8 * 35 + b / 120 * 25 + ce / 6 * 25 + d / 100 * 15) * (0 if freeze else 1),
        "food_prep": (d / 100 * 30 + auth / 100 * 25 + b / 120 * 20 + fs / 60 * 25) * (0 if freeze else 1),
        "freeze":    100 if freeze else max(0, 100 - b * 5),
        "general":   20,
    }
    return max(scores, key=scores.get)


def _analyze_scene(triage_data):
    """Classify scenes, detect transitions, produce timeline & distribution"""
    if not triage_data:
        return {"dominant": "unknown", "scene_label": "未知", "distribution": {},
                "transitions": 0, "timeline": [], "summary": "无画面数据",
                "scene_score": 0}

    timeline = []
    scene_counts = Counter()
    prev_scene = None
    transitions = 0

    for t in triage_data:
        ts = t.get("timestamp", 0)
        scene = _classify_scene(t)
        scene_counts[scene] += 1
        if prev_scene and scene != prev_scene:
            transitions += 1
        prev_scene = scene
        timeline.append({
            "time": datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "?",
            "scene": scene,
            "label": SCENE_LABELS.get(scene, scene),
        })

    total = len(triage_data)
    distribution = {}
    for scene, count in scene_counts.most_common():
        distribution[scene] = {
            "label": SCENE_LABELS.get(scene, scene),
            "count": count,
            "pct": round(count / total * 100, 1),
        }

    dominant = scene_counts.most_common(1)[0][0]

    # Summary: scenes >15% + transition count
    parts = [info["label"] + f"{info['pct']:.0f}%"
             for scene, info in distribution.items() if info["pct"] >= 15]
    summary = " | ".join(parts) if parts else "未知场景"
    summary += f" ({transitions}次切换)"

    # Scene quality score: penalize freeze / low-activity ratio
    freeze_pct = distribution.get("freeze", {}).get("pct", 0)
    scene_score = round(max(0, 100 - freeze_pct * 2))

    return {
        "dominant": dominant,
        "scene_label": SCENE_LABELS.get(dominant, dominant),
        "distribution": distribution,
        "transitions": transitions,
        "timeline": timeline[-40:],
        "summary": summary,
        "score": scene_score,
    }


def _analyze_factors(live_data, triage_data, stt_data, eng, vis, spk, auth, sce, sales=None):
    """List measurable factors that affect viewer engagement & retention"""
    factors = []

    # ---- Speech factors ----
    if spk["stt_count"] > 0:
        factors.append({
            "name": "语速", "dim": "speaking", "value": f"{spk['speech_rate']}字/秒",
            "impact": round(min(spk["speech_rate"] * 30, 25)) if spk["speech_rate"] > 0.5 else 5,
            "desc": "主播说话速度", "direction": "过快赶客, 过慢无聊",
        })
        if spk["question_ratio"] > 0:
            factors.append({
                "name": "提问频率", "dim": "speaking", "value": f"{spk['question_ratio']:.0%}",
                "impact": round(min(spk["question_ratio"] * 100, 20)),
                "desc": "提问引导互动", "direction": "提问频次越高, 弹幕越多",
            })
        if spk["cta_density"] > 0:
            factors.append({
                "name": "转化引导", "dim": "speaking", "value": f"{spk['cta_density']:.0%}",
                "impact": round(min(spk["cta_density"] * 100, 20)),
                "desc": "CTA话术密度", "direction": "转化话术触发购买意愿",
            })
        if spk["emotion_count"] > 0:
            factors.append({
                "name": "情绪感染力", "dim": "speaking", "value": f"{spk['emotion_count']}次",
                "impact": round(min(spk["emotion_count"] * 5, 15)),
                "desc": "感叹/夸张表达", "direction": "带情绪的表达增加留人",
            })
        if spk["pause_avg"] > 5:
            factors.append({
                "name": "停顿时间", "dim": "speaking", "value": f"{spk['pause_avg']}秒",
                "impact": -round(min(spk["pause_avg"] / 2, 15)),
                "desc": "句间停顿", "direction": "停顿过长→观众流失",
            })

    # ---- Engagement factors ----
    if live_data:
        factors.append({
            "name": "弹幕量", "dim": "engagement", "value": str(len(live_data)),
            "impact": round(min(len(live_data) / 3, 20)),
            "desc": "评论活跃度", "direction": "弹幕多→直播间活跃",
        })
        if eng["keyword_density"] > 0:
            factors.append({
                "name": "关键词密度", "dim": "engagement", "value": f"{eng['keyword_density']:.2f}",
                "impact": round(min(eng["keyword_density"] * 100, 20)),
                "desc": "弹幕中关键词占比", "direction": "高密度→内容相关性强",
            })
        if eng["conversion_rate"] > 0:
            factors.append({
                "name": "转化率", "dim": "engagement", "value": f"{eng['conversion_rate']:.1%}",
                "impact": round(min(eng["conversion_rate"] * 200, 25)),
                "desc": "意向转化比例", "direction": "高转化→带货效果好",
            })

    # ---- Visual factors ----
    if triage_data:
        if vis["brightness_avg"] > 0:
            b_impact = round(min(vis["brightness_avg"] / 4, 15))
            if vis["brightness_avg"] < 40:
                b_impact = -5  # too dark penalizes
            factors.append({
                "name": "画面亮度", "dim": "visual", "value": str(vis["brightness_avg"]),
                "impact": b_impact,
                "desc": "直播视觉清晰度", "direction": "亮度过低影响观看体验",
            })
        if vis["food_sat_avg"] > 0:
            factors.append({
                "name": "食物饱和度", "dim": "visual", "value": str(vis["food_sat_avg"]),
                "impact": round(min(vis["food_sat_avg"] / 2, 15)),
                "desc": "美食画面诱人程度", "direction": "饱和度高→更有食欲→互动强",
            })

    # ---- Authenticity factors ----
    if triage_data:
        factors.append({
            "name": "真实感", "dim": "authenticity", "value": f"{auth['authentic_avg']:.0f}",
            "impact": round(min(auth["diff_avg"] * 2, 15)) if auth["diff_avg"] > 0 else 0,
            "desc": "画面真实vs摆拍", "direction": "真实感强→用户信任→转化提升",
        })

    # ---- Scene factors ----
    if sce["distribution"]:
        scene_count = len(sce["distribution"])
        factors.append({
            "name": "场景丰富度", "dim": "scene", "value": f"{scene_count}种",
            "impact": round(min(scene_count * 5, 15)),
            "desc": "直播场景多样性", "direction": "场景多→内容新鲜感强→留人",
        })
        if sce["transitions"] > 0:
            factors.append({
                "name": "场景切换", "dim": "scene", "value": f"{sce['transitions']}次",
                "impact": round(min(sce["transitions"] * 3, 10)),
                "desc": "场景变化频次", "direction": "适度切换增加节奏感",
            })

    # ---- Sales factors ----
    if sales and stt_data:
        if sales.get("product_count", 0) > 0:
            factors.append({
                "name": "产品提及", "dim": "sales", "value": f"{sales['product_count']}次",
                "impact": round(min(sales["product_count"] * 3, 20)),
                "desc": "直播中提及产品的频次", "direction": "高提及→带货认知强",
            })
            factors.append({
                "name": "销售漏斗", "dim": "sales", "value": f"{sales['funnel_completeness']}/4阶段",
                "impact": round(sales["funnel_completeness"] * 5),
                "desc": "吸引→兴趣→渴望→行动", "direction": "完整漏斗提升转化率",
            })
        if sales.get("action_density", 0) > 0.05:
            factors.append({
                "name": "行动号召", "dim": "sales", "value": f"{sales['action_density']:.0%}",
                "impact": round(min(sales["action_density"] * 80, 20)),
                "desc": "下单引导话术密度", "direction": "高密度→转化机会多",
            })
        if sales.get("urgency_density", 0) > 0.02:
            factors.append({
                "name": "促销紧迫感", "dim": "sales", "value": f"{sales['urgency_density']:.0%}",
                "impact": round(min(sales["urgency_density"] * 60, 15)),
                "desc": "限时限量话术", "direction": "紧迫感促成冲动消费",
            })

    factors.sort(key=lambda f: abs(f["impact"]), reverse=True)
    return factors


def _analyze_correlations(live_data, triage_data, stt_data):
    """Cross-dimension correlation: find factor pairs that move together"""
    if not live_data or not triage_data or not stt_data:
        return []

    correlations = []

    # Build aligned time series (bucket by 5-min window)
    def bucket_data(entries, key, agg="avg", default=0):
        """Group entries into 5-min buckets. Handles both scalars and lists."""
        buckets = {}
        for e in entries:
            ts = e.get("timestamp", 0)
            if not ts:
                continue
            b = int(ts // 300) * 300
            val = e.get(key, default)
            if isinstance(val, (list, tuple)):
                val = len(val)  # use list length as value
            if b not in buckets:
                buckets[b] = []
            buckets[b].append(val)
        return {t: (sum(vals) / len(vals) if agg == "avg" else sum(vals))
                for t, vals in sorted(buckets.items())}

    live_kw_series = bucket_data(live_data, "keyword_hits", agg="sum")
    live_conv_series = bucket_data(live_data, "conversion_hits", agg="sum")

    triage_brightness = bucket_data(triage_data, "brightness")
    triage_food_sat = bucket_data(triage_data, "food_saturation")
    triage_warm = bucket_data(triage_data, "warm_ratio")

    # STT-derived time data
    stt_by_bucket = {}
    for s in stt_data:
        ts = s.get("timestamp", 0)
        if not ts:
            continue
        b = int(ts // 300) * 300
        if b not in stt_by_bucket:
            stt_by_bucket[b] = []
        stt_by_bucket[b].append(s.get("text", ""))

    stt_question_series = {}
    stt_cta_series = {}
    stt_len_series = {}
    for b, texts in stt_by_bucket.items():
        full = " ".join(texts)
        stt_question_series[b] = sum(1 for q in QUESTION_MARKERS if q in full)
        stt_cta_series[b] = sum(1 for c in CTA_PHRASES if c in full)
        stt_len_series[b] = len(full)

    def pearson(x, y):
        """Simple correlation -1..1"""
        n = min(len(x), len(y))
        if n < 3:
            return 0
        x_vals = list(x.values())[-n:]
        y_vals = list(y.values())[-n:]
        mx, my = sum(x_vals)/n, sum(y_vals)/n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x_vals, y_vals))
        den = (sum((xi - mx)**2 for xi in x_vals) * sum((yi - my)**2 for yi in y_vals))**0.5
        return round(num / den, 2) if den else 0

    # Find overlapping time windows
    common_times = set(live_kw_series.keys()) & set(triage_brightness.keys())

    # 1. Question count vs Keyword hits (does asking drive chat?)
    q_kw = {t: stt_question_series.get(t, 0) for t in common_times}
    kw_b = {t: live_kw_series[t] for t in common_times & set(live_kw_series.keys())}
    r1 = pearson(q_kw, kw_b)
    if abs(r1) > 0.2:
        correlations.append({
            "factor_a": "提问频次", "factor_b": "关键词命中",
            "r": r1, "interpretation": "提问→弹幕增长" if r1 > 0 else "提问→弹幕减少",
        })

    # 2. CTA count vs Conversion hits
    cta_c = {t: stt_cta_series.get(t, 0) for t in common_times}
    conv_c = {t: live_conv_series[t] for t in common_times & set(live_conv_series.keys())}
    r2 = pearson(cta_c, conv_c)
    if abs(r2) > 0.2:
        correlations.append({
            "factor_a": "CTA话术", "factor_b": "转化意向",
            "r": r2, "interpretation": "话术→转化有效" if r2 > 0 else "话术与转化负相关",
        })

    # 3. Brightness vs Keyword hits
    bright_vs_kw = {t: triage_brightness[t] for t in common_times & set(triage_brightness.keys())}
    r3 = pearson(bright_vs_kw, kw_b)
    if abs(r3) > 0.15:
        correlations.append({
            "factor_a": "画面亮度", "factor_b": "关键词命中",
            "r": r3, "interpretation": "亮画面→更活跃" if r3 > 0 else "暗画面→互动下降",
        })

    # 4. Food saturation vs Keyword hits
    food_vs_kw = {t: triage_food_sat[t] for t in common_times & set(triage_food_sat.keys())}
    r4 = pearson(food_vs_kw, kw_b)
    if abs(r4) > 0.15:
        correlations.append({
            "factor_a": "食物饱和度", "factor_b": "关键词命中",
            "r": r4, "interpretation": "诱人画面→更多美食讨论" if r4 > 0 else "饱和度与互动关联弱",
        })

    # 5. Speaking length vs Keyword hits
    if stt_len_series:
        stt_vs_kw = {t: stt_len_series.get(t, 0) for t in common_times}
        r5 = pearson(stt_vs_kw, kw_b)
        if abs(r5) > 0.2:
            correlations.append({
                "factor_a": "说话量", "factor_b": "关键词命中",
                "r": r5, "interpretation": "话说多→弹幕多" if r5 > 0 else "话说多→弹幕反而少",
            })

    correlations.sort(key=lambda c: abs(c["r"]), reverse=True)
    return correlations[:8]


def _detect_moments(live_data, triage_data):
    """检测行为时刻: 关键词爆发/转化/静默/开始/结束"""
    moments = []
    duration = 0

    if not live_data:
        return moments, 0

    timestamps = [e.get("timestamp", 0) for e in live_data if e.get("timestamp")]
    if not timestamps:
        return moments, 0

    start_ts = min(timestamps)
    end_ts = max(timestamps)
    duration = int(end_ts - start_ts)

    # Stream start
    start_time = datetime.fromtimestamp(start_ts).strftime("%H:%M")
    moments.append({"time": start_time, "type": "start", "label": "开始直播", "detail": ""})

    # Find keyword spikes
    kw_counts = []
    for e in live_data:
        ts = e.get("timestamp", 0)
        n = len(e.get("keyword_hits", []))
        if ts:
            kw_counts.append((ts, n, e.get("keyword_hits", [])))

    if kw_counts:
        vals = [c[1] for c in kw_counts]
        avg_kw = sum(vals) / len(vals) if vals else 0
        threshold = avg_kw * 2.5
        for ts, n, hits in kw_counts:
            if n >= threshold and n >= 2:
                tstr = datetime.fromtimestamp(ts).strftime("%H:%M")
                kw_list = ", ".join(hits[:3])
                moments.append({"time": tstr, "type": "kw_spike", "label": f"关键词爆发({n})", "detail": kw_list})

    # Conversion moments
    for e in live_data:
        if e.get("conversion_hits"):
            ts = e.get("timestamp", 0)
            if ts:
                tstr = datetime.fromtimestamp(ts).strftime("%H:%M")
                conv_list = ", ".join(e["conversion_hits"][:3])
                moments.append({"time": tstr, "type": "conversion", "label": "转化意向", "detail": conv_list})

    # Stream end detection (from triage freeze)
    for t in triage_data:
        if t.get("freeze_detected"):
            ts = t.get("timestamp", 0)
            if ts:
                tstr = datetime.fromtimestamp(ts).strftime("%H:%M")
                moments.append({"time": tstr, "type": "freeze", "label": "画面静止", "detail": ""})

    # End
    end_time = datetime.fromtimestamp(end_ts).strftime("%H:%M")
    moments.append({"time": end_time, "type": "end", "label": "最后数据", "detail": ""})

    # Sort by time, remove duplicates (keep first of each type near same time)
    moments.sort(key=lambda m: m.get("time", ""))
    moments = _dedup_moments(moments)

    return moments, duration


def _dedup_moments(moments):
    """Remove moments within 3 min of same type"""
    if not moments:
        return moments
    result = [moments[0]]
    for m in moments[1:]:
        last = result[-1]
        if m["type"] == last["type"]:
            # Keep the first of each type cluster
            continue
        result.append(m)
    return result


def _extract_topics(live_data, stt_data):
    """提取话题: 从弹幕关键词 + STT 文本"""
    kw_counter = Counter()
    for entry in live_data:
        for h in entry.get("keyword_hits", []):
            kw_counter[h] += 1

    # Add STT words
    for s in stt_data:
        text = s.get("text", "")
        # Simple keyword extraction: look for known cooking-related terms
        for w in ["菜", "肉", "鱼", "鸡", "蛋", "米", "面", "油", "盐",
                  "酱", "醋", "锅", "火", "水", "汤", "煮", "炒", "蒸", "炸",
                  "妈妈", "小时候", "家乡", "农村", "新鲜", "土"]:
            if w in text:
                kw_counter[w] += 1

    return kw_counter.most_common(15)


HOST_NAMES = {"苏苏": "苏苏", "姐": "姐", "海燕": "海燕"}


def _detect_host(text):
    """Detect which host name appears in text, return host key or None"""
    if not text:
        return None
    # Check in priority order: 姐 mentioned = 姐's segment
    for hk in ["姐", "海燕", "苏苏"]:
        if hk in text:
            return hk
    return None


def _segment_by_host(live_data, stt_data):
    """Cluster data by host mentions → time segments per host"""
    # Build host timeline: [(timestamp, host), ...]
    host_signals = []

    # From STT text
    for s in stt_data:
        ts = s.get("timestamp", 0)
        text = s.get("text", "")
        h = _detect_host(text)
        if h and ts:
            host_signals.append((ts, h))

    # From live_data keyword_hits
    for e in live_data:
        ts = e.get("timestamp", 0)
        for kw in e.get("keyword_hits", []):
            h = _detect_host(kw)
            if h and ts:
                host_signals.append((ts, h))

    if not host_signals:
        return {}

    # Sort by timestamp and find dominant host per 5-min window
    host_signals.sort(key=lambda x: x[0])
    window_min = 300  # 5 min

    windows = defaultdict(list)
    for ts, h in host_signals:
        w = int(ts // window_min) * window_min
        windows[w].append(h)

    # Each window gets the most mentioned host
    window_hosts = {}
    for w, hosts in windows.items():
        counter = Counter(hosts)
        dominant = counter.most_common(1)[0][0]
        window_hosts[w] = dominant

    # Merge consecutive same-host windows into segments
    segments = []
    current_host = None
    seg_start = None
    seg_end = None

    for w in sorted(window_hosts.keys()):
        h = window_hosts[w]
        if h != current_host:
            if current_host and seg_start:
                segments.append({
                    "host": current_host,
                    "start_ts": seg_start,
                    "end_ts": seg_end or seg_start,
                    "start": datetime.fromtimestamp(seg_start).strftime("%H:%M"),
                    "end": datetime.fromtimestamp(seg_end or seg_start).strftime("%H:%M"),
                })
            current_host = h
            seg_start = w
            seg_end = w + window_min
        else:
            seg_end = w + window_min

    # Last segment
    if current_host and seg_start:
        segments.append({
            "host": current_host,
            "start_ts": seg_start,
            "end_ts": seg_end or seg_start,
            "start": datetime.fromtimestamp(seg_start).strftime("%H:%M"),
            "end": datetime.fromtimestamp(seg_end or seg_start).strftime("%H:%M"),
        })

    return segments


def analyze_per_host(target, live_data, triage_data, stt_data):
    """Run segmented analysis per detected host"""
    segments = _segment_by_host(live_data, stt_data)
    if not segments:
        return {"hosts": [], "note": "未检测到多主播"}

    results = []
    for seg in segments:
        h = seg["host"]
        st = seg["start_ts"]
        et = seg["end_ts"]

        # Filter data for this segment
        seg_live = [e for e in live_data if st <= e.get("timestamp", 0) <= et]
        seg_triage = [t for t in triage_data if st <= t.get("timestamp", 0) <= et]
        seg_stt = [s for s in stt_data if st <= s.get("timestamp", 0) <= et]

        if not seg_live and not seg_triage and not seg_stt:
            continue

        seg_result = analyze(f"{target}[{h}]", seg_live, seg_triage, seg_stt)
        results.append({
            "host": h,
            "segment_start": seg["start"],
            "segment_end": seg["end"],
            "duration": int((et - st) / 60),
            "data_points": len(seg_live),
            "overall_score": seg_result["overall_score"],
            "summary": seg_result["summary"],
            "dimensions": seg_result["dimensions"],
        })

    results.sort(key=lambda r: r["segment_start"] if r.get("segment_start") else "")
    return {"hosts": results, "note": ""}


# ── 违禁词库 (按平台+严重程度) ──
BANNED_WORDS = {
    "通用": {
        "high": [
            ("治病", "医疗承诺"), ("治愈", "医疗承诺"), ("药到病除", "医疗承诺"),
            ("疗效", "医疗承诺"), ("治疗", "医疗承诺"), ("抗癌", "医疗承诺"),
            ("防癌", "医疗承诺"), ("降糖", "医疗承诺"), ("降压", "医疗承诺"),
            ("减肥药", "医疗承诺"), ("药", "医疗承诺"),
            ("稳赚", "金融保证"), ("保本", "金融保证"), ("收益率", "金融保证"),
            ("最", "极限词"), ("第一", "极限词"), ("最好", "极限词"), ("唯一", "极限词"),
            ("全网最低", "虚假宣传"), ("销量第一", "虚假宣传"), ("永久", "极限词"),
            ("绝对", "绝对化用语"), ("一定", "绝对化用语"),
        ],
        "medium": [
            ("国家", "国家相关"), ("国家级", "国家相关"), ("最好", "极限词"),
            ("超级", "夸大宣传"), ("无敌", "夸大宣传"), ("极好", "夸大宣传"),
            ("纯天然", "食品夸大宣传"), ("野生", "食品夸大宣传"), ("土法", "食品夸大宣传"),
            ("祖传", "食品夸大宣传"), ("秘制", "食品夸大宣传"),
            ("有机", "资质虚假宣传"), ("零添加", "食品夸大宣传"), ("无添加", "食品夸大宣传"),
            ("美白", "化妆品夸大"), ("祛斑", "化妆品夸大"), ("除皱", "化妆品夸大"),
            ("抗衰老", "化妆品夸大"), ("紧致", "化妆品夸大"), ("逆龄", "化妆品夸大"),
            ("淘宝", "竞品提及"), ("京东", "竞品提及"), ("拼多多", "竞品提及"),
        ],
        "low": [
            ("免费领", "诱导互动"), ("不转不是", "诱导互动"), ("必须转发", "诱导互动"),
            ("加微信", "私域导流"), ("公众号", "私域导流"), ("二维码", "私域导流"),
        ],
    },
    "抖音": {
        "high": [("微信", "竞品平台"), ("淘宝搜索", "竞品导流")],
        "medium": [("关注抽奖", "诱导互动"), ("点赞抽奖", "诱导互动")],
    },
    "视频号": {
        "medium": [("个人微信", "私域导流"), ("微信群", "私域导流")],
        "low": [("加我好友", "私域导流"), ("扫码", "私域导流")],
    },
}
BANNED_WEIGHTS = {"high": 25, "medium": 10, "low": 5}


def _analyze_compliance(live_data, stt_data, platform="视频号"):
    """Scan text data for platform banned words → risk score + violation log"""
    violations = []
    risk_score = 100  # start perfect, deduct

    # Collect all text
    texts = []
    for s in stt_data:
        texts.append(("stt", s.get("text", "")))
    for e in live_data:
        for kw in e.get("keyword_hits", []):
            texts.append(("live", kw))
        for t in e.get("real_texts", []):
            texts.append(("chat", t))

    if not texts:
        return {"risk_score": 100, "violations": [], "risk_level": "safe", "found_words": [], "traffic_risk_pct": 0}

    # Scan each text against banned words
    found = set()
    for src, txt in texts:
        for category, words in BANNED_WORDS.items():
            if category != "通用" and category != platform:
                continue
            for severity, word_list in words.items():
                for banned_word, category_name in word_list:
                    if banned_word in txt and (banned_word, category_name, severity) not in found:
                        found.add((banned_word, category_name, severity))
                        weight = BANNED_WEIGHTS.get(severity, 5)
                        violations.append({
                            "word": banned_word,
                            "category": category_name,
                            "severity": severity,
                            "weight": weight,
                            "source": src,
                        })
                        risk_score -= weight

    risk_score = max(0, risk_score)
    total_risk = 100 - risk_score

    # Determine risk level
    if total_risk >= 40:
        risk_level = "critical"
    elif total_risk >= 20:
        risk_level = "warning"
    elif total_risk >= 5:
        risk_level = "low"
    else:
        risk_level = "safe"

    return {
        "risk_score": risk_score,
        "violations": violations,
        "risk_level": risk_level,
        "found_words": [v["word"] for v in violations],
        "traffic_risk_pct": total_risk,
        "summary": f"检测到{len(violations)}项违规, 限流风险{total_risk}%",
    }


def _analyze_platform(platform, eng, vis, spk, auth, sce, pop, traffic):
    """Platform algorithm fit score + key factors per platform"""
    w = PLATFORM_WEIGHTS.get(platform, PLATFORM_WEIGHTS["视频号"])
    factors = PLATFORM_FACTORS.get(platform, PLATFORM_FACTORS["视频号"])

    eng_w = eng["score"] * w["engagement"] / 100
    vis_w = vis["score"] * w["visual"] / 100
    spk_w = spk["score"] * w["speaking"] / 100
    auth_w = auth["score"] * w["authenticity"] / 100
    pop_w = (pop or {}).get("score", 50) * w["popularity"] / 100
    fit_score = round(eng_w + vis_w + spk_w + auth_w + pop_w)

    # Per-factor evaluation
    evals = []
    if "停留时长" in factors:
        vel = (pop or {}).get("chat_velocity", 0)
        evals.append({"factor": "停留时长", "score": "优" if vel > 3 else "良" if vel > 1 else "待优化",
                      "value": f"{vel}条/分", "tip": "增加互动钩子延长停留"})
    if "互动率" in factors:
        evals.append({"factor": "互动率", "score": "优" if eng["keyword_density"] > 0.3 else "良" if eng["keyword_density"] > 0.1 else "待优化",
                      "value": f"{eng['keyword_density']:.2f}", "tip": "引导弹幕互动提升推荐量"})
    if "真实感" in factors:
        evals.append({"factor": "真实感", "score": "优" if auth["diff_avg"] > 10 else "良" if auth["diff_avg"] > 0 else "待优化",
                      "value": f"{auth['diff_avg']:.0f}", "tip": "真实场景提升社交推荐" if platform == "视频号" else "自然感利于引流"})
    if "社交分享" in factors:
        conv = eng.get("conversion_count", 0)
        evals.append({"factor": "社交分享", "score": "良" if conv > 0 else "待优化",
                      "value": f"{conv}次转化", "tip": "增加分享引导'转发到群'"})
    if "付费投流" in factors:
        spikes = (traffic or {}).get("spike_count", 0)
        evals.append({"factor": "付费投流", "score": "良" if spikes >= 2 else "待优化" if spikes == 1 else "未利用",
                      "value": f"{spikes}次脉冲", "tip": "千川投放锁定高峰时段"})
    if "节奏快速" in factors:
        sr = spk.get("speech_rate", 0)
        evals.append({"factor": "节奏快速", "score": "优" if sr > 1.5 else "良" if sr > 0.8 else "待优化",
                      "value": f"{sr}字/秒", "tip": "快节奏适配抖音算法"})

    return {
        "platform": platform,
        "fit_score": fit_score,
        "note": PLATFORM_WEIGHTS.get(platform, w)["note"],
        "factors": factors,
        "evals": evals,
        "weight_breakdown": w,
    }


def _analyze_popularity(live_data, stt_data, eng, spk):
    """人气分析: 弹幕增速/高峰时段/互动循环/留存推断"""
    if not live_data:
        return {"score": 0, "chat_velocity": 0, "peak_hour": "", "engagement_loops": 0,
                "peak_chats": 0, "avg_chats_per_min": 0, "trend": "stable"}

    timestamps = [e.get("timestamp", 0) for e in live_data if e.get("timestamp")]
    if not timestamps:
        return {"score": 0, "chat_velocity": 0, "peak_hour": "", "engagement_loops": 0,
                "peak_chats": 0, "avg_chats_per_min": 0, "trend": "stable"}

    start_ts = min(timestamps)
    end_ts = max(timestamps)
    duration_sec = max(end_ts - start_ts, 60)
    duration_min = duration_sec / 60

    # Chat velocity (chats per minute)
    chat_velocity = round(len(timestamps) / duration_min, 1)

    # Peak detection: which 15-min window has most chats
    window_15 = 900
    peak_windows = Counter()
    for ts in timestamps:
        w = int(ts // window_15) * window_15
        peak_windows[w] += 1
    if peak_windows:
        peak_ts = max(peak_windows, key=peak_windows.get)
        peak_hour = datetime.fromtimestamp(peak_ts).strftime("%H:%M")
        peak_chats = peak_windows[peak_ts]
    else:
        peak_hour, peak_chats = "", 0

    # Engagement loops: detect question→response pairs in STT
    loops = 0
    if len(stt_data) >= 2:
        sorted_stt = sorted(stt_data, key=lambda s: s.get("timestamp", 0))
        for i in range(len(sorted_stt) - 1):
            text = sorted_stt[i].get("text", "")
            # If host asks a question, look for chat response in next window
            for q in QUESTION_MARKERS:
                if q in text:
                    # Check if next STT entry shows follow-up (response to chat)
                    next_text = sorted_stt[i + 1].get("text", "")
                    if len(next_text) > 5:  # meaningful response
                        loops += 1
                    break

    # Trend: compare first half vs second half activity
    mid_ts = start_ts + duration_sec / 2
    first_half = sum(1 for ts in timestamps if ts <= mid_ts)
    second_half = sum(1 for ts in timestamps if ts > mid_ts)
    ratio = second_half / max(first_half, 1)
    if ratio > 1.3:
        trend = "rising"
    elif ratio < 0.7:
        trend = "declining"
    else:
        trend = "stable"

    # Scoring: velocity(40%) + loops(25%) + trend(20%) + peak(15%)
    vel_score = min(chat_velocity * 8, 40)
    loop_score = min(loops * 10, 25)
    trend_score = 20 if trend == "rising" else (10 if trend == "stable" else 0)
    peak_score = min(peak_chats / 10, 15)
    score = round(min(vel_score + loop_score + trend_score + peak_score, 100))

    return {
        "score": score,
        "chat_velocity": chat_velocity,
        "peak_hour": peak_hour,
        "peak_chats": peak_chats,
        "avg_chats_per_min": chat_velocity,
        "engagement_loops": loops,
        "trend": trend,
        "first_half": first_half,
        "second_half": second_half,
    }


def _analyze_traffic(live_data):
    """流量分析: 弹幕脉冲检测 → 推断投流效果"""
    if not live_data:
        return {"spike_count": 0, "traffic_peaks": [], "best_ad_window": "",
                "organic_ratio": 0, "traffic_score": 0, "suggestion": ""}

    timestamps = [e.get("timestamp", 0) for e in live_data if e.get("timestamp")]
    if len(timestamps) < 10:
        return {"spike_count": 0, "traffic_peaks": [], "best_ad_window": "",
                "organic_ratio": 0, "traffic_score": 0, "suggestion": "数据不足"}

    # 5-min bucket chat counts → detect spikes
    bucket_s = 300
    buckets = Counter()
    for ts in timestamps:
        buckets[int(ts // bucket_s) * bucket_s] += 1
    if not buckets:
        return {}

    vals = list(buckets.values())
    avg = sum(vals) / len(vals)
    threshold = avg * 2.0

    spikes = []
    for w, cnt in sorted(buckets.items()):
        if cnt >= threshold and cnt >= 3:
            spikes.append({
                "time": datetime.fromtimestamp(w).strftime("%H:%M"),
                "chats": cnt,
                "multiplier": round(cnt / avg, 1),
            })

    # Best ad window = peak chat bucket
    peak_bucket = max(buckets, key=buckets.get)
    best_window = datetime.fromtimestamp(peak_bucket).strftime("%H:%M")

    # Organic ratio: non-spike traffic / total
    spike_total = sum(s["chats"] for s in spikes)
    total_chats = sum(vals)
    organic_ratio = round(1 - spike_total / max(total_chats, 1), 2)

    # Score: more spikes with high multiplier = good ad effect
    spike_score = min(len(spikes) * 10, 40)
    mult_score = min(sum(s["multiplier"] for s in spikes) * 3, 30) if spikes else 0
    organic_score = max(0, min(organic_ratio * 50, 30))
    traffic_score = round(spike_score + mult_score + organic_score)

    # Suggestion
    if len(spikes) >= 2:
        suggestion = f"投流效果明显, 建议在{best_window}前后加大投放"
    elif len(spikes) == 1:
        suggestion = f"检测到单次流量脉冲, 建议增加投流频次, 集中在{best_window}时段"
    else:
        suggestion = "未检测到明显流量脉冲, 建议尝试小预算投流测试"

    return {
        "spike_count": len(spikes),
        "traffic_peaks": spikes[:5],
        "best_ad_window": best_window,
        "organic_ratio": organic_ratio,
        "traffic_score": traffic_score,
        "suggestion": suggestion,
    }


# ── 带货分析 ──
def _analyze_sales(live_data, stt_data, triage_data):
    """带货分析: 产品提及/销售漏斗/促销信号/展示效果/展示时长"""
    prod_mentions = Counter()
    prod_timeline = []

    for s in stt_data:
        ts = s.get("timestamp", 0)
        text = s.get("text", "")
        for cat, keywords in PRODUCT_CATEGORIES.items():
            for kw in keywords:
                if kw in text:
                    prod_mentions[cat] += 1
                    prod_timeline.append((ts, kw, cat))
                    break

    total_stt = max(len(stt_data), 1)

    funnel_stages = {}
    for stage, info in SALES_FUNNEL.items():
        count = 0
        active_phrases = []
        for s in stt_data:
            text = s.get("text", "")
            for phrase in info["phrases"]:
                if phrase in text:
                    count += 1
                    if phrase not in active_phrases:
                        active_phrases.append(phrase)
                    break
        funnel_stages[stage] = {
            "active": count > 0,
            "count": count,
            "label": info["label"],
            "active_phrases": active_phrases[:5],
        }

    active_stages = sum(1 for s in funnel_stages.values() if s["active"])

    desire_density = funnel_stages["desire"]["count"] / total_stt
    action_density = funnel_stages["action"]["count"] / total_stt

    conv_count = sum(1 for e in live_data if e.get("conversion_hits"))
    conv_density = conv_count / max(len(live_data), 1) if live_data else 0

    prod_density = len(prod_timeline) / total_stt
    prod_score = min(prod_density * 40, 30)
    funnel_score = min(active_stages * 8, 30)
    urgency_score = min(desire_density * 60, 20)
    action_score = min(action_density * 50, 20)
    conv_score = min(conv_density * 300, 10)

    demo_quality = 0
    quality_score = 0
    if triage_data and prod_timeline:
        demo_times = [t[0] for t in prod_timeline if t[0]]
        demo_brightness = []
        demo_sat = []
        for t in triage_data:
            ts = t.get("timestamp", 0)
            for pt in demo_times:
                if pt and abs(ts - pt) < 60:
                    demo_brightness.append(t.get("brightness", 0))
                    demo_sat.append(t.get("food_saturation", 0))
                    break
        if demo_brightness:
            avg_b = sum(demo_brightness) / len(demo_brightness)
            avg_s = sum(demo_sat) / len(demo_sat)
            demo_quality = min(avg_b / 120 * 60 + avg_s / 60 * 40, 100)
            quality_score = min(demo_quality / 5, 10)

    # ── 产品展示持续时长统计 ──
    product_display_times = {}
    sorted_prod = sorted(prod_timeline, key=lambda x: x[0]) if prod_timeline else []
    for i, (ts, kw, cat) in enumerate(sorted_prod):
        key = f"{cat}:{kw}"
        if key not in product_display_times:
            product_display_times[key] = {"first_seen": ts, "last_seen": ts, "mentions": 0, "category": cat}
        product_display_times[key]["last_seen"] = ts
        product_display_times[key]["mentions"] += 1

    # 展示时长 (秒) + 优先级排序
    display_durations = []
    for key, info in product_display_times.items():
        duration = info["last_seen"] - info["first_seen"]
        if duration > 0:
            display_durations.append({
                "product": key,
                "category": info["category"],
                "duration_sec": int(duration),
                "mentions": info["mentions"],
            })
    display_durations.sort(key=lambda x: x["duration_sec"], reverse=True)
    top_products = display_durations[:5]

    total_sales_score = round(prod_score + funnel_score + urgency_score + action_score + conv_score + quality_score)
    total_sales_score = min(total_sales_score, 100)

    return {
        "score": total_sales_score,
        "product_mentions": prod_mentions.most_common(10),
        "product_count": len(prod_timeline),
        "product_density": round(prod_density, 3),
        "funnel": funnel_stages,
        "funnel_completeness": active_stages,
        "funnel_total": 4,
        "urgency_density": round(desire_density, 3),
        "action_density": round(action_density, 3),
        "demo_quality": round(demo_quality, 1) if demo_quality else 0,
        "conv_density": round(conv_density, 3),
        "conv_count": conv_count,
        # 新增
        "display_durations": top_products,
        "product_count_detail": len(product_display_times),
        "stage_conversion_estimate": {
            "attention_to_interest": round(
                funnel_stages["interest"]["count"] / max(funnel_stages["attention"]["count"], 1), 2
            ) if funnel_stages["attention"]["count"] > 0 else 0,
            "interest_to_desire": round(
                funnel_stages["desire"]["count"] / max(funnel_stages["interest"]["count"], 1), 2
            ) if funnel_stages["interest"]["count"] > 0 else 0,
            "desire_to_action": round(
                funnel_stages["action"]["count"] / max(funnel_stages["desire"]["count"], 1), 2
            ) if funnel_stages["desire"]["count"] > 0 else 0,
            "overall_conversion_rate": round(
                conv_count / max(len(live_data), 1), 3
            ) if live_data else 0,
        },
    }


def _generate_recommendations(eng, vis, spk, auth, sce, duration_min, pop=None, traffic=None, pf=None, comp=None, sales=None, host_type=None):
    """Actionable improvement tips based on analysis gaps"""
    recs = []

    # ── Speaking ──
    if spk.get("stt_count", 0) > 0:
        if spk["speech_rate"] > 2.0:
            recs.append({"dim": "speaking", "priority": "high",
                         "title": "语速偏快", "detail": f"当前{spk['speech_rate']}字/秒, 建议降至1.0-1.8字/秒范围",
                         "action": "放慢语速, 每句话后稍作停顿"})
        elif spk["speech_rate"] < 0.5:
            recs.append({"dim": "speaking", "priority": "high",
                         "title": "语速偏慢", "detail": f"当前{spk['speech_rate']}字/秒",
                         "action": "增加说话量, 准备话术脚本"})
        if spk["question_ratio"] < 0.1 and spk["stt_count"] >= 2:
            recs.append({"dim": "speaking", "priority": "medium",
                         "title": "缺少互动提问", "detail": f"提问占比{spk['question_ratio']:.0%}",
                         "action": "每分钟问1-2个问题引导弹幕, 如'大家觉得怎么样?'"})
        if spk["cta_density"] < 0.05:
            recs.append({"dim": "speaking", "priority": "high",
                         "title": "缺少转化引导", "detail": "未检测到CTA话术",
                         "action": "每3-5分钟插入转化话术: '点关注'、'小黄车下单'、'分享直播间'"})
        if spk["emotion_count"] < 1:
            recs.append({"dim": "speaking", "priority": "low",
                         "title": "情绪表达不足", "detail": "缺少感叹/夸张表达",
                         "action": "增加'太'、'超级'、'绝了'等情绪词提升感染力"})
        if spk["pause_avg"] > 15:
            recs.append({"dim": "speaking", "priority": "medium",
                         "title": "停顿过长", "detail": f"平均停顿{spk['pause_avg']}秒",
                         "action": "减少沉默间隙, 准备过渡话术填充"})

    # ── Visual ──
    if vis["score"] < 60:
        if vis["brightness_avg"] < 50:
            recs.append({"dim": "visual", "priority": "high",
                         "title": "画面过暗", "detail": f"亮度{vis['brightness_avg']}/120",
                         "action": "增加补光灯或调整摄像头位置"})
        if vis["food_sat_avg"] < 30:
            recs.append({"dim": "visual", "priority": "medium",
                         "title": "食物色彩不鲜明", "detail": f"饱和度{vis['food_sat_avg']}/60",
                         "action": "调整拍摄角度让食物在光源下, 使用鲜艳食材"})
    if vis["warm_ratio_avg"] < 0.15 or vis["warm_ratio_avg"] > 0.30:
        recs.append({"dim": "visual", "priority": "low",
                     "title": "色调偏" + ("冷" if vis["warm_ratio_avg"] < 0.15 else "暖"),
                     "detail": f"暖色比{vis['warm_ratio_avg']:.2f}",
                     "action": "调整白平衡或背景色调"})

    # ── Engagement ──
    if eng["chat_volume"] > 0:
        if eng["keyword_density"] < 0.1 and duration_min > 10:
            recs.append({"dim": "engagement", "priority": "medium",
                         "title": "关键词密度低", "detail": f"密度{eng['keyword_density']:.2f}",
                         "action": "强调核心卖点词汇, 让弹幕自然带出关键词"})
        if eng["conversion_rate"] < 0.01 and eng["chat_volume"] > 20:
            recs.append({"dim": "engagement", "priority": "high",
                         "title": "转化率低", "detail": f"转化率{eng['conversion_rate']:.1%}",
                         "action": "加强促销话术, 限时优惠/限量抢购制造紧迫感"})

    # ── Authenticity ──
    if auth["diff_avg"] < -5:
        recs.append({"dim": "authenticity", "priority": "medium",
                     "title": "画面显摆拍感", "detail": f"真实感偏低({auth['authentic_avg']:.0f} vs 摆拍{auth['staged_avg']:.0f})",
                     "action": "增加不完美元素: 厨房烟火气, 自然背景音"})

    # ── Scene ──
    if sce.get("distribution"):
        scene_keys = list(sce["distribution"].keys())
        if len(scene_keys) <= 1 and duration_min > 20:
            recs.append({"dim": "scene", "priority": "low",
                         "title": "场景单一", "detail": f"仅{sce['scene_label']}",
                         "action": "尝试切换场景: 厨房→餐桌→户外, 增加新鲜感"})

    # ── Popularity ──
    if pop and duration_min > 5:
        if pop["trend"] == "declining":
            recs.append({"dim": "popularity", "priority": "high",
                         "title": "人气下滑", "detail": f"后半段活跃度比前半段下降{(1-pop['second_half']/max(pop['first_half'],1))*100:.0f}%",
                         "action": "增加互动环节: 抽奖/问答/限时优惠拉回人气"})
        if pop["chat_velocity"] < 2 and duration_min > 10:
            recs.append({"dim": "popularity", "priority": "high",
                         "title": "弹幕活跃度低", "detail": f"平均每分钟{pop['chat_velocity']}条弹幕",
                         "action": "主动引导弹幕: '新进来的朋友打声招呼' '扣1让我看到你们'"})
        if pop["engagement_loops"] == 0 and pop.get("score", 0) < 50:
            recs.append({"dim": "popularity", "priority": "medium",
                         "title": "互动循环未形成", "detail": "未检测到提问→回应模式",
                         "action": "设计互动话术: 提问后点名回应弹幕, 形成循环"})
        if pop["trend"] == "stable" and pop["chat_velocity"] < 5:
            recs.append({"dim": "popularity", "priority": "low",
                         "title": "人气增长缓慢", "detail": "弹幕量稳定但未增长",
                         "action": "增加分享引导: '转发直播间到群' '@三位好友来看'"})

    # ── Compliance ──
    if comp and comp["violations"]:
        if comp["risk_level"] in ("critical", "warning"):
            recs.append({"dim": "compliance", "priority": "high",
                         "title": f"限流风险{comp['traffic_risk_pct']}%", "detail": comp["summary"],
                         "action": f"立即删除违规词: {', '.join(comp['found_words'][:5])}"})
        for v in comp["violations"][:3]:
            recs.append({"dim": "compliance", "priority": "medium" if v["severity"] == "high" else "low",
                         "title": f"违规词: {v['word']}", "detail": f"{v['category']}({v['severity']})权重{v['weight']}",
                         "action": f"替换{v['word']}为合规表达"})

    # ── Traffic ──
    if traffic and traffic.get("suggestion"):
        if traffic["spike_count"] == 0 and duration_min > 15:
            recs.append({"dim": "traffic", "priority": "medium",
                         "title": "无流量脉冲", "detail": "弹幕量平稳无爆发点",
                         "action": traffic["suggestion"]})
        elif traffic["spike_count"] >= 2:
            recs.append({"dim": "traffic", "priority": "low",
                         "title": f"投流窗口: {traffic['best_ad_window']}", "detail": f"检测到{traffic['spike_count']}次流量脉冲",
                         "action": traffic["suggestion"]})
        elif traffic["organic_ratio"] > 0.8 and traffic["spike_count"] > 0:
            recs.append({"dim": "traffic", "priority": "low",
                         "title": "自然流量为主", "detail": f"自然流量占比{traffic['organic_ratio']:.0%}",
                         "action": "自然流量健康, 可适量投流放大效果"})

    # ── Platform ──
    if pf:
        if pf["fit_score"] < 50:
            recs.append({"dim": "platform", "priority": "high",
                         "title": f"不匹配{pf['platform']}算法", "detail": f"算法匹配度{pf['fit_score']}分",
                         "action": f"参考{pf['platform']}推荐指标: {', '.join(pf['factors'][:3])}"})
        for ev in pf.get("evals", []):
            if "待优化" in ev["score"]:
                recs.append({"dim": "platform", "priority": "medium",
                             "title": f"{ev['factor']}待优化", "detail": f"当前{ev['value']}",
                             "action": ev["tip"]})

    # ── Host type focus recommendation ──
    if host_type:
        ht_info = HOST_TYPE_TIPS.get(host_type, {})
        dim = ht_info.get("dim", "")
        focus = ht_info.get("focus", "")
        if dim and focus:
            dim_score = {"visual": vis["score"], "authenticity": auth["score"],
                         "speaking": spk["score"], "popularity": (pop or {}).get("score", 0),
                         "engagement": eng["score"]}.get(dim, 50)
            if dim_score < 60:
                recs.append({"dim": "host_type", "priority": "high",
                             "title": f"{ht_info.get('focus','')}需加强", "detail": f"关键维度{dim}仅{dim_score}分",
                             "action": f"作为{ht_info.get('focus','')}型主播, 重点提升{dim}维度表现"})
            else:
                recs.append({"dim": "host_type", "priority": "low",
                             "title": f"{ht_info.get('focus','')}表现良好", "detail": f"{dim}维度{dim_score}分",
                             "action": "保持当前风格, 优化其他维度"})

    # ── Sales ──
    if sales:
        if sales["score"] < 40:
            recs.append({"dim": "sales", "priority": "high",
                         "title": "带货能力不足", "detail": f"带货评分{sales['score']}分",
                         "action": "增加产品介绍频次, 每5分钟提及1-2款产品"})
        if sales["funnel_completeness"] < 3:
            missing = [info["label"] for stage, info in sales["funnel"].items() if not info["active"]]
            if missing:
                recs.append({"dim": "sales", "priority": "high",
                             "title": "销售漏斗不完整", "detail": f"缺失阶段: {'/'.join(missing)}",
                             "action": f"增加{missing[0]}话术引导观众"})
        if sales["action_density"] < 0.05:
            recs.append({"dim": "sales", "priority": "high",
                         "title": "缺少下单引导", "detail": f"行动号召密度{sales['action_density']:.1%}",
                         "action": "每3分钟引导一次: '点小黄车' '拍一号链接'"})
        if sales["urgency_density"] < 0.03:
            recs.append({"dim": "sales", "priority": "medium",
                         "title": "缺少促销紧迫感", "detail": f"促销话术密度{sales['urgency_density']:.1%}",
                         "action": "使用限时限量话术: '仅剩最后10份' '马上涨价'"})
        if sales["product_density"] < 0.2:
            recs.append({"dim": "sales", "priority": "medium",
                         "title": "产品提及不足", "detail": f"每段语音提及{sales['product_density']:.1f}次",
                         "action": "多叫产品名字, 介绍特色和用途"})
        if sales["demo_quality"] < 30 and sales["product_count"] > 0:
            recs.append({"dim": "sales", "priority": "medium",
                         "title": "产品展示画面不佳", "detail": f"展示区质量分{sales['demo_quality']:.0f}",
                         "action": "展示产品时调整光线和角度"})

    recs.sort(key=lambda r: {"high": 0, "medium": 1, "low": 2}[r["priority"]])
    return recs[:12]


def _generate_summary(overall, eng, vis, spk, auth, duration, sales=None, host_type=None):
    """人话总结 v2: 含语音深度"""
    dur_min = duration // 60
    parts = []

    if overall >= 80:
        parts.append("表现优秀")
    elif overall >= 60:
        parts.append("表现良好")
    elif overall >= 40:
        parts.append("表现一般")
    else:
        parts.append("数据不足")

    parts.append(f"直播 {dur_min} 分钟")

    if eng["chat_volume"] > 0:
        if eng["keyword_density"] > 0.3:
            parts.append("观众互动活跃")
        elif eng["conversion_count"] > 0:
            parts.append("有转化意向")
        else:
            parts.append("互动一般")

    if vis["score"] > 60:
        parts.append("画面质量较好")
    else:
        parts.append("画面偏暗可优化")

    if spk.get("stt_count", 0) > 0:
        line = f"语音 {spk['stt_count']}条"
        if spk.get("question_count", 0) > 0:
            line += f" 提问{spk['question_count']}次"
        if spk.get("cta_count", 0) > 0:
            line += f" CTA{spk['cta_count']}次"
        if spk.get("emotion_count", 0) > 0:
            line += f" 情绪{spk['emotion_count']}次"
        parts.append(line)
    else:
        parts.append("无语音数据")

    if sales and sales.get("score", 0) > 0:
        if sales["score"] >= 70:
            parts.append("带货力强")
        elif sales["score"] >= 40:
            parts.append("带货一般")
        else:
            parts.append("带货需提升")
        if sales.get("funnel_completeness", 0) >= 3:
            parts.append(f"漏斗{sales['funnel_completeness']}/4")

    if host_type:
        ht_info = HOST_TYPE_TIPS.get(host_type, {})
        if ht_info:
            parts.append(f"{ht_info.get('focus','')[:8]}")

    return " · ".join(parts)


if __name__ == "__main__":
    # Quick test
    BASE = Path("E:/MyCodeProjects")
    SUR_DIR = BASE / "04-宝妈直播诊断系统" / "苏苏在浙里"

    def tail_jsonl(path, max_lines=500):
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        results = []
        for line in lines[-max_lines:]:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except:
                    pass
        return results

    live = tail_jsonl(SUR_DIR / "live_data_susu.jsonl")
    triage = tail_jsonl(SUR_DIR / "triage_log_susu.jsonl")
    stt = tail_jsonl(SUR_DIR / "stt.jsonl")

    r = analyze("苏苏在浙里", live, triage, stt)
    print(f"综合评分: {r['overall_score']}")
    print(f"总结: {r['summary']}")
    for dim, data in r['dimensions'].items():
        print(f"  {dim}: {data['score']}")
    print(f"时刻: {len(r['moments'])} 个")
    print(f"话题: {r['topics'][:5]}")
