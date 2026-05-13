"""
Pinpoint exact rename UI and capture batchexecute call.
Focus: click rename menu → what DOM changes → find correct input.
"""
import asyncio, json
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

        # CAPTURE ALL batchexecute requests
        all_reqs = []
        async def on_req(req):
            if "/batchexecute" in req.url:
                try:
                    all_reqs.append({
                        "url": req.url,
                        "body": req.post_data[:1000] if req.post_data else None
                    })
                except: pass
        page.on("request", on_req)

        # Click conv 2 (first non-active)
        print("\n[1] Click conv to open...")
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) { seen.add(m[1]); items.push({id:m[1],title:t, href:h}); }
            }
            return items;
        }""")
        print(f"  {len(convs)} convs. Click conv[1]: '{convs[1]['title'][:40]}'")

        await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{convs[1]['id']}"]');
            if (a) a.click();
        }}""")
        await asyncio.sleep(2)

        # Click actions menu button
        print("\n[2] Open actions menu...")
        btn = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{convs[1]['id']}"]');
            if (!a) return null;
            a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
            const parent = a.closest('div, li') || a.parentElement;
            const btn = parent.querySelector('[data-test-id="actions-menu-button"]');
            if (!btn) return null;
            const rect = btn.getBoundingClientRect();
            return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
        }}""")
        if btn:
            await page.mouse.click(btn["x"], btn["y"])
            await asyncio.sleep(1)

        # Click "重命名"
        print("\n[3] Click '重命名'...")
        clicked = await page.evaluate("""() => {
            const menus = document.querySelectorAll('[role="menu"], .mat-mdc-menu-panel, .cdk-overlay-pane');
            for (const menu of menus) {
                if (menu.offsetParent === null) continue;
                const items = menu.querySelectorAll('[role="menuitem"], button, [mat-menu-item]');
                for (const item of items) {
                    const text = item.textContent?.trim() || '';
                    if (text.includes('重命名') || text.includes('Rename')) {
                        item.click();
                        return { clicked: true, text };
                    }
                }
            }
            return { clicked: false };
        }""")
        print(f"  {json.dumps(clicked, ensure_ascii=False)}")
        await asyncio.sleep(1.5)

        # Now scan ALL contenteditables and inputs to find the ONE that appeared for rename
        print("\n[4] Scan all editable elements...")
        all_editables = await page.evaluate("""() => {
            const result = [];
            // All contenteditable
            const eds = document.querySelectorAll('[contenteditable="true"]');
            for (const e of eds) {
                const rect = e.getBoundingClientRect();
                result.push({
                    type: 'contenteditable',
                    text: e.textContent?.trim()?.substring(0, 40),
                    visible: e.offsetParent !== null,
                    rect: { x: ~~rect.x, y: ~~rect.y, w: ~~rect.width, h: ~~rect.height },
                    class: e.className?.substring(0, 60),
                    parentClasses: (e.parentElement?.className || '').substring(0, 60),
                    html: e.innerHTML?.substring(0, 100)
                });
            }
            // All inputs
            const inputs = document.querySelectorAll('input');
            for (const inp of inputs) {
                const rect = inp.getBoundingClientRect();
                result.push({
                    type: 'input',
                    value: inp.value?.substring(0, 40),
                    placeholder: inp.getAttribute('placeholder') || '',
                    visible: inp.offsetParent !== null,
                    rect: { x: ~~rect.x, y: ~~rect.y, w: ~~rect.width, h: ~~rect.height },
                    class: inp.className?.substring(0, 60)
                });
            }
            // Check specifically for the sidebar title area (might become an input)
            const titles = document.querySelectorAll('.conversation-title');
            for (const t of titles) {
                result.push({
                    type: 'sidebar-title',
                    text: t.textContent?.trim()?.substring(0, 40),
                    visible: t.offsetParent !== null,
                    html: t.innerHTML?.substring(0, 200),
                    rect: {x: ~~t.getBoundingClientRect().x, y: ~~t.getBoundingClientRect().y}
                });
            }
            return result;
        }""")
        print(f"  Found {len(all_editables)} editable elements:")
        for e in all_editables:
            if e.get("visible"):
                print(f"    {json.dumps(e, ensure_ascii=False)[:200]}")

        # Check for batchexecute requests
        maziqc = [r for r in all_reqs if "MaZiqc" in r.get("url", "")]
        print(f"\n[5] MaZiqc batch requests: {len(maziqc)}")
        for r in maziqc[:5]:
            print(f"  URL: {r['url'][:250]}")
            if r.get("body"):
                print(f"  Body: {r['body'][:300]}")

        # If no rename input found, check if we need to click the title AFTER menu
        if not any(e.get("type") in ("input", "contenteditable") and e.get("visible") for e in all_editables):
            print("\n[6] No visible input after rename. Try clicking sidebar conv title...")
            # Maybe rename triggers by clicking the conversation title text
            await page.evaluate(f"""() => {{
                const a = document.querySelector('a[href*="/app/{convs[1]['id']}"]');
                if (!a) return;
                // Click the title text within the sidebar entry
                const titleDiv = a.querySelector('[class*="title"], div');
                if (titleDiv) titleDiv.click();
            }}""")
            await page.keyboard.press("Enter")  # maybe triggers edit mode?
            await asyncio.sleep(1)

            editables2 = await page.evaluate("""() => {
                const result = [];
                const eds = document.querySelectorAll('[contenteditable="true"], input');
                for (const e of eds) {
                    if (e.offsetParent !== null) {
                        result.push({
                            tag: e.tagName,
                            text: e.textContent?.trim()?.substring(0, 40) || e.value?.substring(0, 40),
                            class: e.className?.substring(0, 60)
                        });
                    }
                }
                return result;
            }""")
            print(f"  After click: {json.dumps(editables2, ensure_ascii=False)}")

        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
