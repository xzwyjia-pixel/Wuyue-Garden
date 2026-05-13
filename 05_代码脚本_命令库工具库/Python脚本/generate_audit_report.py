# -*- coding: utf-8 -*-
"""
generate audit report for any target — diagnostic output

Usage:
    python generate_audit_report.py --target 凡姐走乡村
    python generate_audit_report.py --target 小桃
"""
import json, shutil, sys, re, ast
from collections import Counter
from pathlib import Path

ROOT = Path("E:/MyCodeProjects")
INSTRUCTIONS = ROOT / "03-生产素材" / "instructions.md"
_CASE_ROOTS = {
    "fanjie": ROOT / "04-凡姐案例",
    "xiaotao": ROOT / "05-小桃案例",
}

# ── Parse helpers ──────────────────────────────────────

def parse_args():
    target = None
    if "--target" in sys.argv:
        idx = sys.argv.index("--target")
        if idx + 1 < len(sys.argv):
            target = sys.argv[idx + 1]
    return target

def load_dict(name):
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    m = re.search(rf"{name}\s*=\s*(\{{.+?\n\}})", text, re.DOTALL)
    return ast.literal_eval(m.group(1)) if m else {}

def get_profile(target):
    profiles = load_dict("Live_Profiles")
    for key, val in profiles.items():
        if target.lower() in key.lower() or target.lower() in val.get("display", "").lower():
            val["_slug"] = key
            return val
    return None

def gap(val, bench):
    if not bench:
        return "N/A"
    return f"{(val - bench) / bench * 100:+.1f}%"

# ── Diagnostic generators ──────────────────────────────

def diagnose_warm(warm_ratio, peak):
    if warm_ratio < 0.05:
        return ("暖色严重不足", f"当前{warm_ratio:.0%}, 巅峰标杆要求{peak:.0%}, 差距{gap(warm_ratio, peak)}. "
                "建议在食物展示侧增加3200K暖色补光灯, 将暖色占比提升至15%以上以触发食欲诱导")
    if warm_ratio < 0.15:
        return ("暖色偏低", f"当前{warm_ratio:.0%}, 距巅峰{peak:.0%}仍有{gap(warm_ratio, peak)}差距. "
                "建议逐步增加暖光源, 优先照亮食物区域")
    return ("暖色达标", f"当前{warm_ratio:.0%}, 接近巅峰标杆{peak:.0%}")

def diagnose_brightness(b, peak):
    if b > 200:
        return ("过曝风险", f"当前亮度{b:.0f}, 巅峰标杆{peak:.0f}. "
                "建议拉帘降低环境光30%, 将聚光灯集中于产品展示区域")
    if b > 160:
        return ("亮度偏高", f"当前亮度{b:.0f}, 巅峰标杆{peak:.0f}. "
                "建议适当降低环境光, 提升对比度使画面更有质感")
    if b < 100:
        return ("亮度不足", f"当前亮度{b:.0f}, 巅峰标杆{peak:.0f}. "
                "建议增加主光源亮度或调整摄像头曝光补偿")
    return ("亮度适宜", f"当前亮度{b:.0f}, 接近巅峰标杆{peak:.0f}")

def diagnose_detail(d, peak):
    if d < 50:
        return ("细节模糊", f"当前细节得分{d:.0f}, 巅峰标杆{peak:.0f}, 差距{gap(d, peak)}. "
                "建议检查摄像头焦距, 手动对焦至产品标签区域; 增加中心区域局部照明提高纹理可辨度")
    if d < 65:
        return ("细节一般", f"当前细节得分{d:.0f}, 距巅峰{peak:.0f}差距{gap(d, peak)}. "
                "建议在手持产品展示时保持摄像头距离30-40cm以获得最佳清晰度")
    return ("细节清晰", f"当前细节得分{d:.0f}, 接近巅峰标杆{peak:.0f}")

def diagnose_sat(sat, peak):
    if sat < 20:
        return ("食物苍白", f"当前食物饱和度{sat:.0f}, 巅峰标杆{peak:.0f}, 差距{gap(sat, peak)}. "
                "建议使用红色番茄/辣椒或橙色调料碗等色彩鲜明食材; 暖色餐具可提升视觉冲击力50%+")
    if sat < 45:
        return ("饱和度偏低", f"当前食物饱和度{sat:.0f}, 距巅峰{peak:.0f}差距{gap(sat, peak)}. "
                "建议在食物区增加深绿色蔬菜或红色食材点缀, 提升整体色彩层次")
    return ("饱和度达标", f"当前食物饱和度{sat:.0f}, 接近巅峰标杆{peak:.0f}")

