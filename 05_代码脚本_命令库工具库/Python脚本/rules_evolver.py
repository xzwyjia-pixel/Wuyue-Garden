# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 规则自进化引擎
=========================================
读取 sentinel JSON → DeepSeek 分析公告 → 增量更新 rules.json
仅新增，不覆盖。保留手工规则。备份原文。
"""

import json
import copy
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import requests

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_RULES_PATH = Path(__file__).resolve().parent.parent.parent / "rules.json"
_API_KEY = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
_API_URL = "https://api.deepseek.com/v1/chat/completions"
_MODEL = "deepseek-chat"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ──────────────────────────────────────────────
# 发现最新哨兵报告
# ──────────────────────────────────────────────

def _find_latest_sentinel() -> Optional[Path]:
    files = sorted(_DATA_DIR.glob("sentinel_*.json"), reverse=True)
    if not files:
        print("[FAIL] 未找到 data/sentinel_*.json")
        return None
    print(f"[INPUT] {files[0].name}")
    return files[0]


# ──────────────────────────────────────────────
# 从哨兵 JSON 提取可分析文本
# ──────────────────────────────────────────────

def _extract_text_from_sentinel(data: dict) -> str:
    parts = []
    for t in data.get("targets", []):
        label = f"[{t['platform_name']}] {t['label']}"
        # 条目标题
        for a in t.get("articles", []):
            if a.get("title"):
                parts.append(f"{label} > {a['title']}")
        # 全文摘要
        excerpt = t.get("full_text_excerpt", "")
        if excerpt:
            parts.append(f"{label} > {excerpt}")
    return "\n".join(parts)


# ──────────────────────────────────────────────
# DeepSeek 分析：提取规则演变信号
# ──────────────────────────────────────────────

_ANALYSIS_PROMPT = """你是一位短视频平台合规分析专家，服务于「规则甄查 · 甄先生」品牌。
分析以下平台公告文本，提取三类内容：

1. 规则演变信号（正负双向）
2. 平台意图深度解读
3. 监管视角 + 反直觉避坑指南

## 规则
- 仅提取公告文本中明确体现的信号，不凭空推测
- 术语保持「静奢风」定位：极简、克制、精密
- 风险等级：HIGH（封号风险）/ MEDIUM（限流风险）/ LOW（优化建议）
- 激励等级：GREEN_HIGH（流量加权）/ GREEN_MEDIUM（信任资产）/ GREEN_LOW（蓝海机会）
- replace_suggestion 用 " / " 分隔多个选项
- 不输出已经在现有关键词列表中的词

## 输出格式（严格 JSON，不要任何其他文字）
{
  "new_risks": [],
  "new_incentives": [],
  "platform_intent": "",
  "regulatory_perspective": "",
  "counter_intuitive_guide": ""
}

每条 new_risk:
{"word": "风险词", "level": "HIGH", "category_hint": "类别", "risk_description": "原因", "replace_suggestion": "业内深耕 / 核心", "policy_ref": "政策依据"}

每条 new_incentive:
{"category": "类别名", "level": "GREEN_HIGH", "description": "描述", "indicators": ["指标1"], "platform_boost": "扶持信息", "policy_ref": ""}

