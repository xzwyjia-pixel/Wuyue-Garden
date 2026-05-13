"""
Debug MUAZcd fetch: extract fresh params directly from a page's OWN batch request.
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
        body_text = await page.inner_text("body")
        if "登录" in body_text or "Sign in" in body_text:
            for _ in range(60):
                await asyncio.sleep(1)
                if "登录" not in await page.inner_text("body"): break

        # Capture ALL batch requests for 15 seconds, then pick latest params
        all_params = []
        async def on_req(req):
            if "/batchexecute" not in req.url:
                return
            try:
                pd = req.post_data
                if pd and "at=" in pd:
                    parsed_url = urllib.parse.urlparse(req.url)
                    qp = urllib.parse.parse_qs(parsed_url.query)
                    bqp = urllib.parse.parse_qs(pd)
                    all_params.append({
                        "at": bqp.get("at", [""])[0],
                        "bl": qp.get("bl", [""])[0],
                        "fsid": qp.get("f.sid", [""])[0],
                        "reqid": int(qp.get("_reqid", ["0"])[0]),
                        "rpcids": qp.get("rpcids", [""])[0],
                        "source_path": qp.get("source-path", [""])[0],
                        "time": time.time(),
                        "full_url": req.url[:250],
                        "body_preview": pd[:200]
                    })
            except: pass

        page.on("request", on_req)

        # Click a conversation to trigger batch requests
        print("[1] Click first conv to trigger page requests...")
        conv = await page.evaluate("""() => {
            const a = document.querySelector('a[href*="/app/"]');
            if (a) { a.click(); return a.getAttribute('href'); }
            return null;
        }""")
        print(f"  Clicked: {conv}")
        await asyncio.sleep(5)

        # Also trigger the rename UI to get MUAZcd call
        print("[2] Open rename UI to trigger MUAZcd...")
        await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/"]');
            if (!a) return;
            a.scrollIntoView({{block: 'center'}});
            a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
            const parent = a.closest('div, li') || a.parentElement;
            const btn = parent?.querySelector('[data-test-id="actions-menu-button"]');
            if (btn) btn.click();
        }}""")
        await asyncio.sleep(1.5)

        await page.evaluate("""() => {
            const panels = document.querySelectorAll('.mat-mdc-menu-panel, .cdk-overlay-pane');
            for (const p of panels) {
                if (p.offsetParent === null) continue;
                for (const btn of p.querySelectorAll('button')) {
                    if (btn.textContent?.includes('重命名')) {
                        btn.click(); return;
                    }
                }
            }
        }""")
        await asyncio.sleep(2)

        page.remove_listener("request", on_req)

        print(f"\n[3] Captured {len(all_params)} batch requests:")
        for p in all_params:
            print(f"  rpcids={p['rpcids']} _reqid={p['reqid']} source={p['source_path'][:30]}")
            if p['rpcids'] == 'MUAZcd':
                print(f"    **** MUAZcd params ****")
                print(f"    at={p['at'][:40]}...")
                print(f"    bl={p['bl']}")
                print(f"    fsid={p['fsid']}")
                print(f"    body={p['body_preview'][:300]}")

        # Get latest params and test MUAZcd
        if all_params:
            # Use params from a recent non-MUAZcd call (to test without triggering rename UI again)
            # But we need fresh params. Pick the last one with a non-MUAZcd rpcid
            source = None
            for p in reversed(all_params):
                if p["rpcids"] != "MUAZcd" and p["rpcids"] and p["at"]:
                    source = p
                    break

            if source:
                print(f"\n[4] Test MUAZcd fetch with fresh params...")
                print(f"  Using: rpcids={source['rpcids']} _reqid={source['reqid']}")
                req_id = source["reqid"] + 100000

                # Get c_xxx token for test
                # Try to extract from the MUAZcd call we saw
                muazcd_call = next((p for p in all_params if p["rpcids"] == "MUAZcd"), None)
                c_token = None
                if muazcd_call:
                    # Extract c_xxx from body
                    body = muazcd_call["body_preview"]
                    m = re.search(r'c_[a-zA-Z0-9]+', body)
                    if m: c_token = m.group(0)
                    print(f"  Extracted c_token: {c_token}")
                    print(f"  Original body: {body[:400]}")

                if c_token:
                    new_title = f"[TEST] MUAZcd direct {int(time.time())%10000}"
                    muazcd_params = json.dumps([None, [["title"]], [c_token, new_title]])
                    rpc_call = json.dumps([["MUAZcd", muazcd_params, None, "generic"]])
                    body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(source['at'])}"
                    qs = f"rpcids=MUAZcd&source-path=%2Fapp%2F{c_token}&bl={urllib.parse.quote(source['bl'])}&f.sid={urllib.parse.quote(source['fsid'])}&hl=zh-CN&_reqid={req_id}&rt=c"

                    print(f"  Sending MUAZcd request...")
                    result = await page.evaluate("""async (url, body) => {
                        try {
                            const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                            const t = await r.text(); return {ok:r.ok, status:r.status, text:t.substring(0, 300)};
                        } catch(e) { return {ok:false, error:e.message}; }
                    }""", [f"{BATEXECUTE}?{qs}", body_str])
                    print(f"  Result: {json.dumps(result, ensure_ascii=False)[:400]}")
                else:
                    print("  No c_token found in captured requests")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
