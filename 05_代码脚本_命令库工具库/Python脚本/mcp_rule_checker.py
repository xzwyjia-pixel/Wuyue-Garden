# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — Rule Investigator MCP Server
======================================================
协议：JSON-RPC 2.0 over stdio
工具：
  - investigate_text   深度规则调查：追溯每条匹配规则的政策依据、替换建议、风险量化
  - rule_stats         规则库统计：数量分布、分类覆盖度、政策关联度总览
"""

import io
import json
import sys
import traceback
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent  # 03_Internal_Tools → project root
_RULES_PATH = _BASE_DIR / "rules.json"

if sys.stdout.encoding and sys.stdout.encoding.upper() not in ("UTF-8", "UTF8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SERVER_INFO = {"name": "rule-investigator", "version": "1.0.0"}

_RULES_CACHE = None


def _load_rules() -> dict:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        with open(_RULES_PATH, encoding="utf-8") as f:
            _RULES_CACHE = json.load(f)
    return _RULES_CACHE


TOOLS = [
    {
        "name": "investigate_text",
        "description": "深度规则调查。逐条匹配文案与规则库，追溯每条匹配的政策依据、替换路径、风险量化评分与推荐动作。适用于需要理解「为什么这条规则匹配」的场景。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待调查的文案内容"}
            },
            "required": ["text"],
        },
    },
    {
        "name": "rule_stats",
        "description": "规则库统计概览。返回各风险级别规则数量、分类覆盖度、激励点分布、政策契合度评估维度等结构化统计。无需参数。",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def _make_result(data: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]
    }


def _make_error(code: int, message: str) -> dict:
    return {"code": code, "message": message}


def _investigate_text(text: str) -> dict:
    """深度规则调查：不仅输出匹配，还追溯每条规则的政策关联和替代路径"""
    rules = _load_rules()
    findings = []

    for level, details in rules.get("risk_levels", {}).items():
        focus = details.get("focus", {})
        category = details.get("category", "")
        action = details.get("action", "")

        for word, info in focus.items():
            if word in text:
                findings.append({
                    "matched_word": word,
                    "level": level,
                    "category": category,
                    "risk_description": info.get("risk", ""),
                    "replace_suggestion": info.get("replace", ""),
                    "policy_ref": info.get("policy_ref", ""),
                    "action": action,
                    "severity_score": {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(level, 0),
                })

    total_severity = sum(f["severity_score"] for f in findings)
    risk_count = len(findings)

    if risk_count == 0:
        verdict = "PASS"
        summary = "未检测到规则匹配，文案安全。"
    elif total_severity >= 5:
        verdict = "REVIEW_REQUIRED"
        summary = f"检测到 {risk_count} 条匹配（严重度 {total_severity}），建议修改后发布。"
    else:
        verdict = "MINOR_ISSUES"
        summary = f"检测到 {risk_count} 条低严重度匹配，可选择性优化。"

    return {
        "verdict": verdict,
        "summary": summary,
        "findings_count": risk_count,
        "severity_total": total_severity,
        "findings": findings,
        "policy_refs": sorted(set(
            f.get("policy_ref", "") for f in findings if f.get("policy_ref")
        )),
    }


def _rule_stats() -> dict:
    """规则库统计：数量分布、分类覆盖度"""
    rules = _load_rules()

    risk_levels = rules.get("risk_levels", {})
    total_rules = 0
    level_stats = {}
    for level, details in risk_levels.items():
        focus = details.get("focus", {})
        count = len(focus)
        total_rules += count
        level_stats[level] = {
            "count": count,
            "category": details.get("category", ""),
            "sample_words": list(focus.keys())[:5],
        }

    incentives = rules.get("incentive_points", {})
    incentive_stats = {}
    for level, details in incentives.items():
        indicators = details.get("indicators", [])
        incentive_stats[level] = {
            "count": len(indicators),
            "category": details.get("category", ""),
            "sample_indicators": indicators[:3],
        }

    fitness = rules.get("policy_fitness", {})
    dims = fitness.get("dimensions", [])

    return {
        "brand": rules.get("brand", ""),
        "tagline": rules.get("tagline", ""),
        "total_risk_rules": total_rules,
        "risk_level_distribution": level_stats,
        "incentive_point_distribution": incentive_stats,
        "policy_fitness_dimensions": [
            {"name": d["name"], "weight": d["weight"], "description": d["description"]}
            for d in dims
        ],
    }


def handle(request: dict) -> dict:
    method = request.get("method", "")
    rid = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})

        try:
            if name == "investigate_text":
                result = _investigate_text(args.get("text", ""))
                return {"jsonrpc": "2.0", "id": rid, "result": _make_result(result)}

            elif name == "rule_stats":
                result = _rule_stats()
                return {"jsonrpc": "2.0", "id": rid, "result": _make_result(result)}

            else:
                return {
                    "jsonrpc": "2.0", "id": rid,
                    "error": _make_error(-32602, f"Unknown tool: {name}"),
                }

        except Exception as e:
            tb = traceback.format_exc()
            return {
                "jsonrpc": "2.0", "id": rid,
                "error": _make_error(-32603, f"{e}\n{tb}"),
            }

    return {
        "jsonrpc": "2.0", "id": rid,
        "error": _make_error(-32601, f"Method not found: {method}"),
    }


def main():
    """MCP 服务器主循环：stdin/stdout JSON-RPC 2.0"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(
                json.dumps({
                    "jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }, ensure_ascii=False) + "\n"
            )
            sys.stdout.flush()
            continue

        response = handle(request)
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
