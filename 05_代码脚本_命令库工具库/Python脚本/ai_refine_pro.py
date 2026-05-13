# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — AI 静奢风闭环重塑引擎
=================================================
流程：红灯审计 → AI改写 → 再审计验证 → 通过/回退
API：DeepSeek 直连 (OpenAI-compatible)

闭环保证：每次改写后自动 re-audit，风险归零才通过。
"""

import sys
from pathlib import Path
from typing import Optional
import requests

from core.audit_core import audit_dual

# ──────────────────────────────────────────────
# API 配置
# ──────────────────────────────────────────────

_API_KEY = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
_API_URL = "https://api.deepseek.com/v1/chat/completions"
_MODEL = "deepseek-chat"

_REFINE_SYSTEM_PROMPT = """你是一位精通短视频平台合规的专业文案优化师，服务于「规则甄查 · 甄先生」品牌。你的任务是对高风险短视频文案进行"静奢风"改写——在保留表达意图的前提下，规避所有合规风险，提升品质感。

## 改写原则
1. 规避红灯：将绝对化用语、违禁词替换为克制表达
2. 价值升维：将利益驱动转化为价值驱动（如"赚钱秘籍"→"资产增值逻辑"）
3. 静奢克制：语言极简、精密、无冗余，避免夸张和情绪化表达
4. 合规优先：任何时候安全合规大于表达效果
5. 避免将具象、高情绪价值的“第一”“绝对”等强断言替换为抽象、低情绪价值的“业内深耕”“资产增值”等术语，保留原文的稀缺性承诺和确定性表达，以维持互动驱动力。
5. 保留原文的稀缺性暗示和行动号召强度，避免将“唯一性”和“紧迫感”替换为抽象描述，防止信息密度和情绪驱动力下降。

## 输出要求
- 仅输出改写后的文案正文，不加解释、不加引号、不加任何标记
- 保持原文长度基本一致
- 不引入新的违禁词或诱导词
- 不要输出JSON或其他包裹格式"""


def _call_api(messages: list, max_tokens: int = 1024) -> Optional[str]:
    """调用 DeepSeek Chat API（OpenAI-compatible）"""
    try:
        resp = requests.post(
            _API_URL,
            headers={
                "Authorization": f"Bearer {_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": _MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  ⚠️ API 调用失败: {e}")
        return None


def ai_refine(text: str, risks: list) -> Optional[str]:
    """AI 改写：基于审计风险点定向优化"""
    risk_detail = "\n".join(
        f"- [{r['level']}] 「{r['word']}」→ 建议替换为「{r['replace_suggestion']}」"
        for r in risks
    )

    user_prompt = f"""## 待改写文案
{text}

## 已检测到的风险点及替换建议
{risk_detail}

