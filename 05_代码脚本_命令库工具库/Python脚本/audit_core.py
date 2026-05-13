# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 红绿灯双向导航引擎
=============================================
功能：红灯避险（负向风险拦截）+ 绿灯起量（正向激励识别）+ 政策契合度评估
架构：JSON-RPC 2.0 兼容，供 MCP 服务器调用
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_RULES_PATH = Path(__file__).resolve().parent.parent / "rules.json"
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# 规则加载（带缓存）
# ──────────────────────────────────────────────

_RULES_CACHE: Optional[dict] = None


def _load_rules() -> dict:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        with open(_RULES_PATH, encoding="utf-8") as f:
            _RULES_CACHE = json.load(f)
    return _RULES_CACHE


def _invalidate_cache():
    global _RULES_CACHE
    _RULES_CACHE = None


# ──────────────────────────────────────────────
# 红灯模块：负向风险拦截
# ──────────────────────────────────────────────

def _audit_red_light(text: str, rules: dict) -> Tuple[List[dict], str]:
    """
    红灯审计：检测 HIGH / MEDIUM / LOW 三级风险词，返回风险列表与替换后文本。
    返回: (risks_list, refined_text)
    """
    risks = []
    refined = text

    for level, details in rules.get("risk_levels", {}).items():
        focus = details.get("focus", {})
        for word, info in focus.items():
            if word in text:
                risk_item = {
                    "level": level,
                    "category": details.get("category", ""),
                    "word": word,
                    "risk": info.get("risk", ""),
                    "replace_suggestion": info.get("replace", ""),
                    "policy_ref": info.get("policy_ref", ""),
                    "action": details.get("action", ""),
                }
                risks.append(risk_item)

                # 自动替换：提取 replace 中的第一个建议词
                replace_text = info.get("replace", "")
                if replace_text:
                    first_option = replace_text.split("/")[0].strip()
                    refined = refined.replace(word, first_option)

    return risks, refined


# ──────────────────────────────────────────────
# 绿灯模块：正向激励识别
# ──────────────────────────────────────────────

def _audit_green_light(text: str, rules: dict) -> List[dict]:
    """
    绿灯审计：识别内容中符合平台激励方向的特征，返回激励点列表。
    """
    incentives = []
    incentive_data = rules.get("incentive_points", {})

    for level, details in incentive_data.items():
        indicators = details.get("indicators", [])
        matched_indicators = []

        for indicator in indicators:
            # 将指标拆解为关键词进行模糊匹配
            keywords = _extract_keywords(indicator)
            match_count = sum(1 for kw in keywords if kw in text)
            if match_count >= len(keywords) * 0.5:  # 50% 以上关键词匹配即视为命中
                matched_indicators.append(indicator)

        if matched_indicators:
            incentives.append({
                "level": level,
                "category": details.get("category", ""),
                "description": details.get("description", ""),
                "matched_indicators": matched_indicators,
                "platform_boost": details.get("platform_boost", ""),
                "policy_ref": details.get("policy_ref", ""),
            })

    return incentives


def _extract_keywords(text: str) -> List[str]:
    """从指标描述中提取关键词（去除停用词后的有意义的词）"""
    # 简单分词：按常见分隔符拆分
    stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
                  "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
                  "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它",
                  "们", "与", "或", "及", "内容", "类", "提供", "展示"}
    # 按常见分隔符拆分
    parts = re.split(r'[，,、。.：:；;（）()""''\s]', text)
    keywords = [p.strip() for p in parts if p.strip() and p.strip() not in stop_words and len(p.strip()) > 1]
    return keywords


# ──────────────────────────────────────────────
# 政策契合度评估
# ──────────────────────────────────────────────

def evaluate_policy_fitness(text: str, rules: dict) -> dict:
    """
    评估内容与 2026 平台政策的契合度。
    返回四个维度的评分（0-100）及综合得分。
    """
    dimensions = rules.get("policy_fitness", {}).get("dimensions", [])
    scores = {}

    for dim in dimensions:
        name = dim["name"]
        weight = dim["weight"]
        desc = dim["description"]

        if name == "原创度":
            score = _score_originality(text)
        elif name == "真实性":
            score = _score_authenticity(text)
        elif name == "价值性":
            score = _score_value(text)
        elif name == "合规性":
            score = _score_compliance(text, rules)
        else:
            score = 50

        scores[name] = {
            "score": score,
            "weight": weight,
            "description": desc,
            "weighted_score": round(score * weight, 1),
        }

    total = round(sum(v["weighted_score"] for v in scores.values()), 1)

    return {
        "total_score": total,
        "dimensions": scores,
        "grade": _get_grade(total),
        "suggestion": _get_suggestion(total, scores),
    }


