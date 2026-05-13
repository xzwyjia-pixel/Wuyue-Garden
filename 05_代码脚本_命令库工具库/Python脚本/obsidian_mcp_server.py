# -*- coding: utf-8 -*-
"""
Obsidian Local REST API → MCP bridge
Connect Claude Code to Obsidian vault via obsidian-local-rest-api plugin.
Protocol: JSON-RPC 2.0 over stdio (same pattern as mcp_audit_server.py)

Usage:
  python core/obsidian_mcp_server.py
"""

import io
import json
import sys
import urllib.request
import urllib.error
import urllib.parse

# Windows GBK workaround — use sys.stdin.buffer in main() for UTF-8
if sys.stdout.encoding and sys.stdout.encoding.upper() not in ("UTF-8", "UTF8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── Config ──────────────────────────────────────────────────────────────
OBSIDIAN_PORT = 27123
API_KEY = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
BASE_URL = f"http://localhost:{OBSIDIAN_PORT}"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

WRITE_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "text/markdown",
}

# ── Obsidian REST helpers ───────────────────────────────────────────────

def _url(path):
    """Percent-encode path segments while preserving Obsidian API prefix."""
    parts = path.split("/")
    encoded = "/".join(urllib.parse.quote(p, safe="") for p in parts)
    return f"{BASE_URL}{encoded}"

def obsidian_get_json(path):
    req = urllib.request.Request(_url(path), headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def obsidian_get_text(path):
    req = urllib.request.Request(_url(path), headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")

def obsidian_post_vault(path, content):
    """POST raw markdown content to vault (create note)."""
    body = content.encode("utf-8")
    req = urllib.request.Request(_url(path), data=body, headers=WRITE_HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return {"status": resp.status}

def obsidian_put_vault(path, content):
    """PUT raw markdown content to vault (update note)."""
    body = content.encode("utf-8")
    req = urllib.request.Request(_url(path), data=body, headers=WRITE_HEADERS, method="PUT")
    with urllib.request.urlopen(req) as resp:
        return {"status": resp.status}

# ── Tool definitions ────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_notes",
        "description": "List all notes in current Obsidian vault. Returns file paths.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_note",
        "description": "Read content of a specific note by path (e.g., 'folder/note.md')",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Note path relative to vault root (e.g., 'Inbox/note.md')",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_notes",
        "description": "Search notes by keyword in filename and content",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "create_note",
        "description": "Create a new note. If path exists, returns error.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Note path (e.g., 'Inbox/new-note.md')"},
                "content": {"type": "string", "description": "Markdown content"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "update_note",
        "description": "Overwrite an existing note's content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Note path"},
                "content": {"type": "string", "description": "New markdown content"},
            },
            "required": ["path", "content"],
        },
    },
]

# ── Tool dispatcher ─────────────────────────────────────────────────────

def handle_call(name, args):
    if name == "list_notes":
        result = obsidian_get_json("/vault/")
        return {"files": result}

    elif name == "read_note":
        path = args["path"]
        content = obsidian_get_text(f"/vault/{path}")
        return {"content": content}

    elif name == "search_notes":
        query = args["query"]
        result = obsidian_get_json(f"/search?query={urllib.parse.quote(query)}")
        return {"results": result}

    elif name == "create_note":
        path = args["path"]
        content = args["content"]
        result = obsidian_post_vault(f"/vault/{path}", content)
        return result

    elif name == "update_note":
        path = args["path"]
        content = args["content"]
        result = obsidian_put_vault(f"/vault/{path}", content)
        return result

    else:
        raise ValueError(f"Unknown tool: {name}")

# ── JSON-RPC 2.0 over stdio ─────────────────────────────────────────────

def process_request(req):
    req_id = req.get("id")
    method = req.get("method", "")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "obsidian-mcp", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        try:
            result = handle_call(req["params"]["name"], req["params"].get("arguments", {}))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
            }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": e.code, "message": f"Obsidian API error: {err_body}"},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": repr(e)},
            }

    if method == "notifications/initialized":
        return None

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main():
    for raw in sys.stdin.buffer:
        line = raw.decode("utf-8").strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    main()
