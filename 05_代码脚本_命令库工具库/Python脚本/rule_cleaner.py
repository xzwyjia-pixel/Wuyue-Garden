#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 规则库清理器
=========================================
DeepSeek 分析 rules.json → 识别相似/冲突规则 → 合并建议 → 增量清理。

保留静奢风术语，不改结构，不改人工标注。备份原文。
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
import yaml

_BASE_DIR = Path(__file__).resolve().parent.parent
_RULES_PATH = _BASE_DIR / "rules.json"
_DATA_DIR = _BASE_DIR / "data"
_CFG_PATH = _BASE_DIR / "config.yaml"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _load_cfg() -> dict:
    return yaml.safe_load(_CFG_PATH.read_text(encoding="utf-8")) if _CFG_PATH.exists() else {}


def _api_config() -> tuple:
    cfg = _load_cfg()
    api = cfg.get("api", {})
    return (
        api.get("deepseek_key", "sk-cad1b7bcd5dd4644a03c87c14a1fa690"),
        api.get("deepseek_url", "https://api.deepseek.com/v1/chat/completions"),
        api.get("deepseek_model", "deepseek-chat"),
    )


# ──────────────────────────────────────────────
# 从 rules.json 提取待分析数据
# ──────────────────────────────────────────────

def _extract_risk_words(rules: dict) -> list:
    """扁平化所有风险词"""
    items = []
    for level in ("HIGH", "MEDIUM", "LOW"):
        focus = rules.get("risk_levels", {}).get(level, {}).get("focus", {})
        for word, info in focus.items():
            items.append({
                "word": word,
                "level": level,
                "risk": info.get("risk", ""),
                "replace": info.get("replace", ""),
                "policy_ref": info.get("policy_ref", ""),
            })
    return items


def _extract_incentives(rules: dict) -> list:
    """扁平化所有激励类别"""
    items = []
    for level in ("GREEN_HIGH", "GREEN_MEDIUM", "GREEN_LOW"):
        entries = rules.get("incentive_points", {}).get(level, [])
        for e in entries:
            if isinstance(e, dict):
                items.append({
                    "category": e.get("category", ""),
                    "level": level,
                    "description": e.get("description", ""),
                    "indicators": e.get("indicators", []),
                })
    return items


# ──────────────────────────────────────────────
# DeepSeek 分析
# ──────────────────────────────────────────────

_CLEANER_PROMPT = """你是一位短视频平台合规规则库管理员，服务于「规则甄查 · 甄先生」品牌。

分析以下风险词列表，执行：
1. 合并语义相似的重复词（如"第一"和"第一名"应合并，保留更常用的）
2. 识别逻辑冲突：同一词出现在不同风险等级、或同一场景的替换建议相互矛盾
3. 标记可精简的冗余条目

## 约束
- 保持静奢风术语：极简、克制、精密
- 不得引入新词或新规则
- 合并时保留更严格（高等级）的规则
- 替换建议取交集，保留更精密的选项

## 输出格式（严格 JSON，不要其他文字）

{
  "merges": [
    {
      "keep": "保留的词",
      "remove": ["被合并的词1", "被合并的词2"],
      "target_level": "HIGH",
      "reason": "合并原因",
      "merged_replace": "合并后的替换建议",
      "merged_risk": "合并后的风险描述",
      "merged_policy_ref": "合并后的政策依据"
    }
  ],
  "conflicts": [
    {
      "word": "冲突词",
      "detail": "冲突描述",
      "suggestion": "解决建议"
    }
  ]
}

如果没有需要清理的项，返回 {"merges": [], "conflicts": []}"""


def _call_cleaner_api(risk_words: list, incentives: list) -> Optional[dict]:
    key, url, model = _api_config()

    payload = json.dumps({
        "risk_words": risk_words,
        "incentives": incentives,
    }, ensure_ascii=False, indent=2)

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _CLEANER_PROMPT},
                    {"role": "user", "content": payload},
                ],
                "temperature": 0.2,
                "max_tokens": 2048,
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()

        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(content)
    except Exception as e:
        print(f"[FAIL] API: {e}")
        return None


# ──────────────────────────────────────────────
# 应用清理
# ──────────────────────────────────────────────