def _score_originality(text: str) -> int:
    """原创度评分：检测是否包含原创性特征"""
    originality_signals = [
        r"我[们]?[的].*[经验|方法|研究|发现|总结]",
        r"原创|独家|首发|实测|亲测",
        r"[0-9]{4}年.*[数据|报告|统计]",
        r"据.*[统计|调查|研究|分析]",
        r"案例[：:]",
        r"步骤[一二三四五六七八九十]",
    ]
    score = 40  # 基础分
    for pattern in originality_signals:
        if re.search(pattern, text):
            score += 10
    return min(score, 100)


def _score_authenticity(text: str) -> int:
    """真实性评分：检测是否包含可验证的真实信息"""
    authenticity_signals = [
        r"[0-9]{4}年",
        r"[0-9]+[月天日周]",
        r"[0-9]+[%％]",
        r"[0-9]+[万千万亿]",
        r"实测|实拍|实地|现场|真实",
        r"数据[：:]?\s*[0-9]",
        r"截图|录屏|证据|凭证",
    ]
    score = 35
    for pattern in authenticity_signals:
        if re.search(pattern, text):
            score += 10
    return min(score, 100)


def _score_value(text: str) -> int:
    """价值性评分：检测内容是否提供知识/技能/情绪价值"""
    value_signals = [
        r"教你|学会|掌握|了解|知道",
        r"方法|技巧|策略|方案|路径",
        r"为什么|如何|怎样|怎么",
        r"干货|精华|核心|关键|重点",
        r"避坑|防坑|注意|警惕|小心",
        r"趋势|方向|机会|蓝海|红利",
    ]
    score = 35
    for pattern in value_signals:
        if re.search(pattern, text):
            score += 10
    return min(score, 100)


def _score_compliance(text: str, rules: dict) -> int:
    """合规性评分：基于红灯检测结果反向评分"""
    risks, _ = _audit_red_light(text, rules)
    high_risks = sum(1 for r in risks if r["level"] == "HIGH")
    med_risks = sum(1 for r in risks if r["level"] == "MEDIUM")
    low_risks = sum(1 for r in risks if r["level"] == "LOW")

    score = 100
    score -= high_risks * 25
    score -= med_risks * 10
    score -= low_risks * 5
    return max(score, 0)


def _get_grade(total: float) -> str:
    if total >= 85:
        return "S · 卓越"
    elif total >= 70:
        return "A · 优秀"
    elif total >= 55:
        return "B · 良好"
    elif total >= 40:
        return "C · 待优化"
    else:
        return "D · 高风险"


def _get_suggestion(total: float, scores: dict) -> str:
    if total >= 85:
        return "内容契合度极高，建议加大投放获取流量红利。"
    elif total >= 70:
        weak = [k for k, v in scores.items() if v["score"] < 70]
        if weak:
            return f"整体表现优秀，建议针对性提升「{'」「'.join(weak)}」维度。"
        return "内容契合度良好，可正常发布并观察数据。"
    elif total >= 55:
        weak = [k for k, v in scores.items() if v["score"] < 60]
        if weak:
            return f"存在优化空间，重点改进「{'」「'.join(weak)}」维度后再发布。"
        return "建议优化后发布，降低限流风险。"
    elif total >= 40:
        return "风险较高，建议大幅修改后重新评估，避免触发平台处罚。"
    else:
        return "⚠️ 高风险内容，强烈建议放弃当前版本，重新创作。"


# ──────────────────────────────────────────────
# 优化建议生成
# ──────────────────────────────────────────────

def generate_optimization_advice(risks: List[dict], incentives: List[dict],
                                  fitness: dict) -> List[str]:
    """综合红灯、绿灯、政策契合度，生成可执行的优化建议"""
    advice = []

    # 基于红灯风险的建议
    high_risks = [r for r in risks if r["level"] == "HIGH"]
    med_risks = [r for r in risks if r["level"] == "MEDIUM"]

    if high_risks:
        words = "、".join([f"「{r['word']}」" for r in high_risks])
        advice.append(f"🔴 紧急：替换高风险词 {words}，建议改为 {high_risks[0]['replace_suggestion']}")

    if med_risks:
        words = "、".join([f"「{r['word']}」" for r in med_risks])
        advice.append(f"🟡 注意：修改营销诱导词 {words}，降低限流概率")

    # 基于绿灯激励的建议
    if incentives:
        top_incentive = incentives[0]
        advice.append(f"🟢 激励方向：内容符合「{top_incentive['category']}」，建议强化 {top_incentive['matched_indicators'][0]}")

    # 基于政策契合度的建议
    total = fitness.get("total_score", 0)
    if total < 70:
        weak_dims = [k for k, v in fitness.get("dimensions", {}).items() if v["score"] < 60]
        if weak_dims:
            advice.append(f"📊 政策契合度提升：重点优化「{'」「'.join(weak_dims)}」维度")

    if not advice:
        advice.append("✅ 内容质量优秀，无显著优化建议，建议直接发布并监控数据。")

    return advice


