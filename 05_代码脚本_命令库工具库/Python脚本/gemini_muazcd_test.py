"""
Test MUAZcd rename via fetch. Extract params from page, send RPC.
"""
import asyncio, json, urllib.parse, re, time
from playwright.async_api import async_playwright

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(5)
        body = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            for _ in range(60):
                await asyncio.sleep(1)
                if "登录" not in await page.inner_text("body"): break

        # Extract params from real batch request
        print("[1/4] Extracting params from page...")
        params = {}

        async def on_req(req):
            if "/batchexecute" not in req.url or params.get("done"):
                return
            try:
                pd = req.post_data
                if pd and "at=" in pd:
                    bqp = urllib.parse.parse_qs(pd)
                    if "at" in bqp:
                        params["at"] = bqp["at"][0]
                        parsed = urllib.parse.urlparse(req.url)
                        qp = urllib.parse.parse_qs(parsed.query)
                        params["bl"] = qp.get("bl", [""])[0]
                        params["fsid"] = qp.get("f.sid", [""])[0]
                        params["reqid"] = int(qp.get("_reqid", ["0"])[0])
                        params["done"] = True
            except: pass

        page.on("request", on_req)
        # Navigate to trigger requests
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(8)
        page.remove_listener("request", on_req)

        if not params.get("at"):
            print("  FAIL: no at token")
            return

        print(f"  at:  {params['at'][:40]}...")
        print(f"  bl:  {params['bl'][:40]}...")
        print(f"  fsid: {params['fsid']}")
        req_id = params["reqid"] + 100000
        print(f"  _reqid: {req_id}")

        # Get convs
        print("\n[2/4] Getting conversation list...")
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1 && !t.includes('[TEST]') && !t.includes('[DEV]')) {
                    // Get short c_xxx token from the conversation element
                    const parent = a.closest('div, li') || a.parentElement;
                    const convEl = parent?.querySelector('[data-test-id="conversation"]') || a;
                    const cId = convEl.getAttribute('data-conversation-id') || '';
                    items.push({
                        id: m[1],
                        title: t.substring(0, 60),
                        cid: cId,
                        dataAttrs: Object.fromEntries(
                            [...(convEl?.attributes || [])].filter(a => a.name.startsWith('data-')).map(a => [a.name, a.value])
                        )
                    });
                }
            }
            return items;
        }""")
        print(f"  Got {len(convs)} convs")

        # Try to find c_xxx token
        print(f"\n[3/4] Finding c_xxx token...")
        # The c_xxx is in the href or data attributes
        first = convs[0]
        print(f"  First conv: id={first['id']} title='{first['title'][:40]}'")
        print(f"  Data attrs: {json.dumps(first.get('dataAttrs', {}), ensure_ascii=False)}")
        print(f"  cid: {first['cid']}")

        # MUAZcd needs short c_xxx token. Let's get it from the URL or data
        # The "app/xxxxx" URL param is the short token in some cases
        # But Gemini v2 might use different patterns. Let's search in DOM:
        c_token = first["cid"] or first["id"]

        # Try MUAZcd rename via fetch
        print(f"\n[4/4] MUAZcd rename test...")
        new_title = f"[DEV] {first['title'][:40]}"
        print(f"  Token: {c_token}")
        print(f"  New title: '{new_title}'")

        # Build RPC params
        # Format from capture: [null,[["title"]],["c_TOKEN","NEW_TITLE"]]
        muazcd_params = json.dumps([None, [["title"]], [c_token, new_title]])
        rpc_call = json.dumps([["MUAZcd", muazcd_params, None, "generic"]])
        body = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(params['at'])}"
        qs = f"rpcids=MUAZcd&source-path=%2Fapp%2F{c_token}&bl={urllib.parse.quote(params['bl'])}&f.sid={urllib.parse.quote(params['fsid'])}&hl=zh-CN&_reqid={req_id}&rt=c"

        result = await page.evaluate("""async (url, body) => {
            try {
                const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                const t = await r.text(); return {ok:r.ok, status:r.status, text:t};
            } catch(e) { return {ok:false, error:e.message}; }
        }""", [f"{BATEXECUTE}?{qs}", body])
        print(f"  Result: {json.dumps(result, ensure_ascii=False)[:300]}")

        if result.get("ok"):
            # Parse response
            raw = re.sub(r"^\)\]}'\n?", "", result["text"])
            chunks = []
            pos = 0
            while pos < len(raw):
                m = re.match(r'\n(\d+)\n', raw[pos:])
                if not m: break
                size = int(m.group(1)); js = pos + m.end(); je = js + size
                try: chunks.append(json.loads(raw[js:je]))
                except: break
                pos = je
            if chunks:
                print(f"  Parsed: {json.dumps(chunks[0], ensure_ascii=False)[:300]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