def diagnose_entropy(ce, peak):
    if ce < 2.5:
        return ("色彩贫乏", f"当前色彩熵{ce:.1f}, 巅峰标杆{peak:.1f}. "
                "画面色彩单一偏冷, 建议增加食材种类和道具颜色层次, 或切换不同色系的背景布")
    if ce < 3.5:
        return ("色彩一般", f"当前色彩熵{ce:.1f}, 距巅峰{peak:.1f}差距{gap(ce, peak)}. "
                "建议在画面中加入暖色道具或食物, 丰富HSV色相分布")
    return ("色彩丰富", f"当前色彩熵{ce:.1f}, 接近巅峰标杆{peak:.1f}")

def diagnose_interaction(total_live, conversion_count, conv_hit_count):
    if conv_hit_count >= 5:
        return ("高转化互动", f"检测到{conv_hit_count}次转化意向命中, 观众购买意愿强烈. "
                "建议在命中时段立即口播购物车引导, 将询单转化为订单")
    if conv_hit_count >= 1:
        return ("有转化意向", f"检测到{conv_hit_count}次转化意向命中. "
                "建议增加口播'点击下方小黄车查看详情'的频率, 缩短购买决策路径")
    return ("转化待激活", "当前零转化意向命中. 建议主动设置价格锚点: '外面卖XX, 今天我这里只要XX', "
            "或弹出限时优惠券刺激询单")

# ── Main ───────────────────────────────────────────────