# ──────────────────────────────────────────────
# 主审计函数（统一入口）
# ──────────────────────────────────────────────

def audit_text(text: str) -> dict:
    """
    统一审计入口（兼容 v1.0 接口）。
    返回：{ is_safe, risks, refined_content }
    """
    rules = _load_rules()
    risks, refined = _audit_red_light(text, rules)
    return {
        "is_safe": len(risks) == 0,
        "risks": risks,
        "refined_content": refined,
    }


def _inject_green_language(text: str, incentives: List[dict]) -> str:
    """绿灯语言注入：在合规文案中植入正向激励表达"""
    if not incentives:
        return text

    # 从激励点提取可嵌入的短语句
    injections = {
        "GREEN_HIGH": [
            "原创深度内容",
            "行业深度分析",
            "可验证的实证数据",
        ],
        "GREEN_MEDIUM": [
            "真实体验分享",
            "实地验证数据",
            "用户实证案例",
        ],
        "GREEN_LOW": [
            "合规创新表达",
            "传统文化新解",
        ],
    }

    top_level = incentives[0]["level"]
    candidates = injections.get(top_level, [])
    if not candidates:
        return text

    # 仅在文案较短且无相关表达时注入
    if len(text) < 100 and not any(c[:4] in text for c in candidates):
        text += " · " + candidates[0]
    return text


def audit_dual(text: str, mode: str = "standard") -> dict:
    """
    双向导航审计（v2.0 核心接口）。

    Args:
        text: 待审计文案
        mode: 重构模式
            - "standard": 标准替换（仅红灯替换）
            - "aggressive": 激进优化（红灯替换 + 绿灯注入）

    Returns:
        { 风险点, 激励点, 政策契合度, 优化建议, 重构文案, 审计模式 }
    """
    rules = _load_rules()

    # 红灯：风险检测
    risks, refined = _audit_red_light(text, rules)

    # 绿灯：激励识别
    incentives = _audit_green_light(text, rules)

    # 政策契合度评估
    fitness = evaluate_policy_fitness(text, rules)

    # 优化建议
    advice = generate_optimization_advice(risks, incentives, fitness)

    # 激进模式：注入绿灯激励语言
    if mode == "aggressive" and incentives:
        refined_with_green = _inject_green_language(refined, incentives)
        advice.append(f"🟢 已注入合规激励表达：匹配「{incentives[0]['category']}」方向")
    else:
        refined_with_green = refined

    return {
        "version": "2.0.1",
        "mode": mode,
        "brand": rules.get("brand", ""),
        "tagline": rules.get("tagline", ""),
        "risk_points": risks,
        "incentive_points": incentives,
        "policy_fitness": fitness,
        "optimization_advice": advice,
        "refined_content": refined_with_green,
    }


# ──────────────────────────────────────────────
# CLI 测试入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！"

    print("=" * 60)
    print("  规则甄查 · 甄先生 v2.0 — 红绿灯双向导航")
    print("=" * 60)
    print(f"\n📝 原始文案: {test_text}\n")

    result = audit_dual(test_text)

    print("─" * 60)
    print("🔴 红灯 · 风险点")
    print("─" * 60)
    if result["risk_points"]:
        for r in result["risk_points"]:
            print(f"  [{r['level']}] {r['word']} → {r['risk']}")
            print(f"       建议: {r['replace_suggestion']}")
    else:
        print("  ✅ 未检测到风险")

    print("\n" + "─" * 60)
    print("🟢 绿灯 · 激励点")
    print("─" * 60)
    if result["incentive_points"]:
        for inc in result["incentive_points"]:
            print(f"  [{inc['level']}] {inc['category']}")
            print(f"       {inc['description']}")
    else:
        print("  💡 未检测到明显激励特征，建议增加实证/原创元素")

    print("\n" + "─" * 60)
    print("📊 政策契合度")
    print("─" * 60)
    fitness = result["policy_fitness"]
    print(f"  综合评分: {fitness['total_score']}/100  ({fitness['grade']})")
    for dim_name, dim_data in fitness.get("dimensions", {}).items():
        bar = "█" * (dim_data["score"] // 10) + "░" * (10 - dim_data["score"] // 10)
        print(f"  {dim_name}: {bar} {dim_data['score']}/100")

    print("\n" + "─" * 60)
    print("💡 优化建议")
    print("─" * 60)
    for i, adv in enumerate(result["optimization_advice"], 1):
        print(f"  {i}. {adv}")

    print("\n" + "─" * 60)
    print("📄 重构文案")
    print("─" * 60)
    print(f"  {result['refined_content']}")
    print("\n" + "=" * 60)
