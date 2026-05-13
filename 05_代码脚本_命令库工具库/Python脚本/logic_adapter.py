#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — Logic Adapter 逻辑适配器
===================================================
根据 user_pains.json 中的痛点频率/评分，自动匹配最适合的
思维维度（五大引擎）进行针对性分析。

独立模块，可被 deep_insight_agent.py / matrix_distiller.py 调用，
也可独立运行用于分析当前用户痛点分布。

用法：
  python logic_adapter.py                    # 分析当前 user_pains.json
  python logic_adapter.py --path data/user_pains.json  # 指定路径
  python logic_adapter.py --top 5            # 只显示 Top N 痛点
"""

import json
import sys
from collections import Counter
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR / "data"
_DEFAULT_PAINS_PATH = _DATA_DIR / "user_pains.json"

# 引擎→关键词映射表
# 关键词命中越多的痛点，匹配度越高
ENGINE_KEYWORDS = {
    "FPS": ["怎么", "如何", "方法", "本质", "核心", "原理", "为什么", "意义", "目的", "逻辑"],
    "EGT": ["封号", "违规", "处罚", "博弈", "竞争", "封", "限流", "举报", "警告", "黑名单", "降权"],
    "FMEA": ["风险", "安全", "会不会", "危险", "损失", "失败", "错误", "隐患", "避坑", "防"],
    "MOS": ["推荐", "选择", "对比", "稳健", "靠谱", "底线", "边界", "区别", "哪个好", "预算"],
    "RTT": ["规则", "政策", "新规", "法规", "监管", "审核", "通告", "合规", "标准", "条款"],
}

ENGINE_LABELS = {
    "FPS": "第一性原理",
    "EGT": "演化博弈",
    "FMEA": "FMEA",
    "MOS": "安全边际",
    "RTT": "监管溯源",
}


# ──────────────────────────────────────────────
# 适配核心
# ──────────────────────────────────────────────


def load_pains(path: Path = None) -> list:
    """读取 user_pains.json，按评分降序"""
    path = path or _DEFAULT_PAINS_PATH
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return sorted(data.get("pains", []), key=lambda p: p.get("score", 0), reverse=True)
    except Exception as e:
        print(f"[ERROR] 读取痛点失败: {e}")
        return []


def map_pains_to_engines(pains: list) -> dict:
    """痛点→引擎映射，返回各引擎的加权评分

    Returns:
        {engine_id: weighted_score, ...}
    """
    scores = Counter()
    for p in pains:
        text = p.get("text", "")
        score = p.get("score", 1)
        for engine, keywords in ENGINE_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if kw in text)
            if match_count > 0:
                scores[engine] += score * match_count  # 权重=评分×匹配度

    total = sum(scores.values()) or 1
    return {e: round(c / total, 3) for e, c in scores.most_common()}


def best_engine_for_pain(pain_text: str) -> tuple:
    """对单条痛点文本，返回最佳引擎 (engine_id, score, matched_keywords)"""
    best = None
    best_score = 0
    best_kws = []
    for engine, keywords in ENGINE_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in pain_text]
        if matched and len(matched) > best_score:
            best = engine
            best_score = len(matched)
            best_kws = matched
    return best, best_score, best_kws


def adapter_summary(pains: list, top_n: int = 3) -> dict:
    """生成 adapter 总览数据（供 pipeline_state 注入）"""
    pain_map = map_pains_to_engines(pains)

    top_pains = []
    for p in pains[:top_n]:
        engine_id, _, matched_kws = best_engine_for_pain(p.get("text", ""))
        top_pains.append({
            "text": p.get("text", "")[:60],
            "score": p.get("score", 0),
            "best_engine": engine_id or "unknown",
            "matched_keywords": matched_kws,
        })

    best_overall = max(pain_map, key=pain_map.get) if pain_map else "FPS"

    return {
        "total_pains": len(pains),
        "engine_scores": pain_map,
        "lead_engine": best_overall,
        "lead_engine_label": ENGINE_LABELS.get(best_overall, best_overall),
        "top_pains": top_pains,
    }


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────


def _format_pain_row(p: dict) -> str:
    """格式化单条痛点显示"""
    text = p.get("text", "")[:50]
    score = p.get("score", 0)
    source = p.get("source", "?")
    engine_id, _, matched = best_engine_for_pain(text)
    engine_label = ENGINE_LABELS.get(engine_id, "—")
    return f"  [{score:2d}] [{source:8s}] → {engine_label:6s} | {text}"


def main(path: str = None, top: int = 20):
    pains = load_pains(Path(path) if path else None)
    if not pains:
        print("[SKIP] 无痛点数据")
        return

    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — Logic Adapter")
    print("  痛点 → 思维引擎映射")
    print("=" * 48)

    print(f"\n[PAINS] 共 {len(pains)} 条\n")

    # 引擎评分
    engine_scores = map_pains_to_engines(pains)
    if engine_scores:
        print("引擎匹配度:")
        for e, s in engine_scores.items():
            label = ENGINE_LABELS.get(e, e)
            bar = "█" * max(1, int(s * 40))
            print(f"  {label:6s} │{bar} {s*100:.0f}%")
        best = max(engine_scores, key=engine_scores.get)
        print(f"\n最佳引擎: {ENGINE_LABELS.get(best, best)}")

    print(f"\n痛点详情 (Top {min(top, len(pains))}):")
    for p in pains[:top]:
        print(_format_pain_row(p))

    # 单条最佳匹配演示
    print(f"\n{'─' * 48}")
    print(f"单条痛点解析 (Top 3):")
    for p in pains[:3]:
        text = p.get("text", "")[:50]
        engine_id, score, kws = best_engine_for_pain(text)
        label = ENGINE_LABELS.get(engine_id, "无匹配")
        print(f"  \"{text}\"")
        print(f"    最佳引擎: {label} (匹配={score}, 关键词={kws})")

    print(f"\n{'=' * 48}")
    print(f"  适配完成")
    print(f"{'=' * 48}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Logic Adapter — 痛点→思维引擎映射")
    parser.add_argument("--path", type=str, default=None, help="user_pains.json 路径")
    parser.add_argument("--top", type=int, default=20, help="显示 Top N 痛点")
    args = parser.parse_args()
    main(path=args.path, top=args.top)
