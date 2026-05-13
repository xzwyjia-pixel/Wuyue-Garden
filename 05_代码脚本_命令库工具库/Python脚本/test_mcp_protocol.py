import json, subprocess, sys

SERVER = [sys.executable, "core/mcp_audit_server.py"]

def rpc(method, params=None, id=1):
    msg = json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})
    result = subprocess.run(
        SERVER,
        input=msg + "\n",
        capture_output=True, text=True, encoding="utf-8",
        cwd="E:/MyCodeProjects/01-Production/规则甄查系统"
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
