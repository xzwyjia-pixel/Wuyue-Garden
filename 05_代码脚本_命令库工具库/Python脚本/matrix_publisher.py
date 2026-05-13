#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 矩阵内容发布器
==========================================
读取 pipeline_state 当日审计结果 + user_pains → 为 3 平台生成 2 种产出：

  每日文案（douyin + shipinhao）：短平快，今日关键判断 + 避坑 + 选题方向
  每周报模板（gongzhonghao）：周度汇总，风险趋势 + 用户痛点聚类 + 下周策略

用法：
  python matrix_publisher.py                       # 生成每日文案（douyin + shipinhao）
  python matrix_publisher.py --weekly              # 生成每周报模板（gongzhonghao）
  python matrix_publisher.py --all                 # 同时生成每日 + 每周
  python matrix_publisher.py --publish             # 生成 + 标记已发布
"""

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR / "data"
_NOTES_DIR = _BASE_DIR / "notes"
_STATE_PATH = _DATA_DIR / "pipeline_state.json"
_PAINS_PATH = _DATA_DIR / "user_pains.json"

if __name__ == "__main__":
    import sys
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


# ── 数据源 ──

def _load_state() -> dict:
    if _STATE_PATH.exists():
        return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    return {}


def _load_pains() -> list:
    if _PAINS_PATH.exists():
        return json.loads(_PAINS_PATH.read_text(encoding="utf-8")).get("pains", [])
    return []


def _extract_daily_metrics(state: dict) -> dict:
    steps = state.get("steps", [])
    refine_results = state.get("refine_results", [])
    di = state.get("deep_insight", {})
    trend = state.get("trend_collection", {})

    risk_found = 0
    total_high = 0
    top_categories = Counter()
    for r in refine_results:
        pre = r.get("pre_audit", {})
        pts = pre.get("risk_points", [])
        risk_found += len(pts)
        for p in pts:
            if p.get("level") == "HIGH":
                total_high += 1
            if p.get("category"):
                top_categories[p["category"]] += 1

    ci_list = di.get("counter_intuitive", [])
    pi = di.get("platform_intent", {})

    return {
        "total_cases": len(refine_results),
        "risk_found": risk_found,
        "total_high": total_high,
        "safe_passed": sum(1 for r in refine_results if r.get("verified_safe")),
        "duration_s": sum(s.get("duration_s", 0) for s in steps),
        "status": state.get("status", "none"),
        "pipeline_id": state.get("pipeline_id", ""),
        "top_risk_categories": top_categories.most_common(3),
        "platform_intent_title": (pi or {}).get("title", ""),
        "platform_intent_detail": (pi or {}).get("detail", ""),
        "counter_intuitive": ci_list,
        "trend_keywords": trend.get("keywords", []),
        "trend_incentives": trend.get("total_incentives", 0),
    }


# ── 每日文案 · 抖音 （短平快 · 钩子+选题方向）──

def _daily_douyin(m: dict, pains: list) -> str:
    pain = pains[0].get("text", "合规到底怎么做？") if pains else "合规到底怎么做？"
    cate_str = "、".join(c for c, _ in m["top_risk_categories"]) or "合规"
    trend_kw = "、".join(m["trend_keywords"][:3]) if m["trend_keywords"] else "内容创作"

    lines = [
        "---",
        "平台: 抖音",
        "账号: 规则情报局",
        "类型: 每日文案 · 选题方向",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "---",
        "",
        f"🔥 \"{pain}\"",
        "",
        f"今日重点关注：{cate_str}",
        "",
        "**今日金句**",
        f"> {m['platform_intent_title'] or '合规不是束缚，是竞争力'}",
        "",
        "**建议发帖方向**",
    ]
    for i, kw in enumerate(m["trend_keywords"][:4], 1):
        # 匹配用户痛点
        matched = [p["text"] for p in pains if p.get("source") == kw and p.get("score", 0) >= 1][:2]
        pain_hint = f" → 用户问: {' | '.join(matched[:2])}" if matched else ""
        lines.append(f"  {i}. **{kw}**{pain_hint}")
    lines.append("")

    if m["counter_intuitive"]:
        ci = m["counter_intuitive"][0]
        lines.append("**⚠️ 今日避坑**")
        lines.append(f"  {ci.get('scenario', '')}")
        lines.append(f"  ❌ 常识: {ci.get('common_belief', '')}")
        lines.append(f"  ✅ 真相: {ci.get('reality', '')}")
        lines.append("")

    lines.append("💡 选题建议：从用户痛点出发，提供可执行方案而非承诺效果。")
    lines.append("")
    lines.append("#规则甄查 #每日选题 #合规运营 #短视频运营")
    lines.append("")

    return "\n".join(lines)


# ── 每日文案 · 视频号 （数据驱动 · 判断+建议）──

def _daily_shipinhao(m: dict, pains: list) -> str:
    safe_rate = f"{m['safe_passed'] / max(m['total_cases'], 1) * 100:.0f}%"
    pain_items = pains[:4] if pains else []

    lines = [
        "---",
        "平台: 视频号",
        "账号: 规则甄查",
        "类型: 每日文案 · 运营判断",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "---",
        "",
        "# 每日合规判断",
        "",
        f"**处理**: {m['total_cases']} 条 | "
        f"**拦截**: {m['risk_found']} 处 (HIGH×{m['total_high']}) | "
        f"**通过率**: {safe_rate}",
        "",
        "---",
        "",
        "## 今日核心判断",
        "",
    ]
    if m["platform_intent_detail"]:
        lines.append(m["platform_intent_detail"])
        lines.append("")

    lines.append("## 用户痛点 → 内容机会")
    lines.append("")
    for p in pain_items:
        lines.append(f"- 🔸 {p.get('text', '')}")
    lines.append("")
    lines.append("这些高频疑问，就是明天的选题方向。")
    lines.append("")

    if m["counter_intuitive"]:
        lines.append("## 边界预警")
        lines.append("")
        for ci in m["counter_intuitive"][:2]:
            lines.append(f"  **{ci.get('scenario', '')}**")
            lines.append(f"  建议: {ci.get('action', '')}")
            lines.append("")

    lines.append("---")
    lines.append(f"*pipeline #{m['pipeline_id']} · 甄先生 v2.0*")
    lines.append("")

    return "\n".join(lines)


# ── 每周报模板 · 公众号 （结构化周报）──

def _weekly_gongzhonghao(m: dict, pains: list) -> str:
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    trend_kw = "、".join(m["trend_keywords"][:6]) if m["trend_keywords"] else "内容生态"

    # 按 source 聚类痛点
    pain_by_source = {}
    for p in pains:
        s = p.get("source", "其他")
        pain_by_source.setdefault(s, []).append(p)

    lines = [
        "---",
        "平台: 公众号",
        "账号: 规则甄查",
        "类型: 每周报模板",
        f"生成时间: {today.strftime('%Y-%m-%d %H:%M')}",
        f"覆盖周期: {week_start.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}",
        "---",
        "",
        f"# 合规周报 · {today.strftime('%Y-%m-%d')}",
        "",
        "> 用规则思维做内容，让合规成为竞争力。",
        "",
        "---",
        "",
        "## 一、本周概览",
        "",
        "| 指标 | 本周 |",
        "|------|------|",
        f"| 审计文案 | {m['total_cases']} 条 |",
        f"| 拦截风险点 | {m['risk_found']} 处 |",
        f"| 高风险拦截 | {m['total_high']} 处 |",
        f"| 安全通过率 | {m['safe_passed'] / max(m['total_cases'], 1) * 100:.0f}% |",
        f"| 活跃领域 | {trend_kw} |",
        f"| 新增激励方向 | {m['trend_incentives']} 条 |",
        "",
        "---",
        "",
        "## 二、风险趋势分析",
        "",
        "### 本周预警 TOP 风险类别",
        "",
    ]
    for cate, count in m["top_risk_categories"]:
        lines.append(f"- **{cate}**: {count} 次触发")
    lines.append("")

    if m["counter_intuitive"]:
        lines.append("### 反直觉边界案例精选")
        lines.append("")
        for i, ci in enumerate(m["counter_intuitive"][:2], 1):
            lines.append(f"**案例 {i}: {ci.get('scenario', '')}**")
            lines.append(f"- 常见误区: {ci.get('common_belief', '')}")
            lines.append(f"- 真实判定: {ci.get('reality', '')}")
            lines.append(f"- 应对策略: {ci.get('action', '')}")
            lines.append("")

    lines.append("## 三、用户痛点聚类分析")
    lines.append("")
    lines.append(f"本周采集评论区高频疑问 {len(pains)} 条，按领域聚类：")
    lines.append("")
    for source, plist in sorted(pain_by_source.items(), key=lambda x: -len(x[1])):
        top3 = plist[:3]
        lines.append(f"### {source}（{len(plist)} 条）")
        for p in top3:
            lines.append(f"- [{p.get('score', 0)}] {p.get('text', '')}")
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 四、下周内容策略建议")
    lines.append("")
    lines.append("基于本周审计结果与用户痛点，建议下周聚焦：")
    lines.append("")
    if m["trend_keywords"]:
        lines.append("### 推荐选题方向")
        lines.append("")
        for kw in m["trend_keywords"][:4]:
            src_pains = pain_by_source.get(kw, [])
            q = src_pains[0]["text"] if src_pains else f"{kw}类内容"
            lines.append(f"1. **{kw}**: 围绕 \"{q}\" 制作解答型内容")
        lines.append("")
    lines.append("### 注意事项")
    lines.append("")
    lines.append("- 金融类内容必须添加风险提示，禁止任何保本暗示")
    lines.append("- AI 生成内容务必标注 AIGC 标签")
    lines.append("- 避免绝对化用语（第一、最、绝对），使用替代词")
    lines.append("- 个人经历分享 ≠ 医疗建议，需添加免责声明")
    lines.append("")

    if m["platform_intent_title"]:
        lines.append("## 五、平台意图解读")
        lines.append("")
        lines.append(f">{m['platform_intent_title']}")
        lines.append("")
        lines.append("*策略启示：顺着平台意图做内容，合规就是杠杆。*")
        lines.append("")

    lines.append("---")
    lines.append(f"*数据来源: pipeline #{m['pipeline_id']} · "
                 f"由 规则甄查 · 甄先生 v2.0 自动生成*")
    lines.append("")

    return "\n".join(lines)


# ── 主流程 ──

def publish(daily: bool = True, weekly: bool = False, mark_publish: bool = False):
    """生成平台发布内容"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 矩阵内容发布")
    print("=" * 48)

    state = _load_state()
    pains = _load_pains()
    m = _extract_daily_metrics(state)

    print(f"[STATE] {m['total_cases']} 案例 | {m['risk_found']} 风险 | {len(pains)} 痛点")

    if m["total_cases"] == 0 and not pains:
        print("[SKIP] 无运行数据")
        return

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {}

    if daily:
        dou = _daily_douyin(m, pains)
        dp = _DATA_DIR / f"publish_douyin_{ts}.md"
        dp.write_text(dou, encoding="utf-8")
        results["douyin"] = str(dp)
        print(f"[DOUYIN]  {dp.name}")

        sh = _daily_shipinhao(m, pains)
        sp = _DATA_DIR / f"publish_shipinhao_{ts}.md"
        sp.write_text(sh, encoding="utf-8")
        results["shipinhao"] = str(sp)
        print(f"[SHIPINHAO]  {sp.name}")

    if weekly:
        gzh = _weekly_gongzhonghao(m, pains)
        gp = _DATA_DIR / f"publish_gongzhonghao_{ts}.md"
        gp.write_text(gzh, encoding="utf-8")
        results["gongzhonghao"] = str(gp)
        print(f"[GONGZHONGHAO]  {gp.name}")

    # 更新 pipeline_state
    record = {
        "published_at": datetime.now().isoformat(),
        "files": results,
        "publish_flag": mark_publish,
        "type": "daily" if daily and not weekly else ("weekly" if weekly else "mixed"),
        "summary": {
            "total_cases": m["total_cases"],
            "risk_found": m["risk_found"],
            "total_high": m["total_high"],
            "safe_passed": m["safe_passed"],
            "pain_count": len(pains),
        },
    }
    state["matrix_publish"] = record
    _STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[STATE] pipeline_state.json 已更新")

    if mark_publish:
        print("[PUBLISH] 已标记发布")

    print(f"\n{'=' * 48}")
    print(f"  完成: {len(results)} 份产出")
    print(f"{'=' * 48}")
    return record


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="矩阵内容发布器 — 每日文案 + 每周报")
    parser.add_argument("--daily", action="store_true", help="生成每日文案（douyin+shipinhao）")
    parser.add_argument("--weekly", action="store_true", help="生成每周报模板（gongzhonghao）")
    parser.add_argument("--all", action="store_true", help="同时生成每日 + 每周")
    parser.add_argument("--publish", action="store_true", help="标记已发布")
    args = parser.parse_args()

    if args.all:
        publish(daily=True, weekly=True, mark_publish=args.publish)
    elif args.weekly:
        publish(daily=False, weekly=True, mark_publish=args.publish)
    elif args.daily:
        publish(daily=True, weekly=False, mark_publish=args.publish)
    else:
        # 默认：仅每日
        publish(daily=True, weekly=False, mark_publish=args.publish)
