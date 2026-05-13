"""
Capture ONE successful MUAZcd rename request from UI, then replay it with different title.
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

        # Capture MUAZcd rename request
        captured_req = {}

        async def on_req(req):
            if captured_req.get("done"): return
            if "/batchexecute" not in req.url: return
            try:
                pd = req.post_data
                if pd and "MUAZcd" in pd and "title" in pd and not captured_req.get("done"):
                    captured_req.update({
                        "url": req.url,
                        "body": pd[:2000],
                        "headers": dict(req.headers),
                        "done": True,
                        "captured_time": time.time()
                    })
                    print("  [CAPTURED MUAZcd rename request]")
            except: pass

        page.on("request", on_req)

        # Pick a non-[TEST] conv
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) {
                    seen.add(m[1]); items.push({id:m[1], title:t.substring(0,50)});
                }
            }
            return items;
        }""")

        # Find first conv without [TEST] or [DEV]
        target = None
        for c in convs:
            if "[TEST]" not in c["title"] and "[DEV]" not in c["title"]:
                target = c
                break
        if not target:
            print("No non-test conv found")
            return

        original_title = target["title"]
        test_title = f"[TEST] UI rename capture {int(time.time()) % 10000}"

        print(f"Target: '{original_title[:40]}'")
        print(f"New: '{test_title}'")

        # UI rename flow (PROVEN WORKING)
        print("\n[1] UI rename flow...")
        await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (a) {{
                a.scrollIntoView({{block: 'center'}});
                a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
            }}
        }}""")
        await asyncio.sleep(0.8)

        btn_pos = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            const parent = (a?.closest('div, li') || a?.parentElement);
            const btn = parent?.querySelector('[data-test-id="actions-menu-button"]');
            if (!btn || btn.getBoundingClientRect().width === 0) return null;
            const r = btn.getBoundingClientRect();
            return {{x: r.x + r.width/2, y: r.y + r.height/2}};
        }}""")
        if not btn_pos:
            print("  No menu button visible")
            return

        await page.mouse.click(btn_pos["x"], btn_pos["y"])
        await asyncio.sleep(1)

        await page.evaluate("""() => {
            const panels = document.querySelectorAll('.mat-mdc-menu-panel, .cdk-overlay-pane');
            for (const p of panels) {
                if (p.offsetParent === null) continue;
                for (const btn of p.querySelectorAll('button')) {
                    if (btn.textContent?.includes('重命名')) { btn.click(); return; }
                }
            }
        }""")
        await asyncio.sleep(1)

        await page.evaluate("""() => {
            const inputs = document.querySelectorAll('input.mat-mdc-input-element');
            for (const inp of inputs) {
                if (inp.offsetParent !== null) {
                    inp.focus(); inp.value = '';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                    break;
                }
            }
        }""")
        await asyncio.sleep(0.3)
        await page.keyboard.type(test_title, delay=25)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)

        page.remove_listener("request", on_req)

        # Check result
        new_sidebar = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            return a?.textContent?.trim() || null;
        }}""")
        print(f"  Sidebar result: '{new_sidebar}'")

        # Now replay with original title to restore
        if captured_req.get("done"):
            print(f"\n[2] Replay exact captured request to restore...")

            # Parse the captured request
            url = captured_req["url"]
            body = captured_req["body"]

            # Parse URL params
            parsed_url = urllib.parse.urlparse(url)
            qp = urllib.parse.parse_qs(parsed_url.query)
            bl = qp.get("bl", [""])[0]
            fsid = qp.get("f.sid", [""])[0]
            reqid = int(qp.get("_reqid", ["0"])[0])
            source_path = qp.get("source-path", [""])[0]

            # Parse body manually (parse_qs can mangle the nested JSON)
            # Body format: f.req=URL_ENCODED_JSON&at=TOKEN
            at_token = ""
            freqs = ""
            if "&at=" in body:
                freqs_raw = body.split("&at=")[0]
                if freqs_raw.startswith("f.req="):
                    freqs_raw = freqs_raw[6:]
                else:
                    # Try full body
                    freqs_raw = body
                freqs = urllib.parse.unquote(freqs_raw)
                at_part = body.split("&at=")[1]
                # at token might have trailing & or not
                at_token = at_part.split("&")[0] if "&" in at_part else at_part
            else:
                bqp = urllib.parse.parse_qs(body)
                at_token = bqp.get("at", [""])[0]
                freqs = urllib.parse.unquote(bqp.get("f.req", [""])[0])

            print(f"  freqs: {freqs[:300]}")

            # Parse the RPC call
            rpc_data = json.loads(freqs)
            # Structure is [[["MUAZcd", params, null, "generic"]]] — extra nesting
            inner = rpc_data
            while isinstance(inner, list) and len(inner) == 1 and isinstance(inner[0], list):
                inner = inner[0]
            # Now inner should be ["MUAZcd", params, null, "generic"]
            rpc_name = inner[0]
            rpc_params_str = inner[1]
            rpc_params = json.loads(rpc_params_str)
            print(f"  rpc_name: {rpc_name}, c_token: {rpc_params[2][0]}, title: {rpc_params[2][1]}")

            # rpc_params format: [null, [["title"]], ["c_xxx", "NEW_TITLE"]]
            c_token = rpc_params[2][0]

            print(f"  Decoded:")
            print(f"    rpcid: {rpc_name}")
            print(f"    c_token: {c_token}")
            print(f"    bl: {bl}...")
            print(f"    fsid: {fsid}")
            print(f"    _reqid: {reqid}")
            print(f"    source_path: {source_path}")

            # NOW replay with ORIGINAL title
            print(f"\n[3] Replay fetch with ORIGINAL title...")
            replay_reqid = reqid + 100000
            replay_params = json.dumps([None, [["title"]], [c_token, original_title]])
            replay_rpc = json.dumps([[rpc_name, replay_params, None, "generic"]])
            replay_body = f"f.req={urllib.parse.quote(replay_rpc)}&at={urllib.parse.quote(at_token)}"
            replay_qs = f"rpcids={rpc_name}&source-path={urllib.parse.quote(source_path)}&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={replay_reqid}&rt=c"

            replay_result = await page.evaluate("""async (url, body) => {
                try {
                    const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                    const text = await r.text();
                    return {ok: r.ok, status: r.status, text: text.substring(0, 300)};
                } catch(e) { return {ok:false, error: e.message}; }
            }""", [f"{BATEXECUTE}?{replay_qs}", replay_body])

            print(f"  Replay result: {json.dumps(replay_result, ensure_ascii=False)[:400]}")

            if replay_result.get("ok"):
                await asyncio.sleep(1)
                restored = await page.evaluate(f"""() => {{
                    const a = document.querySelector('a[href*="/app/{target['id']}"]');
                    return a?.textContent?.trim() || null;
                }}""")
                print(f"  Sidebar after replay: '{restored}'")
            else:
                print(f"  Replay FAILED. Trying different approaches...")

                # Try with same _reqid (not incremented)
                print(f"\n[4] Retry with SAME _reqid...")
                replay_qs2 = f"rpcids={rpc_name}&source-path={urllib.parse.quote(source_path)}&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={reqid}&rt=c"
                replay_result2 = await page.evaluate("""async (url, body) => {
                    try {
                        const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                        const text = await r.text();
                        return {ok: r.ok, status: r.status, text: text.substring(0, 300)};
                    } catch(e) { return {ok:false, error: e.message}; }
                }""", [f"{BATEXECUTE}?{replay_qs2}", replay_body])
                print(f"  Result: {json.dumps(replay_result2, ensure_ascii=False)[:400]}")

                if not replay_result2.get("ok"):
                    print(f"\n[5] Try with FRESH at token...")
                    # Get fresh at from a page request
                    fresh_at = None
                    at_fut = asyncio.get_event_loop().create_future()
                    async def capture_at(req):
                        if at_fut.done(): return
                        if "/batchexecute" in req.url:
                            try:
                                pd = req.post_data
                                if pd and "at=" in pd:
                                    bqp = urllib.parse.parse_qs(pd)
                                    if "at" in bqp:
                                        at_fut.set_result(bqp["at"][0])
                            except: pass
                    page.on("request", capture_at)
                    # Trigger a page interaction to get fresh at
                    await page.evaluate("""() => {
                        const a = document.querySelector('a[href*="/app/"]');
                        if (a) a.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                    }""")
                    await asyncio.sleep(3)
                    try: fresh_at = await asyncio.wait_for(at_fut, timeout=5)
                    except: pass
                    page.remove_listener("request", capture_at)

                    if fresh_at:
                        print(f"  Fresh at: {fresh_at[:40]}...")
                        replay_body3 = f"f.req={urllib.parse.quote(replay_rpc)}&at={urllib.parse.quote(fresh_at)}"
                        replay_reqid3 = reqid + 200000
                        replay_qs3 = f"rpcids={rpc_name}&source-path={urllib.parse.quote(source_path)}&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={replay_reqid3}&rt=c"
                        replay_result3 = await page.evaluate("""async (url, body) => {
                            try {
                                const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                                const text = await r.text();
                                return {ok: r.ok, status: r.status, text: text.substring(0, 300)};
                            } catch(e) { return {ok:false, error: e.message}; }
                        }""", [f"{BATEXECUTE}?{replay_qs3}", replay_body3])
                        print(f"  Result: {json.dumps(replay_result3, ensure_ascii=False)[:400]}")
        else:
            print("\n[2] No MUAZcd renamed request captured")
            print(f"  (rename probably didn't go through)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