def _apply_merges(rules: dict, merges: list) -> dict:
    """应用合并建议 — 删除被合并词，优化保留词"""
    for m in merges:
        keep = m.get("keep", "")
        remove_list = m.get("remove", [])
        target_level = m.get("target_level", "")

        if not keep or not remove_list:
            continue

        # 从规则中删除被合并的词
        for level in ("HIGH", "MEDIUM", "LOW"):
            focus = rules.get("risk_levels", {}).get(level, {}).get("focus", {})
            for w in remove_list:
                if w in focus:
                    del focus[w]
                    print(f"  [RM] {level}「{w}」→ 合并到「{keep}」")

        # 更新保留词的信息（若提供了合并后的内容且保留词存在）
        for level in ("HIGH", "MEDIUM", "LOW"):
            focus = rules.get("risk_levels", {}).get(level, {}).get("focus", {})
            if keep in focus and level == target_level:
                entry = focus[keep]
                if m.get("merged_replace"):
                    entry["replace"] = m["merged_replace"]
                if m.get("merged_risk"):
                    entry["risk"] = m["merged_risk"]
                if m.get("merged_policy_ref"):
                    entry["policy_ref"] = m["merged_policy_ref"]
                print(f"  [UPD] {level}「{keep}」已优化")

    return rules


def _resolve_conflicts(rules: dict, conflicts: list) -> dict:
    """根据 DeepSeek 建议解决冲突"""
    for c in conflicts:
        word = c.get("word", "")
        suggestion = c.get("suggestion", "")
        if not word:
            continue

        print(f"  [CONFLICT]「{word}」: {suggestion[:60]}...")

        # 简单冲突处理：若建议中指定了目標等级，将词移动到该等级
        import re
        level_match = re.search(r"(HIGH|MEDIUM|LOW)", suggestion)
        if level_match:
            target = level_match.group(1)
            # 从当前等级删除
            source_info = None
            for level in ("HIGH", "MEDIUM", "LOW"):
                focus = rules.get("risk_levels", {}).get(level, {}).get("focus", {})
                if word in focus:
                    if level != target:
                        source_info = focus.pop(word)
                        print(f"  [MOVE] {level} → {target}「{word}」")
            # 添加到目标等级
            if source_info and target:
                rules.setdefault("risk_levels", {}).setdefault(target, {}).setdefault("focus", {})
                if word not in rules["risk_levels"][target]["focus"]:
                    rules["risk_levels"][target]["focus"][word] = source_info

    return rules


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def clean():
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 规则库清理")
    print("=" * 48)

    # 1. 加载规则
    rules = json.loads(_RULES_PATH.read_text(encoding="utf-8"))
    risk_words = _extract_risk_words(rules)
    incentives = _extract_incentives(rules)
    print(f"[LOAD] 风险词 {len(risk_words)} 个, 激励 {len(incentives)} 条")

    if len(risk_words) < 2 and len(incentives) < 2:
        print("[SAME] 数据量过少，无需清理")
        return

    # 2. DeepSeek 分析
    print("[API] 分析中...")
    result = _call_cleaner_api(risk_words, incentives)
    if not result:
        print("[FAIL] 分析失败")
        return

    merges = [m for m in result.get("merges", []) if m.get("remove")]
    conflicts = result.get("conflicts", [])
    print(f"[ANALYSIS] 合并建议 {len(merges)} 条, 冲突 {len(conflicts)} 条")

    if not merges and not conflicts:
        print("[CLEAN] 规则库质量良好，无需清理")
        return

    # 3. 备份
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = _DATA_DIR / f"rules_backup_preclean_{ts}.json"
    backup.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[BACKUP] {backup.name}")

    # 4. 应用清理
    if merges:
        rules = _apply_merges(rules, merges)
    if conflicts:
        rules = _resolve_conflicts(rules, conflicts)

    # 5. 版本递增
    v = rules.get("version", "2.0.0")
    parts = v.split(".")
    parts[2] = str(int(parts[2]) + 1)
    rules["version"] = ".".join(parts)
    rules["cleaned_at"] = datetime.now().isoformat()

    # 6. 写回
    _RULES_PATH.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SAVE] {_RULES_PATH} (v{rules['version']})")

    # 7. 摘要
    new_count = _extract_risk_words(rules)
    print(f"\n{'─' * 48}")
    print("  CLEANUP REPORT")
    print(f"{'─' * 48}")
    for m in merges:
        print(f"  MERGE: «{m['keep']}» ← {', '.join(m['remove'])}")
        print(f"         {m.get('reason', '')[:60]}")
    for c in conflicts:
        print(f"  CONFLICT: «{c['word']}» → {c.get('suggestion', '')[:60]}")
    print(f"\n  BEFORE: {len(risk_words)}  →  AFTER: {len(new_count)} 风险词")
    print(f"[DONE] 清理完成")


if __name__ == "__main__":
    clean()
