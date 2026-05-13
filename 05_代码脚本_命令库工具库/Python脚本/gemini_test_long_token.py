"""
Test: MaZiqc with larger batch sizes and extract long tokens.
"""
import asyncio, json, urllib.parse, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

def parse_batch(body: str) -> list:
    body = re.sub(r"^\)\]}'\n?", "", body)
    chunks = []
    pos = 0
    while pos < len(body):
        m = re.match(r'\n(\d+)\n', body[pos:])
        if not m:
            break
        size = int(m.group(1))
        jstart = pos + m.end()
        jend = jstart + size
        try:
            chunks.append(json.loads(body[jstart:jend]))
        except json.JSONDecodeError:
            break
        pos = jend
    return chunks

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(3)

        body = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            print("[等待] 登录...")
            for _ in range(180):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt:
                    break

        # Get at token
        print("[获取] at token...")
        at_token = None
        future = asyncio.get_event_loop().create_future()
        async def on_req(req):
            if future.done(): return
            if "/batchexecute" in req.url:
                pd = req.post_data
                if isinstance(pd, str) and "at=" in pd:
                    parsed = urllib.parse.parse_qs(pd)
                    if "at" in parsed and parsed["at"][0]:
                        future.set_result(parsed["at"][0])
        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(5)
        try:
            at_token = await asyncio.wait_for(future, timeout=10)
        except asyncio.TimeoutError:
            print("[FAIL] no at")
            return
        finally:
            page.remove_listener("request", on_req)
        print(f"  at: {at_token[:40]}...")

        # Test different MaZiqc params
        tests = [
            ("列表 [13]", [13, null, [0, null, 50]]),
            ("列表 [13] no limit", [13, null, [0, null, null]]),
            ("列表 [13] custom", [13, null, [0, "0", 50]]),
            ("加载 hNvQHb (test short token)", None),  # special case
        ]

        for label, params in tests:
            if params is None:
                continue

            print(f"\n[测试] MaZiqc {label}")
            rpc_params = json.dumps(params)
            rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
            body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

            result = await page.evaluate("""async (url, body) => {
                try {
                    const resp = await fetch(url + '?rpcids=MaZiqc&source-path=%2Fapp&hl=zh-CN&rt=c', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                        body: body,
                    });
                    return { ok: resp.ok, status: resp.status, text: await resp.text() };
                } catch (e) {
                    return { ok: false, error: e.message };
                }
            }""", [BATEXECUTE, body_str])

            if result.get("ok") and result.get("text"):
                chunks = parse_batch(result["text"])
                if chunks:
                    # Parse the inner JSON from the wrb.fr format
                    inner = chunks[0]
                    if isinstance(inner, list) and len(inner) > 0 and isinstance(inner[0], list):
                        # wrb.fr format: [RPCID, data_string, ...]
                        data_str = inner[0][2] if len(inner[0]) > 2 else None
                        if isinstance(data_str, str):
                            try:
                                data = json.loads(data_str)
                                # data = [null, null/long_token, [[conv1], ...]]
                                if isinstance(data, list) and len(data) >= 3:
                                    convs = data[2] if isinstance(data[2], list) else []
                                    long_token = data[1] if isinstance(data[1], str) and len(data[1]) > 20 else None
                                    print(f"  → {len(convs)} 条对话, 长token: {'有' if long_token else '无'}")
                                    for j, c in enumerate(convs[:5]):
                                        if isinstance(c, list) and len(c) >= 2:
                                            print(f"    {j+1}. {c[0][:30]:30s} {str(c[1])[:50]}")
                                    if len(convs) > 5:
                                        print(f"    ... ({len(convs)-5} 更多)")
                            except json.JSONDecodeError as e:
                                print(f"  parse failed: {e}")
            else:
                print(f"  error: {result.get('status', '?')}")

        # ── Now try to get long tokens from hNvQHb ──
        print(f"\n\n[测试] 从 hNvQHb 提取长 token")
        print("  先发送 MaZiqc list 获取一个 conversation ID...")

        # Get a short token first
        rpc_list = json.dumps([13, None, [0, None, 1]])
        rpc_call = json.dumps([["MaZiqc", rpc_list, None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"
        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url + '?rpcids=MaZiqc&source-path=%2Fapp&hl=zh-CN&rt=c', {
                    method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body,
                });
                return { ok: resp.ok, status: resp.status, text: await resp.text() };
            } catch (e) { return { ok: false, error: e.message }; }
        }""", [BATEXECUTE, body_str])

        conv_id = None
        if result.get("ok"):
            chunks = parse_batch(result["text"])
            if chunks:
                inner = chunks[0][0] if len(chunks[0][0]) > 2 else None
                if inner:
                    d = json.loads(inner[2])
                    if len(d) >= 3 and d[2]:
                        conv_id = d[2][0][0]

        if conv_id:
            print(f"  conv_id: {conv_id}")
            print(f"  发送 hNvQHb 请求...")

            # Send hNvQHb to load the conversation
            rpc_h = json.dumps([null, null, [null, null, null, null, null, null, [1, 2]]])

            # Actually hNvQHb params might be different. Let me try:
            rpc_h = json.dumps([None, None])
            rpc_call = json.dumps([["hNvQHb", rpc_h, None, "generic"]])
            body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"
            source_path = f"/app/{conv_id}"

            result_h = await page.evaluate("""async (url, body) => {
                try {
                    const resp = await fetch(url + '?rpcids=hNvQHb&source-path=%2Fapp&hl=zh-CN&rt=c', {
                        method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                        body: body,
                    });
                    return { ok: resp.ok, status: resp.status, text: await resp.text() };
                } catch (e) { return { ok: false, error: e.message }; }
            }""", [BATEXECUTE, body_str])

            if result_h.get("ok"):
                resp_text = result_h["text"]
                print(f"  hNvQHb response: {len(resp_text)} bytes")
                # Parse and search for long token pattern
                chunks = parse_batch(resp_text)
                if chunks:
                    # Stringify the whole response and search for base64-like tokens
                    full = json.dumps(chunks, ensure_ascii=False)
                    # Look for long token patterns (tCs0, tCuQ, etc.)
                    long_tokens = re.findall(r'[a-zA-Z0-9+/]{50,}={0,2}', full)
                    print(f"  找到 {len(long_tokens)} 个 base64 长字符串:")
                    for t in long_tokens[:10]:
                        print(f"    {t[:60]}...")
            else:
                print(f"  error: {result_h.get('status', '?')}")
        else:
            print("  [WARN] no conv_id found")

        await browser.close()

# Handle None/null properly
null = None

if __name__ == "__main__":
    asyncio.run(main())