请根据改写原则输出优化后的文案："""

    return _call_api([
        {"role": "system", "content": _REFINE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])


def _rule_fallback(text: str, risks: list) -> str:
    """API 不可用时用规则兜底替换"""
    refined = text
    for r in risks:
        old = r["word"]
        replacement = r["replace_suggestion"].split("/")[0].strip()
        if replacement:
            refined = refined.replace(old, replacement)
    return refined


def _count_risks_by_level(audit_result: dict) -> dict:
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in audit_result.get("risk_points", []):
        level = r.get("level", "LOW")
        if level in counts:
            counts[level] += 1
    return counts


# ──────────────────────────────────────────────
# 核心闭环：审计 → AI改写 → 再审计验证
# ──────────────────────────────────────────────

def refine_with_verification(text: str, mode: str = "standard",
                              max_rounds: int = 3) -> dict:
    """
    闭环：审计 → AI改写 → 再审计验证 → 通过/继续/回退

    Args:
        text: 原始文案
        mode: "standard" 规则替换 / "aggressive" 规则替换+绿灯注入
        max_rounds: 最大改写轮次

    Returns:
        完整闭环报告，含 verified_safe 布尔标识
    """
    # ── 第一轮：原始文案审计 ──
    pre_audit = audit_dual(text, mode=mode)
    pre_risk_counts = _count_risks_by_level(pre_audit)

    print(f"  \U0001f4cb 原始风险: HIGH={pre_risk_counts['HIGH']}, "
          f"MEDIUM={pre_risk_counts['MEDIUM']}, LOW={pre_risk_counts['LOW']}")

    # 无风险，直接通过
    if not pre_audit["risk_points"]:
        return {
            "original_text": text,
            "final_text": text,
            "rounds": 0,
            "pre_audit": pre_audit,
            "post_audit": pre_audit,
            "verified_safe": True,
            "mode": mode,
        }

    current_text = text
    history = []
    verified = False
    final_audit = pre_audit

    for round_num in range(1, max_rounds + 1):
        print(f"\n  \U0001f504 第 {round_num} 轮改写...")

        # ── AI改写 ──
        rewritten = ai_refine(current_text, pre_audit["risk_points"])
        if rewritten is None:
            print(f"  ⚠️ API 不可用，使用规则兜底替换")
            rewritten = _rule_fallback(current_text, final_audit["risk_points"])
        current_text = rewritten

        # ── 再审计验证 ──
        final_audit = audit_dual(current_text, mode=mode)
        post_risk_counts = _count_risks_by_level(final_audit)

        history.append({
            "round": round_num,
            "text": current_text,
            "risk_counts": post_risk_counts,
            "risk_count": len(final_audit["risk_points"]),
            "policy_fitness": final_audit["policy_fitness"],
        })

        print(f"  ✅ 改写后风险: HIGH={post_risk_counts['HIGH']}, "
              f"MEDIUM={post_risk_counts['MEDIUM']}, LOW={post_risk_counts['LOW']}")

        # 零风险 → 通过
        if not final_audit["risk_points"]:
            verified = True
            print(f"  ✅ 第 {round_num} 轮验证通过！零风险。")
            break

        # 风险未继续减少 → 提前终止，避免死循环
        if round_num > 1:
            prev_count = history[-2]["risk_count"]
            curr_count = len(final_audit["risk_points"])
            if curr_count >= prev_count:
                print(f"  ⏱️ 风险未继续减少，停止改写")
                break

    return {
        "original_text": text,
        "final_text": current_text,
        "rounds": len(history),
        "round_history": history,
        "pre_audit": pre_audit,
        "post_audit": final_audit,
        "verified_safe": verified,
        "mode": mode,
    }


# ──────────────────────────────────────────────
# 报告输出
# ──────────────────────────────────────────────

def _print_report(result: dict):
    pre = result["pre_audit"]
    post = result["post_audit"]
    pre_risks = _count_risks_by_level(pre)
    post_risks = _count_risks_by_level(post)
    pre_fit = pre.get("policy_fitness", {})
    post_fit = post.get("policy_fitness", {})

    print("\n" + "=" * 64)
    print("  规则甄查 · 甄先生 v2.0 — AI 闭环重塑报告")
    print("=" * 64)

    print(f"\n\U0001f4dd 原始文案")
    print(f"  {result['original_text']}")

    print(f"\n\U0001f4c4 终版文案")
    print(f"  {result['final_text']}")

    print(f"\n" + "─" * 64)
    print("\U0001f534 风险变化")
    print("─" * 64)
    print(f"  高风险: {pre_risks['HIGH']} → {post_risks['HIGH']}  "
          f"{'✅ 清除' if post_risks['HIGH'] == 0 else '⚠️ 仍有残留'}")
    print(f"  中风险: {pre_risks['MEDIUM']} → {post_risks['MEDIUM']}  "
          f"{'✅ 清除' if post_risks['MEDIUM'] == 0 else '⚠️ 仍有残留'}")
    print(f"  低风险: {pre_risks['LOW']} → {post_risks['LOW']}")
    print(f"  改写轮次: {result['rounds']}")
    status = "✅ 闭环验证通过 · 零风险" if result["verified_safe"] else "⚠️ 仍有风险 · 建议人工调整"
    print(f"  验证状态: {status}")

    print(f"\n" + "─" * 64)
    print("\U0001f4ca 政策契合度变化")
    print("─" * 64)
    print(f"  综合评分: {pre_fit.get('total_score', 'N/A')} → {post_fit.get('total_score', 'N/A')}")
    for dim in pre_fit.get("dimensions", {}):
        ps = pre_fit["dimensions"][dim]["score"]
        fs = post_fit["dimensions"][dim]["score"]
        delta = fs - ps
        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "─"
        print(f"  {dim}: {ps} → {fs}  ({arrow}{abs(delta)})")

    print(f"\n" + "─" * 64)
    print("\U0001f4a1 优化建议")
    print("─" * 64)
    for adv in post.get("optimization_advice", []):
        print(f"  • {adv}")

    print("\n" + "=" * 64)


# ──────────────────────────────────────────────
# 批量处理
# ──────────────────────────────────────────────

def run_batch(test_cases: list, mode: str = "standard"):
    total = len(test_cases)
    safe_count = 0

    for i, text in enumerate(test_cases, 1):
        print(f"\n\n{'=' * 64}")
        print(f"  ▶ 案例 {i}/{total}")
        print(f"{'=' * 64}")
        result = refine_with_verification(text, mode=mode)
        _print_report(result)
        if result["verified_safe"]:
            safe_count += 1

    print(f"\n{'=' * 64}")
    print(f"  闭环审计小结：共 {total} 案，通过 {safe_count}，待优化 {total - safe_count}")
    print(f"{'=' * 64}")


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！",
        "点击领取私信我，最快入账方式，绝对赚钱。",
        "零成本创业，一学就会的赚钱方法。",
    ]

    mode = "aggressive" if len(sys.argv) > 1 and sys.argv[1] == "aggressive" else "standard"

    run_batch(test_cases, mode=mode)
