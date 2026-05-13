"""
Click actions menu → find rename → capture the REAL batchexecute call.
"""
import asyncio, json, re, urllib.parse
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

        print(f"URL: {page.url}")

        # Capture real rename request
        capture = {}
        async def on_req(req):
            if capture.get("done"): return
            if "/batchexecute" in req.url and "MaZiqc" in req.url:
                try:
                    pd = req.post_data
                    if pd:
                        capture["url"] = req.url
                        capture["method"] = req.method
                        capture["headers"] = dict(req.headers)
                        capture["body"] = pd[:2000]
                        capture["done"] = True
                        print(f"\n>>> CAPTURED MaZiqc request!")
                        print(f"  URL: {req.url}")
                except Exception as e:
                    print(f"  capture error: {e}")

        # Also capture response for any MaZiqc
        async def on_resp(resp):
            if "MaZiqc" in resp.url:
                try:
                    body = await resp.text()
                    print(f">>> MaZiqc RESP ({resp.status}): {body[:300]}")
                except: pass

        page.on("request", on_req)
        page.on("response", on_resp)

        # Click first conversation to load it
        print("\n[1] Click first conv...")
        first = await page.evaluate("""() => {
            const a = document.querySelector('a[href*="/app/"]');
            if (a) { a.click(); return a.getAttribute('href'); }
            return null;
        }""")
        print(f"  Clicked: {first}")
        await asyncio.sleep(3)

        # Try clicking "prompt-edit-button" (rename button next to title)
        print("\n[2] Find prompt-edit-button...")
        edit_btn = await page.evaluate("""() => {
            const btn = document.querySelector('[data-testid="prompt-edit-button"]');
            if (!btn) return null;
            const rect = btn.getBoundingClientRect();
            if (rect.width === 0 && rect.height === 0) return { hidden: true };
            return { x: rect.x, y: rect.y, w: rect.width, h: rect.height, visible: true };
        }""")
        print(f"  prompt-edit-button: {json.dumps(edit_btn, ensure_ascii=False)}")

        # Also try clicking the title to trigger rename
        print("\n[3] Click title text...")
        await page.evaluate("""() => {
            const h1 = document.querySelector('h1');
            if (h1) { h1.click(); }
        }""")
        await asyncio.sleep(2)

        # Check if input box appeared for rename
        input_check = await page.evaluate("""() => {
            const inputs = document.querySelectorAll('input[type="text"], input:not([type]), [contenteditable="true"]');
            for (const inp of inputs) {
                if (inp.offsetParent !== null) {
                    return { tag: inp.tagName, placeholder: inp.getAttribute('placeholder') || '', value: inp.value || inp.textContent?.trim() || '' };
                }
            }
            // Also check for textareas
            const textareas = document.querySelectorAll('textarea');
            for (const ta of textareas) {
                if (ta.offsetParent !== null) return { tag: 'textarea', value: ta.value?.substring(0, 50) };
            }
            return null;
        }""")
        print(f"  Visible text inputs after title click: {json.dumps(input_check, ensure_ascii=False)}")

        # Now try clicking actions menu button in sidebar
        print("\n[4] Click actions-menu-button (sidebar)...")
        menu = await page.evaluate("""() => {
            const btn = document.querySelector('[data-test-id="actions-menu-button"]');
            if (!btn) return null;
            const rect = btn.getBoundingClientRect();
            if (rect.width === 0 && rect.height === 0) {
                // Need to hover parent first
                const parent = btn.closest('[class*="conversation"], a, li') || btn.parentElement;
                if (parent) {
                    parent.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                    return { clicked: false, hidden: true };
                }
            }
            const x = rect.x + rect.width/2;
            const y = rect.y + rect.height/2;
            btn.click();
            return { x, y, w: rect.width, h: rect.height };
        }""")
        print(f"  Click result: {json.dumps(menu, ensure_ascii=False)}")
        await asyncio.sleep(2)

        # Check for visible menu
        print("\n[5] Visible menu items after click:")
        menu_items = await page.evaluate("""() => {
            const items = [];
            // Look for Angular Material menu panels
            const panels = document.querySelectorAll('.mat-mdc-menu-panel, [role="menu"], [class*="menu-panel"], [class*="dropdown"]');
            for (const panel of panels) {
                if (panel.offsetParent !== null) {
                    const options = panel.querySelectorAll('[role="menuitem"], [mat-menu-item], button, [role="button"]');
                    for (const opt of options) {
                        items.push({
                            text: opt.textContent?.trim()?.substring(0, 40),
                            aria: opt.getAttribute('aria-label'),
                            tag: opt.tagName,
                            html: opt.innerHTML?.substring(0, 120)
                        });
                    }
                }
            }
            // Also check any visible popup/overlay
            const overlays = document.querySelectorAll('.cdk-overlay-pane, [class*="overlay"]');
            for (const ov of overlays) {
                if (ov.offsetParent !== null) {
                    const opts = ov.querySelectorAll('button, [role="menuitem"]');
                    for (const opt of opts) {
                        items.push({
                            from: 'overlay',
                            text: opt.textContent?.trim()?.substring(0, 40),
                            aria: opt.getAttribute('aria-label'),
                            tag: opt.tagName
                        });
                    }
                }
            }
            return items;
        }""")
        if menu_items:
            print(f"  Found {len(menu_items)} items:")
            for m in menu_items:
                print(f"    {json.dumps(m, ensure_ascii=False)[:150]}")
        else:
            print("  No visible menu found")

        # If no menu appeared, try right-click approach on sidebar
        if not menu_items:
            print("\n[6] Try right-click on sidebar conv...")
            # Use mouse to scroll sidebar first to see top item
            sidebar_item = await page.evaluate("""() => {
                const a = document.querySelector('a[href*="/app/"]');
                if (!a) return null;
                const rect = a.getBoundingClientRect();
                return {
                    x: rect.x + rect.width/2,
                    y: rect.y + 50,
                    inView: rect.top >= 0 && rect.bottom <= window.innerHeight
                };
            }""")
            print(f"  Sidebar item: {json.dumps(sidebar_item, ensure_ascii=False)}")
            if sidebar_item:
                await page.mouse.click(sidebar_item["x"], sidebar_item["y"], button="right")
                await asyncio.sleep(2)
                rcm = await page.evaluate("""() => {
                    const items = [];
                    const menus = document.querySelectorAll('[role="menu"]');
                    for (const menu of menus) {
                        for (const item of menu.querySelectorAll('[role="menuitem"]')) {
                            if (item.offsetParent !== null) {
                                const spans = item.querySelectorAll('span, div');
                                let text = '';
                                for (const s of spans) text += s.textContent?.trim() + ' ';
                                items.push(text.substring(0, 60) || item.textContent?.trim().substring(0, 60));
                            }
                        }
                    }
                    return items;
                }""")
                if rcm:
                    print(f"  Right-click menu:")
                    for r in rcm:
                        print(f"    - {r}")

        # Check if capture worked
        if capture.get("done"):
            print(f"\n=== RENAME RPC CAPTURED ===")
            url = capture["url"]
            print(f"URL: {url}")
            body = capture["body"]
            print(f"Body: {body[:500]}")
            # Extract relevant params
            qp = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            print(f"Query params:")
            for k, v in qp.items():
                print(f"  {k}: {v}")
            # Parse body
            bqp = urllib.parse.parse_qs(body)
            for k, v in bqp.items():
                if k != "at":
                    print(f"  body {k}: {urllib.parse.unquote(v[0])[:300]}")
        else:
            print("\n=== No MaZiqc request captured ===")

        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
