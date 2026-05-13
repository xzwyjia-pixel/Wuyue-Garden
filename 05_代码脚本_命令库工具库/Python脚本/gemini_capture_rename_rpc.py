"""
UI rename + CAPTURE the batchexecute request.
Goal: finally decode the exact MaZiqc [20] format.
"""
import asyncio, json, urllib.parse, re
from playwright.async_api import async_playwright

CDP_PORT = 9229

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

        # Capture ALL batchexecute requests
        batch_reqs = []
        async def on_req(req):
            if "/batchexecute" in req.url:
                try:
                    batch_reqs.append({
                        "url": req.url,
                        "method": req.method,
                        "headers": {k: v for k, v in req.headers.items() if k in ("content-type",)},
                        "body": req.post_data[:2000] if req.post_data else None
                    })
                except Exception as e:
                    batch_reqs.append({"error": str(e)[:100]})
        page.on("request", on_req)

        # Capture responses too
        batch_resps = []
        async def on_resp(resp):
            if "/batchexecute" in resp.url:
                try:
                    t = await resp.text()
                    batch_resps.append({
                        "url": resp.url[:200],
                        "status": resp.status,
                        "body": t[:500]
                    })
                except: pass
        page.on("response", on_resp)

        # Pick non-test conv
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1 && !t.includes('[TEST]')) {
                    seen.add(m[1]); items.push({id:m[1], title:t.substring(0,50)});
                }
            }
            return items;
        }""")
        target = convs[0]
        print(f"Target: '{target['title']}'")

        # Get original sidebar text for the input value (should be shorter than full title)
        sidebar_text = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (!a) return '';
            const titleEl = a.querySelector('[class*="title"], div');
            return titleEl ? titleEl.textContent?.trim() || '' : a.textContent?.trim() || '';
        }}""")
        print(f"Sidebar text: '{sidebar_text}'")

        # Scroll + hover + click menu
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
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return {{x: r.x + r.width/2, y: r.y + r.height/2}};
        }}""")
        if not btn_pos:
            print("No menu button")
            return

        await page.mouse.click(btn_pos["x"], btn_pos["y"])
        await asyncio.sleep(1)

        # Click "重命名"
        await page.evaluate("""() => {
            const panels = document.querySelectorAll('.mat-mdc-menu-panel, .cdk-overlay-pane');
            for (const p of panels) {
                if (p.offsetParent === null) continue;
                for (const btn of p.querySelectorAll('button')) {
                    if (btn.textContent?.includes('重命名')) {
                        btn.click();
                        return true;
                    }
                }
            }
            return false;
        }""")
        await asyncio.sleep(1)

        # Clear input and type NEW name only
        new_name = f"[DEV] Test rename RPC capture"
        await page.evaluate(f"""() => {{
            const inputs = document.querySelectorAll('input.mat-mdc-input-element');
            for (const inp of inputs) {{
                if (inp.offsetParent !== null) {{
                    inp.focus();
                    inp.value = '';
                    inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                    break;
                }}
            }}
        }}""")
        await asyncio.sleep(0.3)
        await page.keyboard.type(new_name, delay=30)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)

        # Restore original title
        await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (a) {{
                a.scrollIntoView({{block: 'center'}});
                a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
            }}
        }}""")
        await asyncio.sleep(0.5)
        await page.mouse.click(btn_pos["x"], btn_pos["y"])
        await asyncio.sleep(1)
        await page.evaluate("""() => {
            const panels = document.querySelectorAll('.mat-mdc-menu-panel, .cdk-overlay-pane');
            for (const p of panels) {
                if (p.offsetParent === null) continue;
                for (const btn of p.querySelectorAll('button')) {
                    if (btn.textContent?.includes('重命名')) {
                        btn.click();
                        return true;
                    }
                }
            }
            return false;
        }""")
        await asyncio.sleep(1)
        await page.evaluate(f"""() => {{
            const inputs = document.querySelectorAll('input.mat-mdc-input-element');
            for (const inp of inputs) {{
                if (inp.offsetParent !== null) {{
                    inp.focus();
                    inp.value = '';
                    inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                    break;
                }}
            }}
        }}""")
        await asyncio.sleep(0.3)
        await page.keyboard.type(target["title"], delay=30)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)

        # Show captured batchexecute calls
        print(f"\n=== {len(batch_reqs)} batchexecute requests ===")
        for i, r in enumerate(batch_reqs):
            print(f"\n--- Request {i} ---")
            print(f"  URL: {r['url'][:250]}")

            # Parse URL params
            parsed = urllib.parse.urlparse(r['url'])
            qp = urllib.parse.parse_qs(parsed.query)
            print(f"  Params: rpcids={qp.get('rpcids',['?'])[0]} _reqid={qp.get('_reqid',['?'])[0]} f.sid={qp.get('f.sid',['?'])[0]}")

            # Parse body
            body = r.get('body', '')
            if body:
                # f.req=<urlencoded> & at=<urlencoded>
                body_qp = urllib.parse.parse_qs(body)
                if 'f.req' in body_qp:
                    freqs = urllib.parse.unquote(body_qp['f.req'][0])
                    # Parse the NDJSON
                    raw = re.sub(r'^\)\]}\'\n?', '', freqs)
                    try:
                        # Try JSON array parse
                        data = json.loads(raw) if raw.startswith('[') else None
                        if data:
                            print(f"  f.req parsed:")
                            for entry in data if isinstance(data, list) else [data]:
                                if isinstance(entry, list) and len(entry) >= 2:
                                    rpc_id = entry[0]
                                    params = entry[1]
                                    print(f"    RPCID: {rpc_id}")
                                    print(f"    Params: {str(params)[:200]}")
                                else:
                                    print(f"    {str(entry)[:200]}")
                        else:
                            print(f"  f.req raw: {raw[:300]}")
                    except json.JSONDecodeError:
                        print(f"  f.req raw: {raw[:300]}")
                if 'at' in body_qp:
                    print(f"  at: {urllib.parse.unquote(body_qp['at'][0])[:40]}...")

        print(f"\n=== {len(batch_resps)} batchexecute responses ===")
        for r in batch_resps:
            print(f"  Status {r['status']}: {r['body'][:200]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
