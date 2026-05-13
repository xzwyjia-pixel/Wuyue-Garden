"""
Gemini 对话列表 RPC 发现工具

用法:
  # 终端 1: Chrome CDP (已登录 Gemini)
  powershell -File start_chrome_cdp.ps1

  # 终端 2: 运行发现
  python gemini_discover_rpc.py

说明:
  - 连接到 Chrome CDP → 打开 Gemini
  - 捕获所有 batchexecute 响应 60 秒
  - 用户可滚动侧边栏加载更多对话
  - 保存到 gemini_rpc_capture.json
  - 自动尝试识别对话列表 RPC
"""

import asyncio, sys, json, re, urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

CDP_PORT = 9229
GEMINI_URL = "https://gemini.google.com/app"
SCRIPT_DIR = Path(__file__).resolve().parent

CAPTURE_TIME = 60  # seconds to listen


def strip_wrapper(body: str) -> str:
    return re.sub(r"^\)\]}'\n?", "", body)


def looks_like_title(s: str) -> bool:
    if not isinstance(s, str) or len(s) < 3 or len(s) > 200:
        return False
    if re.match(r'^[\d\s,.%+\-/\\]+$', s):
        return False
    if re.match(r'^https?://', s):
        return False
    if re.match(r'^[{\[\"\']', s):
        return False
    if not re.search(r'[一-鿿\w]', s):
        return False
    return True


def scan_for_conversations(body: str, min_count=3):
    """Extract (token, title) from batchexecute response."""
    cleaned = strip_wrapper(body)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    candidates = []

    def walk(obj, path=""):
        if isinstance(obj, list):
            for idx, item in enumerate(obj):
                if isinstance(item, dict):
                    token = (item.get("conversationToken") or item.get("token")
                             or item.get("id") or item.get("conversationId"))
                    title = (item.get("title") or item.get("displayName")
                             or item.get("name"))
                    if token and title and looks_like_title(str(title)):
                        candidates.append((str(token), str(title), 0.8))
                elif isinstance(item, list) and len(item) >= 2:
                    first, second = str(item[0]), str(item[1])
                    if len(first) > 30 and looks_like_title(second):
                        candidates.append((first, second, 0.7))
                walk(item, f"{path}[{idx}]")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")

    walk(data)
    return candidates if len(candidates) >= min_count else None


async def main():
    async with async_playwright() as p:
        print(f"[连接] CDP Chrome ({CDP_PORT})...")
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto(GEMINI_URL, timeout=30000)
            await asyncio.sleep(3)

        # Login wait
        body_text = await page.inner_text("body")
        if "登录" in body_text or "Sign in" in body_text:
            print("[等待] 登录 Gemini...")
            for _ in range(180):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt:
                    break

        # ── Capture ──────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"开始捕获 batchexecute 响应 ({CAPTURE_TIME}s)")
        print("请在浏览器中操作:")
        print("  1. 确保侧边栏已展开")
        print("  2. 滚动侧边栏加载更多对话")
        print("  3. (可选) 右键点击某对话 → 重命名 → 观察请求")
        print(f"{'='*60}")

        captured = {}  # rpcid -> {count, samples: [{body, url}]}
        at_token = None
        found_conversations = None

        async def on_response(resp):
            nonlocal at_token, found_conversations
            url = resp.url
            if "/batchexecute" not in url:
                return

            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            rpcids = qs.get("rpcids", [])

            if not at_token and "at" in qs:
                at_token = qs["at"][0]

            try:
                body = await resp.text()
            except:
                return

            for rpcid in rpcids:
                if rpcid not in captured:
                    captured[rpcid] = {"count": 0, "samples": [], "urls": set()}
                captured[rpcid]["count"] += 1
                captured[rpcid]["urls"].add(url[:150])
                if len(captured[rpcid]["samples"]) < 2:
                    captured[rpcid]["samples"].append(body[:2000])

            # Auto-detect conversation list
            if rpcids and not found_conversations:
                convs = scan_for_conversations(body, min_count=3)
                if convs:
                    found_conversations = {
                        "rpcids": rpcids,
                        "count": len(convs),
                        "samples": convs[:5],
                    }

        page.on("response", on_response)

        # Already-loaded: wait for async operations
        await asyncio.sleep(CAPTURE_TIME)

        # ── Report ───────────────────────────────────────
        print(f"\n{'='*60}")
        print("捕获结果")
        print(f"{'='*60}")
        print(f"\nat_token: {at_token[:30] if at_token else 'NOT FOUND'}...")

        print(f"\n发现 {len(captured)} 个 RPCID:")
        for rpcid, info in sorted(captured.items()):
            print(f"\n  {rpcid} ({info['count']} 次)")
            for sample_body in info["samples"]:
                preview = strip_wrapper(sample_body)[:200].replace('\n', ' ').strip()
                print(f"    响应: {preview[:150]}")

        if found_conversations:
            print(f"\n{'='*60}")
            print(f"[!!!] 识别到对话列表 RPC: {found_conversations['rpcids']}")
            print(f"      共 {found_conversations['count']} 条对话")
            print(f"{'='*60}")
            for token, title, conf in found_conversations["samples"]:
                print(f"  {title[:50]:50s} (token: {token[:25]}...)")
        else:
            print(f"\n{'='*60}")
            print("未识别到对话列表 RPC")
            print("请检查捕获数据, 手动识别包含对话列表的 RPC")
            print(f"{'='*60}")

        # ── Save ─────────────────────────────────────────
        out = {
            "at_token": at_token,
            "found_conversations": found_conversations,
            "rpcs": {
                rpcid: {
                    "count": info["count"],
                    "samples": info["samples"],
                    "urls": list(info["urls"]),
                }
                for rpcid, info in captured.items()
            },
        }

        out_path = SCRIPT_DIR / "gemini_rpc_capture.json"
        json.dump(out, open(out_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"\n已保存: {out_path}")

        # ── Sidebar dump ─────────────────────────────────
        print("\n侧边栏对话链接:")
        sidebar = await page.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="/app/"]');
            const items = [];
            const seen = new Set();
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const text = a.textContent?.trim() || '';
                const m = href.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && text.length > 1) {
                    seen.add(m[1]);
                    items.push({ convId: m[1], title: text.substring(0, 100) });
                }
            }
            return items;
        }""")
        print(f"  共 {len(sidebar)} 个可见对话")
        for item in sidebar[:20]:
            print(f"    {item['convId'][:25]:25s} {item['title'][:50]}")
        if len(sidebar) > 20:
            print(f"    ... ({len(sidebar) - 20} 更多)")

        # Count with/without prefix
        with_prefix = sum(1 for s in sidebar
                          if any(s['title'].startswith(p) for p in
                                 ["[DEV]", "[AUD]", "[CPY]", "[OPS]", "[PJM]",
                                  "[DAT]", "[LIV]", "[MCP]", "[OBS]", "[OTH]"]))
        print(f"  已有前缀: {with_prefix}, 未加: {len(sidebar) - with_prefix}")


if __name__ == "__main__":
    asyncio.run(main())
