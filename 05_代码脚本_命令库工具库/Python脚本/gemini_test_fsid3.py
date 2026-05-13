"""
Use existing page (no navigate). Capture f.sid, test MaZiqc.
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
        page = ctx.pages[0]

        await asyncio.sleep(2)

        # Capture one batchexecute request
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
        await asyncio.sleep(10)
        page.remove_listener("request", on_req)

        if "at" not in url_data:
            print("[FAIL] no at token")
            if "url" in url_data:
                print(f"  Got URL but no at: {url_data['url'][:100]}")
            return

        at_token = url_data["at"]
        parsed = urllib.parse.urlparse(url_data["url"])
        qs = urllib.parse.parse_qs(parsed.query)
        fsid = qs.get("f.sid", [""])[0]
        bl = qs.get("bl", [""])[0]

        print(f"f.sid: {fsid}")
        print(f"bl: {bl}")
        print(f"at: {at_token[:40]}...")

        # Build URL
        base_params = {"rpcids":"MaZiqc","source-path":"/app","bl":bl,"f.sid":fsid,"hl":"zh-CN","rt":"c"}
        qs_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in base_params.items())

        # Test: MaZiqc list all recent
        print(f"\n[测试] MaZiqc list [13,null,[0,null,50]]")
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
                inner_str = chunks[0][0][2]
                inner = json.loads(inner_str)
                convs = inner[2] if len(inner) > 2 else []
                print(f"  → {len(convs)} 对话")
                for c in convs[:5]:
                    tok = c[0] if len(c) > 0 else "?"
                    title = c[1] if len(c) > 1 else "?"
                    print(f"    {str(tok)[:30]:30s} {str(title)[:60]}")
        else:
            print(f"  error: {result.get('status', '?')}")
            if result.get("text"):
                print(f"  body: {result['text'][:200]}")

        # Test rename with SHORT token
        print(f"\n[测试] MaZiqc rename [20,\"c_test\",\"title\"]")
        rpc_params = json.dumps([20, "c_1e571b3941650ebe", "[TEST] short token"])
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
            print(f"  OK! status: {result['status']}")
            print(f"  body: {result['text'][:300]}")
        else:
            print(f"  error: {result.get('status', '?')}")
            if result.get("text"):
                print(f"  body: {result['text'][:200]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
