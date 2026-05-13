#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 矩阵内容蒸馏器（多端动态变调）
=========================================================
读取 pipeline_state 中的五大思维引擎输出 + user_pains，
自动为 3 个平台生成风格各异的 Markdown 发布文案。

变调策略：
  - 抖音 (规则情报局):  EGT 博弈结论 + 反直觉避坑 → 快节奏风险预警
  - 视频号 (规则甄查):  FMEA 审计 + 安全边际 → 案例驱动
  - 公众号 (规则甄查):  FPS 第一性原理 + RTT 监管溯源 → 深度长文

用法：
  python matrix_distiller.py                # 基于今日数据生成
  python matrix_distiller.py --publish      # 生成 + 标记已发布
  python matrix_distiller.py --history 3    # 回溯近 3 天记录
"""

import json
from datetime import datetime
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


# ──────────────────────────────────────────────
# 读取数据源
# ──────────────────────────────────────────────


def _load_state() -> dict:
    if _STATE_PATH.exists():
        return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    return {}


def _load_pains() -> dict:
    if _PAINS_PATH.exists():
        return json.loads(_PAINS_PATH.read_text(encoding="utf-8"))
    return {"pains": [], "extracted_at": "N/A"}


def _summarize_today(state: dict) -> dict:
    """从 pipeline_state 提取今日关键数据"""
    steps = state.get("steps", [])
    refine_results = state.get("refine_results", [])
    di = state.get("deep_insight", {})
    trend = state.get("trend_collection", {})
    shadow = state.get("shadow_simulation", {})

    risk_found = 0
    safe_passed = 0
    for r in refine_results:
        pre = r.get("pre_audit", {})
        risk_found += len(pre.get("risk_points", []))
        if r.get("verified_safe"):
            safe_passed += 1

    # 思维引擎权重
    engine_weights = di.get("thinking_engine_weights", {})
    # 排序：按 weight 降序
    sorted_engines = sorted(
        engine_weights.items(),
        key=lambda x: x[1].get("weight", 0) if isinstance(x[1], dict) else 0,
        reverse=True,
    )

    # 痛点→引擎映射
    pain_engine_map = di.get("pain_engine_map", {})

    # 主导引擎
    lead_engine = ""
    if sorted_engines:
        e_name = sorted_engines[0][0]
        label_map = {"FPS": "第一性原理", "EGT": "演化博弈", "FMEA": "FMEA", "MOS": "安全边际", "RTT": "监管溯源"}
        lead_engine = label_map.get(e_name, e_name)

    summary = {
        "total_cases": len(refine_results),
        "safe_passed": safe_passed,
        "risk_found": risk_found,
        "duration_s": sum(s.get("duration_s", 0) for s in steps),
        "status": state.get("status", "none"),
        "pipeline_id": state.get("pipeline_id", ""),
        # 深度洞察
        "platform_intent": di.get("platform_intent", {}).get("title", ""),
        "counter_intuitive": di.get("counter_intuitive", []),
        "fmea_table": di.get("fmea_table", []),
        # 思维引擎
        "engine_weights": {k: v.get("weight", 0) if isinstance(v, dict) else 0 for k, v in engine_weights.items()},
        "sorted_engines": [{"id": e[0], "weight": e[1].get("weight", 0) if isinstance(e[1], dict) else 0, "label": label_map.get(e[0], e[0])} for e in sorted_engines],
        "lead_engine": lead_engine,
        "pain_engine_map": pain_engine_map,
        # 趋势
        "trend_incentives": trend.get("total_incentives", 0),
        "trend_keywords": trend.get("keywords", []),
        # 影子模拟
        "shadow_degraded": shadow.get("degraded_count", 0),
        "shadow_lock": shadow.get("lock_status", "none"),
    }
    return summary


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

_ENGINE_LABELS = {
    "FPS": "第一性原理",
    "EGT": "演化博弈",
    "FMEA": "FMEA",
    "MOS": "安全边际",
    "RTT": "监管溯源",
}


def _engine_bar(weights: dict) -> str:
    """ASCII 权重条形图"""
    if not weights:
        return ""
    lines = []
    for name, label in [("FPS", "第一性原理"), ("EGT", "演化博弈"), ("FMEA", "FMEA"), ("MOS", "安全边际"), ("RTT", "监管溯源")]:
        w = weights.get(name, 0) or 0
        bar = "█" * max(1, w // 10) if w > 0 else "▁"
        lines.append(f"  {label:6s} │{bar:10s} {w}")
    return "\n".join(lines)


def _pick_engine(weights: dict, preferred: list) -> str:
    """从偏好列表中选权重最高的引擎"""
    best = None
    best_w = -1
    for e in preferred:
        w = weights.get(e, 0) or 0
        if w > best_w:
            best_w = w
            best = e
    return best


# ──────────────────────────────────────────────
# 文案模板 — 多端动态变调
# ──────────────────────────────────────────────


def _douyin_copy(s: dict, pains: list) -> str:
    """规则情报局 · 抖音 — EGT 博弈结论 + 反直觉避坑

    变调策略：从 counter_intuitive 中选取最具博弈冲突的案例，
    以"博弈结论"为钩子，强调风险—收益的权衡关系。
    """
    insight = s.get("platform_intent") or "平台规则正在快速迭代"
    ci_list = s.get("counter_intuitive", [])[:2]
    weights = s.get("engine_weights", {})
    lead = _pick_engine(weights, ["EGT", "FMEA", "MOS"]) or "EGT"
    lead_label = _ENGINE_LABELS.get(lead, lead)
    pain_point = pains[0].get("text", "合规到底怎么做？") if pains else "合规到底怎么做？"

    lines = [
        "---",
        "平台: 抖音",
        "账号: 规则情报局",
        "风格: 博弈结论 · 反直觉避坑",
        f"主导引擎: {lead_label}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "---",
        "",
        f"🔥 \"{pain_point}\"",
        "",
        f"平台释放了一个博弈信号：{insight}",
        "",
        "今天 3 条必知变化 👇",
        "",
    ]

    if lead == "EGT":
        lines.append("🎯 **博弈视角** — 这不是单向管控，是平台与创作者之间的均衡调整。")
        lines.append("你每踩一次红线，平台就收紧一格。理解博弈规则的人，先拿到流量红利。")
        lines.append("")
    elif lead == "FMEA":
        lines.append("⚠️ **FMEA 优先级** — 按风险等级排序，先解决最高 RPN 的问题。")
        lines.append("")

    # 反直觉教训（博弈包装）
    for i, item in enumerate(ci_list, 1):
        lines.append(f"{i}. **{item.get('scenario', '')}**")
        lines.append(f"   ❌ 常识: {item.get('common_belief', '')}")
        lines.append(f"   ✅ 博弈结论: {item.get('reality', '')}")
        lines.append(f"   💡 {item.get('action', '')}")
        lines.append("")

    if weights:
        lines.append("📊 **思维权重分布**")
        lines.append("")
        lines.append(_engine_bar(weights))

    lines.append("")
    lines.append("💡 合规不是束缚，是帮你避开暗礁的导航。")
    lines.append("")
    lines.append("#规则甄查 #合规运营 #博弈分析 #避坑指南")
    lines.append("")

    return "\n".join(lines)


def _shipinhao_copy(s: dict, pains: list) -> str:
    """规则甄查 · 视频号 — FMEA 审计 + 安全边际

    变调策略：以 FMEA 优先级表格为骨架，展示风险失效模式，
    用安全边际计算帮助创作者建立"合规缓冲区"。
    """
    ci_list = s.get("counter_intuitive", [])
    fmea_list = s.get("fmea_table", [])
    weights = s.get("engine_weights", {})
    lead = _pick_engine(weights, ["FMEA", "MOS", "EGT"]) or "FMEA"
    lead_label = _ENGINE_LABELS.get(lead, lead)
    pain_top3 = pains[:3] if pains else []

    lines = [
        "---",
        "平台: 视频号",
        "账号: 规则甄查",
        "风格: FMEA 审计 · 安全边际",
        f"主导引擎: {lead_label}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "---",
        "",
        "# 合规日报 · FMEA 风险审计",
        "",
        f"**今日处理**: {s['total_cases']} 条文案 | "
        f"**拦截风险**: {s['risk_found']} 处 | "
        f"**安全通过**: {s['safe_passed']} 条",
        "",
        "---",
        "",
        "## 核心判断",
        "",
        f"> {s.get('platform_intent') or '平台规则持续更新中'}",
        "",
    ]

    if fmea_list:
        lines.append("## FMEA 风险优先级分析")
        lines.append("")
        lines.append("| 失效模式 | S(严重度) | O(发生度) | D(检测度) | RPN | 建议 |")
        lines.append("|----------|----------|----------|----------|-----|------|")
        for item in fmea_list[:5]:
            fm = item.get("failure_mode", "")[:24]
            s_val = item.get("severity", 0)
            o_val = item.get("occurrence", 0)
            d_val = item.get("detection", 0)
            rpn = item.get("rpn", s_val * o_val * d_val)
            rec = item.get("recommendation", "")[:20]
            lines.append(f"| {fm} | {s_val} | {o_val} | {d_val} | **{rpn}** | {rec} |")
        lines.append("")

        # 最高 RPN 警告
        max_item = max(fmea_list, key=lambda x: x.get("rpn", 0))
        lines.append(f"⚠️ **最高优先级**: {max_item.get('failure_mode', '')} (RPN={max_item.get('rpn', 0)})")
        lines.append(f"   → {max_item.get('recommendation', '')}")
        lines.append("")

    if lead == "MOS":
        lines.append("## 安全边际建议")
        lines.append("")
        lines.append("在规则边界之外建立缓冲区是专业创作者的核心技能：")
        lines.append('- 避免使用任何可能被"放大解读"的表述')
        lines.append('- 涉及数据/收益时至少保留 30% 的安全余量')
        lines.append("- AI 生成内容标注不仅合规，更是信任资产")
        lines.append("")

    if ci_list:
        lines.append("## 反直觉边界案例")
        lines.append("")
        for item in ci_list:
            lines.append(f"### {item.get('scenario', '')}")
            lines.append(f"- **常见认知**: {item.get('common_belief', '')}")
            lines.append(f"- **真实判定**: {item.get('reality', '')}")
            lines.append(f"- **原因**: {item.get('reason', '')}")
            lines.append(f"- **建议**: {item.get('action', '')}")
            lines.append("")

    if pain_top3:
        lines.append("## 用户最关心的问题")
        lines.append("")
        for p in pain_top3:
            lines.append(f"- {p.get('text', '')}")
        lines.append("")

    if weights:
        lines.append("## 思维引擎权重")
        lines.append("")
        lines.append(_engine_bar(weights))
        lines.append("")

    lines.append("---")
    lines.append("*由 规则甄查 · 甄先生 v2.0 · FMEA 风险审计引擎生成*")
    lines.append("")

    return "\n".join(lines)


def _gongzhonghao_copy(s: dict, pains: list, state: dict) -> str:
    """规则甄查 · 公众号 — FPS 第一性原理 + RTT 监管溯源

    变调策略：以第一性原理深挖规则本质，用监管溯源还原政策意图，
    形成完整的"本质→历史→边界→展望"论证链条。
    """
    di = state.get("deep_insight", {})
    pi = di.get("platform_intent", {})
    pl = di.get("policy_logic", {})
    ci_list = s.get("counter_intuitive", [])
    fmea_list = s.get("fmea_table", [])
    weights = s.get("engine_weights", {})
    trend_kw = s.get("trend_keywords", [])
    trend_inc = s.get("trend_incentives", 0)
    lead = _pick_engine(weights, ["FPS", "RTT", "FMEA"]) or "FPS"
    lead_label = _ENGINE_LABELS.get(lead, lead)
    pain_map = s.get("pain_engine_map", {})

    lines = [
        "---",
        "平台: 公众号",
        "账号: 规则甄查",
        "风格: 第一性原理 · 监管溯源 · 深度分析",
        f"主导引擎: {lead_label}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "---",
        "",
        f"# 合规本周深度报告：{datetime.now().strftime('%Y-%m-%d')}",
        "",
        "> 用规则思维做内容，让合规成为竞争力。",
        "",
        "---",
        "",
        "## 一、今日概览",
        "",
        f"| 指标 | 数值 |",
        "|------|------|",
        f"| 处理文案 | {s['total_cases']} 条 |",
        f"| 拦截风险点 | {s['risk_found']} 处 |",
        f"| 安全通过 | {s['safe_passed']} 条 |",
        f"| 全流程耗时 | {s['duration_s']}s |",
        f"| 主导思维引擎 | {lead_label} |",
        f"| 趋势领域 | {', '.join(trend_kw[:4]) if trend_kw else '—'} |",
        f"| 新增激励词 | {trend_inc} 条 |",
        "",
        "---",
        "",
    ]

    # 思维权重看板
    if weights:
        lines.append("## 思维引擎权重分布")
        lines.append("")
        lines.append("```")
        lines.append(_engine_bar(weights))
        lines.append("```")
        lines.append("")

    # 平台意图
    if pi:
        lines.append("## 二、平台意图深度分析")
        lines.append("")
        lines.append(f"### {pi.get('title', '')}")
        lines.append("")
        lines.append(pi.get("detail", ""))
        lines.append("")
        if pi.get("driving_forces"):
            lines.append("**驱动力分析**：")
            for f in pi["driving_forces"]:
                lines.append(f"- {f}")
            lines.append("")

    # 政策逻辑
    if pl:
        lines.append("## 三、政策逻辑拆解")
        lines.append("")
        lines.append(f"### {pl.get('title', '')}")
        lines.append("")
        if pl.get("causal_chain"):
            for c in pl["causal_chain"]:
                lines.append(f"- {c}")
            lines.append("")
        if pl.get("impact_path"):
            lines.append(f"**影响路径**: {pl['impact_path']}")
            lines.append("")

    # FMEA 表格
    if fmea_list:
        lines.append("## 四、FMEA 失效模式分析")
        lines.append("")
        lines.append("| 失效模式 | S | O | D | RPN | 建议 |")
        lines.append("|---------|---|---|----|-----|------|")
        for item in fmea_list[:5]:
            fm = item.get("failure_mode", "")[:24]
            s_val = item.get("severity", 0)
            o_val = item.get("occurrence", 0)
            d_val = item.get("detection", 0)
            rpn = item.get("rpn", s_val * o_val * d_val)
            rec = item.get("recommendation", "")[:20]
            lines.append(f"| {fm} | {s_val} | {o_val} | {d_val} | **{rpn}** | {rec} |")
        lines.append("")

    # 反直觉案例
    if ci_list:
        lines.append("## 五、反直觉边界案例")
        lines.append("")
        for i, item in enumerate(ci_list, 1):
            lines.append(f"### {i}. {item.get('scenario', '')}")
            lines.append(f"- **常见误区**: {item.get('common_belief', '')}")
            lines.append(f"- **真实判定**: {item.get('reality', '')}")
            lines.append(f"- **原因解析**: {item.get('reason', '')}")
            lines.append(f"- **应对策略**: {item.get('action', '')}")
            lines.append("")

    # 用户痛点
    if pains:
        lines.append("## 六、用户痛点与引擎匹配")
        lines.append("")
        lines.append(f"采集自竞对评论区，共 {len(pains)} 条高频问题。")
        lines.append("逻辑适配器（Logic Adapter）已自动匹配最佳思维引擎：")
        lines.append("")
        if pain_map:
            lines.append("| 引擎 | 匹配度 |")
            lines.append("|------|--------|")
            for engine, pct in sorted(pain_map.items(), key=lambda x: -x[1]):
                label = _ENGINE_LABELS.get(engine, engine)
                lines.append(f"| {label} | {pct*100:.0f}% |")
            lines.append("")
            top_engine = max(pain_map, key=pain_map.get)
            top_label = _ENGINE_LABELS.get(top_engine, top_engine)
            lines.append(f"**最佳匹配**: {top_label} — 当前用户痛点最集中的思维维度。")
            lines.append("")

        lines.append("Top 痛点预览：")
        lines.append("")
        for p in pains[:6]:
            lines.append(f"- [{p.get('score', 0)}] {p.get('text', '')}")
        lines.append("")

    lines.append("---")
    lines.append(f"*数据来源: pipeline #{s['pipeline_id']} · "
                 f"思维引擎: {lead_label if lead_label else '标准'} · "
                 f"由 规则甄查 · 甄先生 v2.0 自动蒸馏生成*")
    lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────


def distill(publish: bool = False):
    """读取状态 → 生成 3 平台文案 → 存储"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 矩阵内容蒸馏")
    print("  [多端动态变调]")
    print("=" * 48)

    # 1. 加载数据
    state = _load_state()
    pains_data = _load_pains()
    pains = pains_data.get("pains", [])

    summary = _summarize_today(state)
    lead = summary.get("lead_engine", "")
    print(f"[STATE] pipeline {summary['pipeline_id']} | "
          f"{summary['total_cases']} 案例 | {summary['risk_found']} 风险")
    print(f"[ENGINE] 主导: {lead} | 引擎: {list(summary['engine_weights'].keys())}")
    print(f"[PAINS] {len(pains)} 条痛点")

    if summary["total_cases"] == 0 and not pains:
        print("[SKIP] 无运行数据，无法蒸馏")
        return

    # 2. 生成三份文案
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    copies = {}

    # 抖音 — EGT 博弈 + 反直觉
    douyin = _douyin_copy(summary, pains)
    douyin_path = _DATA_DIR / f"publish_douyin_{ts}.md"
    douyin_path.write_text(douyin, encoding="utf-8")
    copies["douyin"] = str(douyin_path)
    print(f"\n[DOUYIN] {douyin_path.name}")

    # 视频号 — FMEA + MOS
    shipinhao = _shipinhao_copy(summary, pains)
    shipinhao_path = _DATA_DIR / f"publish_shipinhao_{ts}.md"
    shipinhao_path.write_text(shipinhao, encoding="utf-8")
    copies["shipinhao"] = str(shipinhao_path)
    print(f"[SHIPINHAO] {shipinhao_path.name}")

    # 公众号 — FPS + RTT
    gzh = _gongzhonghao_copy(summary, pains, state)
    gzh_path = _DATA_DIR / f"publish_gongzhonghao_{ts}.md"
    gzh_path.write_text(gzh, encoding="utf-8")
    copies["gongzhonghao"] = str(gzh_path)
    print(f"[GONGZHONGHAO] {gzh_path.name}")

    # 3. 同步到 pipeline_state
    record = {
        "distilled_at": datetime.now().isoformat(),
        "files": copies,
        "publish_flag": publish,
        "lead_engine": lead,
        "engine_weights": summary.get("engine_weights", {}),
        "pain_engine_map": summary.get("pain_engine_map", {}),
        "summary": {
            "total_cases": summary["total_cases"],
            "risk_found": summary["risk_found"],
            "safe_passed": summary["safe_passed"],
            "trend_incentives": summary["trend_incentives"],
        },
    }
    state["matrix_distill"] = record
    _STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[STATE] pipeline_state.json 已更新")

    if publish:
        print("[PUBLISH] 已标记为待发布 (可在 status.html 预览)")

    print(f"\n{'=' * 48}")
    print(f"  完成: 3 份文案已生成")
    print(f"  主导引擎: {lead}")
    print(f"{'=' * 48}")

    return record


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="矩阵内容蒸馏器 — 多端动态变调")
    parser.add_argument("--publish", action="store_true", help="生成 + 标记待发布")
    args = parser.parse_args()
    distill(publish=args.publish)
