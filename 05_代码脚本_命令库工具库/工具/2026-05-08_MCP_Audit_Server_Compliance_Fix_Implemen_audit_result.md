# MCP Audit Server Compliance Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `mcp_audit_server.py` 重构为符合 MCP JSON-RPC 2.0 规范的标准服务器，支持 Claude Desktop / Claude Code 直接调用。

**Architecture:** 当前脚本仅模拟 MCP（`sys.argv` 入参，无协议层）。需实现 stdio 传输层（stdin/stdout JSON-RPC）、`tools/list` 与 `tools/call` 方法、以及结构化 `inputSchema`。`rules.json` 保持不变，审计逻辑复用。

**Tech Stack:** Python 3.10+, `json`, `sys` (stdio transport), MCP JSON-RPC 2.0 spec

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `mcp_audit_server.py` | 修改 | MCP stdio 服务器（协议层 + 工具注册） |
| `audit_core.py` | 新建 | 纯审计逻辑（从 mcp_audit_server 中提取） |
| `tests/test_audit_core.py` | 新建 | 审计逻辑单元测试 |
| `tests/test_mcp_protocol.py` | 新建 | MCP 协议层集成测试 |

---

### Task 1: 提取审计核心逻辑到独立模块

**Files:**
- Create: `audit_core.py`
- Create: `tests/test_audit_core.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_audit_core.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from audit_core import audit_text

def test_high_risk_word_detected():
    result = audit_text("这是最好的产品")
    assert result["is_safe"] is False
    risks = [r["word"] for r in result["risks"]]
    assert "最" in risks

def test_safe_text_passes():
    result = audit_text("今天天气不错")
    assert result["is_safe"] is True
    assert result["risks"] == []

def test_refined_content_replaces_word():
    result = audit_text("我们是第一")
    assert "第一" not in result["refined_content"]
    assert "业内深耕" in result["refined_content"] or "追求极致" in result["refined_content"]

def test_medium_risk_detected():
    result = audit_text("点击链接领取奖励")
    levels = [r["level"] for r in result["risks"]]
    assert "MEDIUM" in levels
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd E:/MyCodeProjects
python -m pytest tests/test_audit_core.py -v
```

期望输出：`ImportError: No module named 'audit_core'`

- [ ] **Step 3: 创建 `audit_core.py`**

```python
import json
import re
from pathlib import Path

_RULES_PATH = Path(__file__).parent / "rules.json"

def _load_rules() -> dict:
    with open(_RULES_PATH, encoding="utf-8") as f:
        return json.load(f)

def audit_text(text: str) -> dict:
    """
    返回:
      is_safe: bool
      risks: list[{level, word, advice}]
      refined_content: str
    """
    rules = _load_rules()
    risk_found = []
    refined = text

    for level, details in rules.get("risk_levels", {}).items():
        for word, advice in details.get("focus", {}).items():
            if word in text:
                risk_found.append({"level": level, "word": word, "advice": advice})
                match = re.search(r"“(.+?)”", advice)
                if match:
                    refined = refined.replace(word, match.group(1))

    return {
        "is_safe": len(risk_found) == 0,
        "risks": risk_found,
        "refined_content": refined,
    }
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_audit_core.py -v
```

期望：4 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add audit_core.py tests/test_audit_core.py
git commit -m "feat: extract audit logic into audit_core module"
```

---

### Task 2: 实现 MCP JSON-RPC 2.0 协议层

**Files:**
- Modify: `mcp_audit_server.py`
- Create: `tests/test_mcp_protocol.py`

**背景知识 — MCP stdio 协议：**
Claude Desktop 通过 stdin 发送 JSON-RPC 请求，服务器从 stdout 返回 JSON-RPC 响应，每条消息以 `\n` 分隔。必须支持三个方法：
- `initialize` — 握手，返回服务器能力声明
- `tools/list` — 返回工具列表（含 `inputSchema`）
- `tools/call` — 执行工具，返回 `content` 数组

- [ ] **Step 1: 写协议层测试**

```python
# tests/test_mcp_protocol.py
import json, subprocess, sys

SERVER = [sys.executable, "mcp_audit_server.py"]