字段说明（末尾三个）：
- platform_intent: 一句话概括"平台为什么出这条规则"，比如"打击虚假宣传，保护用户决策权"
- regulatory_perspective: 从监管层看这条规则的深层含义，比如"呼应《互联网广告管理办法》最新司法解释"
- counter_intuitive_guide: 一条最具代表性的反直觉避坑建议，直击创作者最容易踩的误区，比如"很多人以为替换违禁词就安全，但平台AI会检测语义等价词，需要整体重构句式而非简单替换"
"""


def _call_analysis_api(text: str) -> Optional[dict]:
    try:
        resp = requests.post(
            _API_URL,
            headers={"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": _ANALYSIS_PROMPT},
                    {"role": "user", "content": text},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()

        # 提取 JSON（兼容 markdown 包裹）
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(content)
    except Exception as e:
        print(f"[FAIL] API 调用/解析失败: {e}")
        return None


# ──────────────────────────────────────────────
# 增量合并 rules.json
# ──────────────────────────────────────────────

_RISK_LEVEL_MAP = {
    "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW",
}

_INCENTIVE_LEVEL_MAP = {
    "GREEN_HIGH": "GREEN_HIGH",
    "GREEN_MEDIUM": "GREEN_MEDIUM",
    "GREEN_LOW": "GREEN_LOW",
}


def _existing_risk_words(rules: dict) -> set:
    words = set()
    for level in ("HIGH", "MEDIUM", "LOW"):
        for word in rules.get("risk_levels", {}).get(level, {}).get("focus", {}):
            words.add(word)
    return words


def _existing_incentive_categories(rules: dict) -> set:
    cats = set()
    for level in ("GREEN_HIGH", "GREEN_MEDIUM", "GREEN_LOW"):
        for inc in rules.get("incentive_points", {}).get(level, []):
            if isinstance(inc, dict):
                cats.add(inc.get("category", ""))
    return cats


def _merge_risks(rules: dict, new_risks: list) -> dict:
    """增量合并风险词，不覆盖已有"""
    existing = _existing_risk_words(rules)
    added = 0
    for r in new_risks:
        word = r.get("word", "").strip()
        level = _RISK_LEVEL_MAP.get(r.get("level", ""))
        if not word or not level:
            continue
        if word in existing:
            continue
        rules.setdefault("risk_levels", {}).setdefault(level, {}).setdefault("focus", {})
        rules["risk_levels"][level]["focus"][word] = {
            "risk": r.get("risk_description", ""),
            "replace": r.get("replace_suggestion", ""),
            "policy_ref": r.get("policy_ref", ""),
        }
        # 保障 category / action 存在
        cat_hint = r.get("category_hint", "")
        if cat_hint and not rules["risk_levels"][level].get("category"):
            rules["risk_levels"][level]["category"] = cat_hint
        if not rules["risk_levels"][level].get("action"):
            actions = {"HIGH": "强制拦截", "MEDIUM": "建议修改", "LOW": "标注提醒"}
            rules["risk_levels"][level]["action"] = actions.get(level, "标注提醒")
        existing.add(word)
        added += 1
    print(f"  [ADD] 风险词: {added}")
    return rules


def _merge_incentives(rules: dict, new_incentives: list) -> dict:
    """增量合并激励点"""
    existing_cats = _existing_incentive_categories(rules)
    added = 0
    for inc in new_incentives:
        category = inc.get("category", "").strip()
        level = _INCENTIVE_LEVEL_MAP.get(inc.get("level", ""))
        if not category or not level:
            continue
        if category in existing_cats:
            continue
        rules.setdefault("incentive_points", {}).setdefault(level, [])
        # 检查列表中是否已存在（按 name 字段可能不同但 category 相同）
        exists = any(
            isinstance(x, dict) and x.get("category") == category
            for x in rules["incentive_points"][level]
        )
        if exists:
            continue
        entry = {
            "category": category,
            "description": inc.get("description", ""),
            "indicators": inc.get("indicators", []),
            "platform_boost": inc.get("platform_boost", ""),
            "policy_ref": inc.get("policy_ref", ""),
        }
        rules["incentive_points"][level].append(entry)
        existing_cats.add(category)
        added += 1
    print(f"  [ADD] 激励点: {added}")
    return rules


def _merge_content_engine(rules: dict, pi: str, rp: str, cig: str) -> dict:
    """存储平台意图 / 监管视角 / 反直觉避坑指南到 rules.json"""
    if not pi and not rp and not cig:
        return rules
    rules.setdefault("content_engine", {})
    if pi:
        rules["content_engine"]["platform_intent"] = pi
    if rp:
        rules["content_engine"]["regulatory_perspective"] = rp
    if cig:
        rules["content_engine"]["counter_intuitive_guide"] = cig
    rules["content_engine"]["updated_at"] = datetime.now().isoformat()
    return rules


def _bump_version(rules: dict):
    """微版本号递增"""
    v = rules.get("version", "2.0.0")
    parts = v.split(".")
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
    rules["version"] = ".".join(parts)


# ──────────────────────────────────────────────
# 备份规则文件
# ──────────────────────────────────────────────

def _backup_rules() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = _DATA_DIR / f"rules_backup_{ts}.json"
    backup.write_bytes(_RULES_PATH.read_bytes())
    print(f"[BACKUP] {backup.name}")
    return backup


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def evolve():
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 规则自进化")
    print("=" * 48)

    # 1. 找最新哨兵报告
    sentinel_path = _find_latest_sentinel()
    if not sentinel_path:
        return
    with open(sentinel_path, encoding="utf-8") as f:
        sentinel_data = json.load(f)

    # 2. 提取分析文本
    analysis_text = _extract_text_from_sentinel(sentinel_data)
    if not analysis_text.strip():
        print("[FAIL] 哨兵报告无可分析文本")
        return
    print(f"[TEXT] {len(analysis_text)} chars\n")

    # 3. 当前规则快照
    with open(_RULES_PATH, encoding="utf-8") as f:
        rules = json.load(f)
    existing_risks = _existing_risk_words(rules)
    existing_cats = _existing_incentive_categories(rules)
    print(f"[CURRENT] 风险词 {len(existing_risks)} 个, 激励类别 {len(existing_cats)} 个")

    # 4. 调用 API 分析
    print("[API] 分析中...")
    result = _call_analysis_api(analysis_text)
    if not result:
        print("[FAIL] 未获得分析结果，中止")
        return

    new_risks = result.get("new_risks", [])
    new_incentives = result.get("new_incentives", [])
    platform_intent = result.get("platform_intent", "")
    reg_perspective = result.get("regulatory_perspective", "")
    counter_intuitive = result.get("counter_intuitive_guide", "")
    print(f"[API] 解析到 风险信号 {len(new_risks)} 条, 政策信号 {len(new_incentives)} 条")
    if platform_intent:
        print(f"[API] 平台意图: {platform_intent[:60]}...")
    if reg_perspective:
        print(f"[API] 监管视角: {reg_perspective[:60]}...")
    if counter_intuitive:
        print(f"[API] 避坑指南: {counter_intuitive[:60]}...")

    if not new_risks and not new_incentives:
        print("[SAME] 无新增规则信号")
        return

    # 5. 增量合并
    rules = _merge_risks(rules, new_risks)
    rules = _merge_incentives(rules, new_incentives)
    rules = _merge_content_engine(rules, platform_intent, reg_perspective, counter_intuitive)

    # 6. 版本 + 时间戳
    _bump_version(rules)
    rules["updated_at"] = datetime.now().isoformat()

    # 7. 备份 → 写入
    _backup_rules()
    with open(_RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=4)
    print(f"[SAVE] {_RULES_PATH} (v{rules['version']})")

    # 8. 输出差异摘要
    print(f"\n{'─' * 48}")
    print("  DIFF")
    print(f"{'─' * 48}")
    for r in new_risks:
        w = r.get("word", "?")
        lv = r.get("level", "?")
        rep = r.get("replace_suggestion", "")[:20]
        print(f"  + [{lv}] {w} -> {rep}")
    for inc in new_incentives:
        cat = inc.get("category", "?")
        lv = inc.get("level", "?")
        print(f"  + [{lv}] {cat}")
    if platform_intent:
        print(f"\n  [意图] {platform_intent}")
    if reg_perspective:
        print(f"  [监管] {reg_perspective}")
    if counter_intuitive:
        print(f"  [避坑] {counter_intuitive[:80]}...")

    print(f"\n[DONE] v{rules['version']}")


if __name__ == "__main__":
    evolve()
