# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — MCP JSON-RPC 2.0 服务器
=================================================
协议：JSON-RPC 2.0 over stdio
工具：
  - audit_content    (v1.0 兼容) 单文案风险审计
  - audit_dual       (v2.0 核心) 红绿灯双向导航审计
  - policy_check     (v2.0 新增) 政策契合度专项评估
"""

import io
import json
import os
import sys
import traceback
from audit_core import audit_text, audit_dual, evaluate_policy_fitness, _load_rules

# Windows GBK stdout workaround — emoji in tool descriptions crash JSON-RPC
if sys.stdout.encoding and sys.stdout.encoding.upper() not in ("UTF-8", "UTF8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="surrogatepass")

def _clean_surrogates(obj):
    """Strip surrogate chars from JSON-serializable objects (Windows fix)."""
    if isinstance(obj, str):
        return obj.encode("utf-8", errors="surrogatepass").decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {k: _clean_surrogates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_surrogates(v) for v in obj]
    return obj

SERVER_INFO = {"name": "zhen-audit-server", "version": "2.0.0"}

TOOLS = [
    {
        "name": "audit_content",
        "description": "【v1.0 兼容】审计短视频文案，检测违禁词与营销诱导词，返回风险列表与合规改写建议。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待审计的文案内容"}
            },
            "required": ["text"],
        },
    },
    {
        "name": "audit_dual",
        "description": "【v2.0 核心】红绿灯双向导航审计。同时输出：🔴红灯风险点、🟢绿灯激励点、📊政策契合度评分、💡优化建议。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待审计的文案内容"}
            },
            "required": ["text"],
        },
    },
    {
        "name": "policy_check",
        "description": "【v2.0 专项】政策契合度评估。从原创度、真实性、价值性、合规性四个维度评分，判断内容与2026平台政策的契合程度。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待评估的文案内容"}
            },
            "required": ["text"],
        },
    },
]


def _make_result(data: dict) -> dict:
    """统一封装 MCP 结果"""
    return {
        "content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]
    }


def _make_error(code: int, message: str) -> dict:
    return {"code": code, "message": message}


def handle(request: dict) -> dict:
    method = request.get("method", "")
    rid = request.get("id")

    # ── 初始化 ──
    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }

    # ── 列出工具 ──
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    # ── 调用工具 ──
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})

        try:
            if name == "audit_content":
                result = audit_text(args.get("text", ""))
                return {"jsonrpc": "2.0", "id": rid, "result": _make_result(result)}

            elif name == "audit_dual":
                result = audit_dual(args.get("text", ""))
                return {"jsonrpc": "2.0", "id": rid, "result": _make_result(result)}

            elif name == "policy_check":
                text = args.get("text", "")
                rules = _load_rules()
                result = evaluate_policy_fitness(text, rules)
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

    # ── 未知方法 ──
    return {
        "jsonrpc": "2.0", "id": rid,
        "error": _make_error(-32601, f"Method not found: {method}"),
    }


def main():
    """MCP 服务器主循环：stdin/stdout JSON-RPC 2.0 协议"""
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
        sys.stdout.write(json.dumps(_clean_surrogates(response), ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