def main():
    target_name = parse_args()
    if not target_name:
        print("Usage: python generate_audit_report.py --target <名称>")
        sys.exit(1)

    profile = get_profile(target_name)
    if not profile:
        print(f"[错误] 未找到目标 '{target_name}'")
        sys.exit(1)

    slug = profile["_slug"]
    alias = profile.get("_alias", slug.capitalize())
    display = profile.get("display", slug)
    target_bench = profile.get("benchmark", {})
    peak = load_dict("PEAK_BENCHMARK")

    case_root = _CASE_ROOTS.get(alias.lower(), ROOT)
    TRIAGE = case_root / f"triage_log_{alias.lower()}.jsonl"
    LIVE = case_root / f"live_data_{alias.lower()}.jsonl"
    ASSETS = ROOT / "case_assets" / alias
    REPORT = case_root / f"Audit_Report_{alias}.md"
    ASSETS.mkdir(parents=True, exist_ok=True)

    # ── 1. Load triage ──
    triage = []
    if TRIAGE.exists():
        with open(TRIAGE, encoding="utf-8") as f:
            for line in f:
                triage.append(json.loads(line))

    valid = [t for t in triage if t.get("brightness", 0) < 255]
    invalid = [t for t in triage if t.get("brightness", 0) >= 255]
    avg_auth = sum(t["score_authentic"] for t in valid) / len(valid) if valid else 0
    avg_diff = sum(t["diff"] for t in valid) / len(valid) if valid else 0

    fluctuations = []
    for i in range(1, len(triage)):
        delta = abs(triage[i]["diff"] - triage[i-1]["diff"])
        if delta >= 15:
            fluctuations.append((
                i, triage[i-1]["diff"], triage[i]["diff"], delta,
                triage[i].get("image", ""), triage[i].get("brightness", 0)
            ))

    # ── 2. Keywords & emoji ──
    keywords = profile.get("keywords", [])
    hits = Counter()
    total_live = 0
    emoji_total = 0
    conversion_records = []
    if LIVE.exists():
        with open(LIVE, encoding="utf-8") as f:
            for line in f:
                total_live += 1
                d = json.loads(line)
                full = "".join(d.get("texts", []))
                for kw in keywords:
                    if kw in full:
                        hits[kw] += full.count(kw)
                emoji_total += d.get("emoji_count", 0)
                if d.get("conversion_hits"):
                    conversion_records.append(d)

    # ── 2b. Dual-platform keyword stats ──
    dy_counter = Counter()
    wch_counter = Counter()
    dy_keywords = profile.get("dy_keywords", [])
    wch_keywords = profile.get("wch_keywords", [])
    if LIVE.exists():
        with open(LIVE, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                full = "".join(d.get("texts", []))
                for kw in dy_keywords:
                    if kw in full:
                        dy_counter[kw] += full.count(kw)
                for kw in wch_keywords:
                    if kw in full:
                        wch_counter[kw] += full.count(kw)

    # ── 3. Negatives ──
    negatives = {"咸了": 0, "油少": 0, "太咸": 0, "不好吃": 0, "太油": 0, "贵": 0}
    if LIVE.exists():
        with open(LIVE, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                full = "".join(d.get("texts", []))
                for kw in negatives:
                    if kw in full:
                        negatives[kw] += 1

    # ── 4. Averages ──
    if valid:
        avg = {k: sum(t.get(k, 0) for t in valid) / len(valid)
               for k in ["brightness", "contrast", "warm_ratio", "detail", "color_entropy"]}
        avg["product_detail"] = sum(t.get("product_detail", 0) for t in valid) / len(valid)
        avg["food_saturation"] = sum(t.get("food_saturation", 0) for t in valid) / len(valid)
    else:
        avg = {}

    warm_r = avg.get("warm_ratio", 0) if avg else 0
    sat_avg = avg.get("food_saturation", 0) if avg else 0

    # ── 5. Diagnostics ──
    pk = peak
    diag_results = {}
    if avg:
        diag_results = {
            "brightness": diagnose_brightness(avg.get("brightness", 0), pk.get("brightness", 145)),
            "warm": diagnose_warm(avg.get("warm_ratio", 0), pk.get("warm_ratio", 0.30)),
            "detail": diagnose_detail(avg.get("detail", 0), pk.get("detail", 80)),
            "sat": diagnose_sat(avg.get("food_saturation", 0), pk.get("food_saturation", 65)),
            "entropy": diagnose_entropy(avg.get("color_entropy", 0), pk.get("color_entropy", 4.2)),
            "interaction": diagnose_interaction(total_live, len(conversion_records), len(conversion_records)),
        }

    # ── 6. Suggestions from diagnostics ──
    suggestions = []
    for key, (title, msg) in diag_results.items():
        if "达标" not in title and "适宜" not in title and "清晰" not in title and "丰富" not in title and "高转化" not in title:
            suggestions.append(f"{title}: {msg}")
    suggestions.append("固定窗口: find_and_pin() 置顶防坐标偏移")

    # ── Write report ──
    W = []
    a = W.append

    a(f"# 直播间人设审计诊断报告 - {display}")
    a("")
    a(f"> 生成时间: 2026-05-10 | 窗口: 约{total_live * 30 // 60}min 直播")
    a(f"> 巅峰标杆: 综合顶尖直播间")
    a("")
    a("---")
    a("")
    a("## 一、诊断总览")
    a("")
    a(f"- 有效Triage记录: {len(valid)} | 过滤无效: {len(invalid)}")
    a(f"- 平均真实感评分: {avg_auth:.0f}/100 | 平均偏差值: {avg_diff:+.0f}")
    a(f"- 总OCR轮次: {total_live} | 表情符号总数: {emoji_total}")
    a(f"- 转化意向命中: {len(conversion_records)} 次 | 关键词总命中: {sum(hits.values())}")
    a("")
    a("### 关键诊断")
    a("")
    for key, (title, msg) in diag_results.items():
        a(f"- **{title}**: {msg}")
    a("")
    a("### 与巅峰标杆差距")
    a("")
    a("| 指标 | 当前值 | 巅峰标杆 | 差距 |")
    a("|------|--------|----------|------|")
    if avg:
        for k in ["brightness", "warm_ratio", "detail", "food_saturation", "color_entropy"]:
            pk_v = pk.get(k, 0)
            av = avg.get(k, 0)
            bar = "█" * max(0, min(int(av / max(pk_v, 1) * 20), 20))
            a(f"| {k} | {av:.2f} | {pk_v:.2f} | {gap(av, pk_v)} {bar} |")
    a("")
    a("---")
    a("")
    a("## 二、视觉质量分析")
    a("")
    # Red list: frames where product_detail exceeds peak
    peak_pd = pk.get("product_detail", 85)
    best_frames = [t for t in valid if t.get("product_detail", 0) >= peak_pd]
    a("### 高价值时刻 (product_detail >= {:.0f})".format(peak_pd))
    a("")
    if best_frames:
        for t in best_frames:
            a(f"- pd={t.get('product_detail','?')} 亮度={t['brightness']} 暖色={t['warm_ratio']:.0%} sat={t.get('food_saturation','?')}")
            a(f"  - img: {t.get('image','?')}")
    else:
        a("(当前无帧达到巅峰标杆产品细节标准)")
    a("")
    a("### 需优化帧")
    a("")
    low_frames = [t for t in valid if t.get("product_detail", 0) < 40]
    for t in low_frames:
        a(f"- pd={t.get('product_detail','?')} 亮度={t['brightness']} 原因: 细节不足/模糊")
        a(f"  - img: {t.get('image','?')}")
    a("")
    a("---")
    a("")
    a("## 三、评论区生态")
    a("")
    a("### 热词排行")
    a("")
    if hits:
        a("| 关键词 | 频次 |")
        a("|--------|------|")
        for kw, c in hits.most_common(10):
            bar = "█" * min(c, 25)
            a(f"| {kw} | {c} {bar} |")
    else:
        a("(无关键词命中)")
    a("")
    a("### 转化意向时序")
    a("")
    if conversion_records:
        for r in conversion_records:
            a(f"- {r['time']} -> {', '.join(r['conversion_hits'])}")
    else:
        a("(无转化意向记录)")
    a("")
    a("### 负面舆情")
    a("")
    warns = [f"- {k} = {v}次" for k, v in negatives.items() if v > 0]
    if warns:
        for w in warns:
            a(w)
    else:
        a("- 无负面监测")
    a("")
    a("---")
    a("")
    a("## 四、双端协同度评估")
    a("")
    a("### 抖音端热词")
    a("")
    dy_total = sum(dy_counter.values())
    if dy_total:
        a("| 关键词 | 频次 |")
        a("|--------|------|")
        for kw, c in dy_counter.most_common(8):
            bar = "█" * min(c, 25)
            a(f"| {kw} | {c} {bar} |")
    else:
        a("(无抖音端关键词命中)")
    a("")
    a("### 视频号端热词")
    a("")
    wch_total = sum(wch_counter.values())
    if wch_total:
        a("| 关键词 | 频次 |")
        a("|--------|------|")
        for kw, c in wch_counter.most_common(8):
            bar = "█" * min(c, 25)
            a(f"| {kw} | {c} {bar} |")
    else:
        a("(无视频号端关键词命中)")
    a("")
    # Diagnostic
    if dy_total > wch_total * 2:
        a("- **诊断**: 抖音端侧重价格询问与购买转化, 视频号端侧重人设互动。建议在抖音口播时强化优惠力度话术, 在视频号增加人设故事分享。")
    elif wch_total > dy_total * 2:
        a("- **诊断**: 视频号端侧重人设互动与品质认同, 抖音端侧重价格询问。建议在视频号保持烟火气人设, 在抖音增加限时折扣话术。")
    else:
        a("- **诊断**: 双端关键词分布较均衡, 内容对两个平台均有适配性。可同步更新但注意各平台话术微调。")
    # Visual cross-reference
    if avg:
        sat_ok = abs(avg.get("food_saturation", 0) - 55) <= 10
        warm_ok = abs(avg.get("warm_ratio", 0) - 0.18) <= 0.05
        if sat_ok and warm_ok:
            a("- **视觉双端适配**: 当前饱和度和暖色均在双端公约数范围内, 视觉效果在两个平台均表现良好。")
        elif sat_ok:
            a("- **视觉双端适配**: 饱和度达标, 但暖色{}偏离公约数(目标18%±5%), 建议微调暖光源占比。".format(
                "偏低" if avg.get("warm_ratio", 0) < 0.13 else "偏高"))
        elif warm_ok:
            a("- **视觉双端适配**: 暖色达标, 但饱和度{}偏离公约数(目标55±10), 建议调整食物色彩搭配。".format(
                "偏低" if avg.get("food_saturation", 0) < 45 else "偏高"))
        else:
            a("- **视觉双端适配**: 饱和度和暖色均偏离双端公约数, 建议同时调整暖光源和食物色彩搭配以兼顾双端视觉体验。")
    a("")
    a("---")
    a("")
    a("## 五、偏差波动分析")
    a("")
    for i, pd, cd, dlt, img, b in fluctuations:
        a(f"### T{i} -> T{i+1}: diff {pd:+d} -> {cd:+d} (δ={dlt:+d})")
        if b >= 255:
            a(f"- 原因: 纯白画面 @ brightness={b:.0f}")
        elif dlt >= 40:
            a(f"- 原因: 大幅场景切换 @ brightness={b:.0f}")
        elif cd > pd:
            a(f"- 原因: 画面改善 @ brightness={b:.0f}")
        else:
            a(f"- 原因: 画面下降 @ brightness={b:.0f}")
        a(f"- img: {img}")
        a("")
    a("")
    a("---")
    a("")
    a("## 六、改进建议")
    a("")
    for i, sug in enumerate(suggestions[:8], 1):
        a(f"{i}. {sug}")
    a("")
    a("---")
    a("")
    a("*AI生成 by Triage Engine | 诊断模型 v2.0*")

    REPORT.write_text("\n".join(W), encoding="utf-8")
    print(f"Report written: {REPORT}")

    # Move assets
    moved = 0
    for f in ROOT.glob("debug_crop.*"):
        shutil.move(str(f), str(ASSETS / f.name))
        moved += 1
    for _, _, _, _, img_path, _ in fluctuations:
        p = ROOT / img_path
        if p.exists():
            shutil.move(str(p), str(ASSETS / p.name))
            moved += 1
    for t in best_frames + low_frames:
        ip = t.get("image", "")
        if ip:
            p = ROOT / ip
            if p.exists():
                shutil.move(str(p), str(ASSETS / p.name))
                moved += 1

    print(f"Moved {moved} assets to {ASSETS}")
    print(f": {display} 诊断报告已生成: {REPORT}")

if __name__ == "__main__":
    main()
