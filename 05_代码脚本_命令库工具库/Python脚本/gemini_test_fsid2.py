"""
Test: MaZiqc list call with proper f.sid.
"""
import asyncio, json, urllib.parse, re
from playwright.async_api import async_playwright

def parse_batch(body: str) -> list:
    body = re.sub(r"^\)\]}'\n?", "", body)
    chunks = []
    pos = 0
    while pos < len(body):
        m = re.match(r'\n(\d+)\n', body[pos:])
        if not m: break
        size = int(m.group(1))
        jstart = pos + m.end()
        jend = jstart + size
        try:
            chunks.append(json.loads(body[jstart:jend]))
        except json.JSONDecodeError:
            break
        pos = jend
    return chunks

BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9229")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Capture one batchexecute request to get f.sid
        url_data = {}
        async def on_req(req):
            if "/batchexecute" in req.url and "url_data" not in url_data:
                url_data["url"] = req.url
                pd = req.post_data
                if isinstance(pd, str) and "at=" in pd:
                    parsed = urllib.parse.parse_qs(pd)
                    if "at" in parsed:
                        url_data["at"] = parsed["at"][0]

        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(8)
        page.remove_listener("request", on_req)

        if "at" not in url_data:
            print("[FAIL] no at token")
            return

        at_token = url_data["at"]
        batch_url = url_data.get("url", "")

        # Parse f.sid from captured URL
        parsed = urllib.parse.urlparse(batch_url)
        qs = urllib.parse.parse_qs(parsed.query)
        fsid = qs.get("f.sid", [""])[0]
        bl = qs.get("bl", [""])[0]
        print(f"f.sid: {fsid}")
        print(f"bl: {bl}")
        print(f"at: {at_token[:40]}...")

        # Build correct URL
        base_params = {
            "rpcids": "MaZiqc",
            "source-path": "/app",
            "bl": bl,
            "f.sid": fsid,
            "hl": "zh-CN",
            "rt": "c",
        }
        qs_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in base_params.items())

        # Test 1: MAZIQC LIST (pinned)
        print(f"\n[测试 1] MaZiqc list pinned [13,null,[1,null,1]]")
        rpc_call = json.dumps([["MaZiqc", "[13,null,[1,null,1]]", None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{qs_str}", body_str])

        if result.get("ok") and result.get("text"):
            chunks = parse_batch(result["text"])
            if chunks and len(chunks[0]) > 0 and len(chunks[0][0]) > 2:
                inner = json.loads(chunks[0][0][2])
                convs = inner[2] if len(inner) > 2 else []
                print(f"  → {len(convs)} 对话")
                for c in convs[:5]:
                    if isinstance(c, list) and len(c) >= 2:
                        print(f"    {c[0][:30]:30s} {str(c[1])[:60]}")
        else:
            print(f"  error: {result.get('status', '?')}")

        # Test 2: MAZIQC LIST (recent) - get more at once
        print(f"\n[测试 2] MaZiqc list recent [13,null,[0,null,50]]")
        rpc_call = json.dumps([["MaZiqc", "[13,null,[0,null,50]]", None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{qs_str}", body_str])

        if result.get("ok") and result.get("text"):
            chunks = parse_batch(result["text"])
            if chunks and len(chunks[0]) > 0 and len(chunks[0][0]) > 2:
                inner = json.loads(chunks[0][0][2])
                convs = inner[2] if len(inner) > 2 else []
                print(f"  → {len(convs)} 对话")
                for c in convs[:10]:
                    if isinstance(c, list) and len(c) >= 2:
                        print(f"    {c[0][:30]:30s} {str(c[1])[:60]}")
        else:
            print(f"  error: {result.get('status', '?')}")

        # Test 3: RENAME with SHORT token
        print(f"\n[测试 3] MaZiqc rename with SHORT token")
        rpc_params = json.dumps([20, "c_1e571b3941650ebe", "[TEST] rename test"])
        rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{qs_str}", body_str])

        if result.get("ok"):
            print(f"  status: {result['status']}")
            print(f"  body: {result['text'][:200]}")
        else:
            print(f"  error code: {result.get('status')}")

        # Test 4: hNvQHb to load conversation
        print(f"\n[测试 4] hNvQHb load conversation")
        qs_h = qs_str.replace("rpcids=MaZiqc", "rpcids=hNvQHb").replace("source-path=%2Fapp", "source-path=%2Fapp%2Fc_1e571b3941650ebe")
        rpc_call = json.dumps([["hNvQHb", "[null,null]", None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{qs_h}", body_str])

        if result.get("ok") and result.get("text"):
            print(f"  response: {len(result['text'])} bytes")
            # Search for long token patterns
            matches = re.findall(r't[A-Za-z0-9+/]{50,}={0,2}', result['text'])
            print(f"  long tokens found: {len(matches)}")
            for m in matches[:5]:
                print(f"    {m[:60]}...")
        else:
            print(f"  error: {result.get('status', '?')}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
