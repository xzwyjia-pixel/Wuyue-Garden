"""
Test both bracket formats for MUAZcd fetch.
The UI sends f.req=[[[...]]] but earlier code sends f.req=[[...]].
Also test whether source-path matters.
"""
import asyncio, json, urllib.parse, re, time
from playwright.async_api import async_playwright

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

async def test_format(page, params, rpc_name, rpc_params, label, use_triple=False):
    """Send MUAZcd and return result."""
    if use_triple:
        body_json = json.dumps([[rpc_name, rpc_params, None, "generic"]])
    else:
        body_json = json.dumps([rpc_name, rpc_params, None, "generic"])

    body_str = f"f.req={urllib.parse.quote(body_json)}&at={urllib.parse.quote(params['at'])}"
    req_id = params["reqid"]
    params["reqid"] = req_id + 100000

    qs = f"rpcids={rpc_name}&source-path={urllib.parse.quote(params['source_path'])}&bl={urllib.parse.quote(params['bl'])}&f.sid={urllib.parse.quote(params['fsid'])}&hl=zh-CN&_reqid={req_id + 100000}&rt=c"

    result = await page.evaluate("""async (url, body) => {
        try {
            const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
            return {ok:r.ok, status:r.status, text: (await r.text()).substring(0, 200)};
        } catch(e) { return {ok:false, error:e.message}; }
    }""", [f"{BATEXECUTE}?{qs}", body_str])

    ok = "OK" if result.get("ok") else "FAIL"
    print(f"  [{ok}] {label}: status={result.get('status','?')}")
    if not result.get("ok"):
        print(f"    {result.get('text','')[:150]}")
    return result.get("ok")

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

        # Capture params from a REAL rename via UI
        print("[1] Get params from a real UI rename...")

        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1 && !t.includes('[TEST]') && !t.includes('[DEV]')) {
                    seen.add(m[1]); items.push({id:m[1], title:t.substring(0,50)});
                }
            }
            return items;
        }""")
        print(f"  Found {len(convs)} convs")

        # Also do a MaZiqc list to get c_xxx tokens
        # Extract params from page
        async def capture_params():
            fut = asyncio.get_event_loop().create_future()
            async def on_req(req):
                if fut.done(): return
                if "/batchexecute" not in req.url: return
                try:
                    pd = req.post_data
                    if pd and "at=" in pd:
                        parsed_url = urllib.parse.urlparse(req.url)
                        qp = urllib.parse.parse_qs(parsed_url.query)
                        bqp = urllib.parse.parse_qs(pd)
                        if "at" in bqp:
                            fut.set_result({
                                "at": bqp["at"][0],
                                "bl": qp.get("bl", [""])[0],
                                "fsid": qp.get("f.sid", [""])[0],
                                "reqid": int(qp.get("_reqid", ["0"])[0]),
                                "source_path": qp.get("source-path", ["/app"])[0],
                            })
                except: pass
            page.on("request", on_req)
            # Trigger a request
            await page.evaluate("""() => {
                const a = document.querySelector('a[href*="/app/"]');
                if (a) a.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
            }""")
            try: result = await asyncio.wait_for(fut, timeout=8)
            except: result = None
            page.remove_listener("request", on_req)
            return result

        params = None

        # Test 1: MUAZcd via UI (ensure we get a working rename captured)
        print("\n[2] UI rename to capture real params...")
        target = None
        for c in convs:
            if "[TEST]" not in c["title"] and "[DEV]" not in c["title"]:
                target = c
                break

        # First capture params from page
        params = await capture_params()
        if params:
            print(f"  Params from page: at={params['at'][:30]}... _reqid={params['reqid']}")

        # Now do UI rename and capture the real request
        captured = {}

        async def on_req(req):
            if captured.get("done"): return
            if "/batchexecute" in req.url and "MUAZcd" in req.url:
                try:
                    pd = req.post_data
                    if pd and "title" in pd:
                        captured.update({
                            "url": req.url,
                            "body": pd[:2000],
                            "done": True
                        })
                except: pass

        page.on("request", on_req)

        # UI flow
        test_title = f"[TST] fetch format test {int(time.time()) % 10000}"
        print(f"  Target: '{target['title'][:40]}' -> '{test_title}'")

        await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (a) {{ a.scrollIntoView({{block: 'center'}}); a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}})); }}
        }}""")
        await asyncio.sleep(0.8)

        btn_pos = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            const parent = (a?.closest('div, li') || a?.parentElement);
            const btn = parent?.querySelector('[data-test-id="actions-menu-button"]');
            if (!btn || btn.getBoundingClientRect().width === 0) return null;
            const r = btn.getBoundingClientRect(); return {{x: r.x + r.width/2, y: r.y + r.height/2}};
        }}""")
        if not btn_pos: print("  No button"); return

        await page.mouse.click(btn_pos["x"], btn_pos["y"])
        await asyncio.sleep(1)
        await page.evaluate("""() => {
            for (const p of document.querySelectorAll('.mat-mdc-menu-panel, .cdk-overlay-pane')) {
                if (p.offsetParent === null) continue;
                for (const btn of p.querySelectorAll('button')) {
                    if (btn.textContent?.includes('重命名')) { btn.click(); return; }
                }
            }
        }""")
        await asyncio.sleep(1)
        await page.evaluate("""() => {
            for (const inp of document.querySelectorAll('input.mat-mdc-input-element')) {
                if (inp.offsetParent !== null) {
                    inp.focus(); inp.value = '';
                    inp.dispatchEvent(new Event('input', {bubbles: true})); break;
                }
            }
        }""")
        await asyncio.sleep(0.3)
        await page.keyboard.type(test_title, delay=25)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)
        page.remove_listener("request", on_req)

        # Now we have:
        # - params from page (fresh at, fsid, bl, reqid)
        # - captured rename request (for format)
        # - target was renamed (need to restore)

        print(f"\n[3] Analyze captured request...")
        if captured:
            raw_body = captured["body"]
            print(f"  Raw body: {raw_body[:300]}")

            # Extract f.req value
            m = re.search(r'f\.req=([^&]+)', raw_body)
            if m:
                freqs = urllib.parse.unquote(m.group(1))
                print(f"  f.req decoded: {freqs[:300]}")

                # Count bracket nesting
                level = 0
                for ch in freqs:
                    if ch == '[': level += 1
                    elif ch == ']': level -= 1
                print(f"  Max nesting level: {level}")

                # Parse
                rpc_data = json.loads(freqs)
                print(f"  Parsed type: {type(rpc_data).__name__}")
                print(f"  Parsed top len: {len(rpc_data) if isinstance(rpc_data, list) else 'N/A'}")
                if isinstance(rpc_data, list) and len(rpc_data) > 0:
                    inner = rpc_data[0]
                    print(f"  Inner[0] type: {type(inner).__name__}, len: {len(inner) if isinstance(inner, list) else 'N/A'}")
                    if isinstance(inner, list) and len(inner) > 0:
                        innermost = inner[0]
                        print(f"  Innermost type: {type(innermost).__name__}, len: {len(innermost) if isinstance(innermost, list) else 'N/A'}")

            # Extract at
            m2 = re.search(r'at=([^&]+)', raw_body)
            at_token = urllib.parse.unquote(m2.group(1)) if m2 else params['at']

            # Extract URL params
            url = captured["url"]
            parsed_url = urllib.parse.urlparse(url)
            qp = urllib.parse.parse_qs(parsed_url.query)
            fsid = qp.get("f.sid", [params['fsid']])[0]
            bl = qp.get("bl", [params['bl']])[0]
            source_path = qp.get("source-path", ["/app"])[0]
            ui_reqid = int(qp.get("_reqid", ["0"])[0])

            print(f"\n  Captured params:")
            print(f"    source_path: {source_path}")
            print(f"    fsid: {fsid}")
            print(f"    bl: {bl[:40]}...")
            print(f"    _reqid: {ui_reqid}")

            c_token = None
            if m:
                m3 = re.search(r'c_[a-zA-Z0-9]+', m.group(1))
                if m3: c_token = m3.group(0)

            # Test both bracket formats
            print(f"\n[4] Testing MUAZcd fetch formats...")

            params2 = {
                "at": at_token,
                "bl": bl,
                "fsid": fsid,
                "source_path": source_path,
                "reqid": ui_reqid
            }

            if c_token:
                muazcd_params = json.dumps([None, [["title"]], [c_token, target["title"]]])

                # Test 1: 2-bracket (our old format)
                # The raw captured format: [[["MUAZcd", params, null, "generic"]]] - 3 brackets
                # Our old code: json.dumps([[rpc_name, params, null, "generic"]]) → 2 brackets
                print(f"\n  A) 2-bracket: json.dumps([[rpc_name, params, null, generic]])")
                # Page sends [[[...]]] but maybe this is post-form-encoded format
                result_a = await page.evaluate("""async (url, body) => {
                    try {
                        const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                        return {ok:r.ok, status:r.status, text: (await r.text()).substring(0, 200)};
                    } catch(e) { return {ok:false, error:e.message}; }
                }""", [
                    f"{BATEXECUTE}?rpcids=MUAZcd&source-path={urllib.parse.quote(source_path)}&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={ui_reqid + 100000}&rt=c",
                    f"f.req={urllib.parse.quote(json.dumps([rpc_name, muazcd_params, None, 'generic']))}&at={urllib.parse.quote(at_token)}"
                ])
                print(f"    Status: {result_a.get('status')} OK={result_a.get('ok')}")
                if not result_a.get("ok"):
                    print(f"    {result_a.get('text','')[:150]}")

                # Test 2: 3-bracket (matches page format)
                print(f"\n  B) 3-bracket: json.dumps([[[rpc_name, params, null, generic]]])")
                result_b = await page.evaluate("""async (url, body) => {
                    try {
                        const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                        return {ok:r.ok, status:r.status, text: (await r.text()).substring(0, 200)};
                    } catch(e) { return {ok:false, error:e.message}; }
                }""", [
                    f"{BATEXECUTE}?rpcids=MUAZcd&source-path={urllib.parse.quote(source_path)}&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={ui_reqid + 200000}&rt=c",
                    f"f.req={urllib.parse.quote(json.dumps([[rpc_name, muazcd_params, None, 'generic']]))}&at={urllib.parse.quote(at_token)}"
                ])
                print(f"    Status: {result_b.get('status')} OK={result_b.get('ok')}")
                if not result_b.get("ok"):
                    print(f"    {result_b.get('text','')[:150]}")

                # Test 3: Try with JUST [rpc_name, params, null, generic] (1 bracket, no array wrapping)
                print(f"\n  C) 1-bracket: json.dumps([rpc_name, params, null, generic])")
                result_c = await page.evaluate("""async (url, body) => {
                    try {
                        const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                        return {ok:r.ok, status:r.status, text: (await r.text()).substring(0, 200)};
                    } catch(e) { return {ok:false, error:e.message}; }
                }""", [
                    f"{BATEXECUTE}?rpcids=MUAZcd&source-path={urllib.parse.quote(source_path)}&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={ui_reqid + 300000}&rt=c",
                    f"f.req={urllib.parse.quote(json.dumps([rpc_name, muazcd_params, None, 'generic']))}&at={urllib.parse.quote(at_token)}"
                ])
                print(f"    Status: {result_c.get('status')} OK={result_c.get('ok')}")
                if not result_c.get("ok"):
                    print(f"    {result_c.get('text','')[:150]}")
        else:
            print("  No request captured (rename may have failed)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