def rpc(method, params=None, id=1):
    msg = json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})
    result = subprocess.run(
        SERVER,
        input=msg + "\n",
        capture_output=True, text=True,
        cwd="E:/MyCodeProjects"
    )
    return json.loads(result.stdout.strip())

def test_initialize():
    resp = rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}})
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert "tools" in resp["result"]["capabilities"]

def test_tools_list():
    resp = rpc("tools/list")
    tools = resp["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "audit_content" in names
    schema = next(t for t in tools if t["name"] == "audit_content")["inputSchema"]
    assert "text" in schema["properties"]

def test_tools_call_unsafe():
    resp = rpc("tools/call", {"name": "audit_content", "arguments": {"text": "绝对第一"}})
    content = resp["result"]["content"][0]["text"]
    data = json.loads(content)
    assert data["is_safe"] is False

def test_tools_call_safe():
    resp = rpc("tools/call", {"name": "audit_content", "arguments": {"text": "今天分享技巧"}})
    content = resp["result"]["content"][0]["text"]
    data = json.loads(content)
    assert data["is_safe"] is True

def test_unknown_method_returns_error():
    resp = rpc("unknown/method")
    assert "error" in resp
    assert resp["error"]["code"] == -32601
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_mcp_protocol.py -v
```

期望：所有测试失败（服务器无协议响应）

- [ ] **Step 3: 重写 `mcp_audit_server.py`**

```python
import json
import sys
from audit_core import audit_text

SERVER_INFO = {
    "name": "zhen-audit-server",
    "version": "1.0.0",
}

TOOLS = [
    {
        "name": "audit_content",
        "description": "审计短视频文案，检测违禁词与营销诱导词，返回风险列表与合规改写建议。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "待审计的文案内容",
                }
            },
            "required": ["text"],
        },
    }
]


def handle(request: dict) -> dict:
    method = request.get("method", "")
    rid = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
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
        if name == "audit_content":
            result = audit_text(args.get("text", ""))
            return {
                "jsonrpc": "2.0",
                "id": rid,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "error": {"code": -32602, "message": f"Unknown tool: {name}"},
        }

    return {
        "jsonrpc": "2.0",
        "id": rid,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }) + "\n")
            sys.stdout.flush()
            continue
        response = handle(request)
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_mcp_protocol.py -v
```

期望：5 tests PASSED

- [ ] **Step 5: 全量测试**

```bash
python -m pytest tests/ -v
```

期望：9 tests PASSED（4 core + 5 protocol）

- [ ] **Step 6: Commit**

```bash
git add mcp_audit_server.py tests/test_mcp_protocol.py
git commit -m "feat: implement MCP JSON-RPC 2.0 stdio protocol in audit server"
```

---

### Task 3: Claude Desktop 集成配置

**Files:**
- Create: `docs/mcp-config.md`

- [ ] **Step 1: 创建集成配置文档**

```markdown
# Claude Desktop MCP 集成配置

将以下配置加入 Claude Desktop 的 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "zhen-audit": {
      "command": "python",
      "args": ["E:/MyCodeProjects/mcp_audit_server.py"]
    }
  }
}
```

配置路径（Windows）：`%APPDATA%\Claude\claude_desktop_config.json`

重启 Claude Desktop 后，在对话中可直接调用：
> "帮我审计这段文案：[文案内容]"
```

- [ ] **Step 2: Commit**

```bash
git add docs/mcp-config.md
git commit -m "docs: add Claude Desktop MCP integration config"
```

---

## Self-Review

**Spec 覆盖检查：**
- ✅ `rules.json` 结构兼容性 — Task 1 中 `audit_core.py` 直接读取，无需改动 rules.json
- ✅ MCP 协议合规 — Task 2 实现 `initialize` / `tools/list` / `tools/call` 三个必需方法
- ✅ inputSchema 声明 — Task 2 `TOOLS` 定义中包含完整 JSON Schema
- ✅ 错误处理 — 未知方法返回 -32601，未知工具返回 -32602，解析错误返回 -32700
- ✅ Claude Desktop 集成 — Task 3

**Placeholder 扫描：** 无 TBD / TODO / "类似 Task N" 表述。

**类型一致性：** `audit_text()` 在 Task 1 定义，Task 2 中 `from audit_core import audit_text` 调用，签名一致。
