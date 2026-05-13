"""
Working UI-driven rename. Flow:
1. Hover sidebar conv → click actions-menu-button
2. Click "重命名" menu item
3. Find the visible mat-mdc-input-element (rename input)
4. Clear + type new name + Enter
5. Verify + capture batchexecute call
"""
import asyncio, json, urllib.parse, re
from playwright.async_api import async_playwright

CDP_PORT = 9229

async def rename_conv(page, conv_id, new_title):
    """Rename one conversation via UI. Returns (success, new_sidebar_title, captured_rpc)."""
    captured = []

    async def on_req(req):
        if "/batchexecute" in req.url:
            try:
                pd = req.post_data
                if pd:
                    captured.append({"url": req.url, "body": pd[:1000]})
            except: pass

    page.on("request", on_req)

    # Scroll into view
    await page.evaluate(f"""() => {{
        const a = document.querySelector('a[href*="/app/{conv_id}"]');
        if (a) a.scrollIntoView({{block: 'center'}});
    }}""")
    await asyncio.sleep(0.3)

    # Hover + click actions menu button
    menu_clicked = await page.evaluate(f"""() => {{
        const a = document.querySelector('a[href*="/app/{conv_id}"]');
        if (!a) return false;
        a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
        const parent = a.closest('div, li') || a.parentElement;
        const btn = parent?.querySelector('[data-test-id="actions-menu-button"]');
        if (!btn) return false;
        const rect = btn.getBoundingClientRect();
        if (rect.width === 0) return false;
        btn.click();
        return true;
    }}""")
    if not menu_clicked:
        page.remove_listener("request", on_req)
        return False, None, captured
    await asyncio.sleep(0.8)

    # Click "重命名" menu item
    rename_clicked = await page.evaluate("""() => {
        const menus = document.querySelectorAll('[role="menu"], .mat-mdc-menu-panel, .cdk-overlay-pane');
        for (const menu of menus) {
            if (menu.offsetParent === null) continue;
            const items = menu.querySelectorAll('[role="menuitem"], button, [mat-menu-item]');
            for (const item of items) {
                const text = item.textContent?.trim() || '';
                if (text.includes('重命名') || text.includes('Rename')) {
                    item.click();
                    return true;
                }
            }
        }
        return false;
    }""")
    if not rename_clicked:
        page.remove_listener("request", on_req)
        return False, None, captured
    await asyncio.sleep(0.8)

    # Find the visible rename input
    input_found = await page.evaluate(f"""() => {{
        const inputs = document.querySelectorAll('input.mat-mdc-input-element');
        for (const inp of inputs) {{
            if (inp.offsetParent !== null) {{
                inp.value = '';
                inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                inp.dispatchEvent(new Event('focus', {{bubbles: true}}));
                // Store what we need for keyboard typing
                const rect = inp.getBoundingClientRect();
                inp.focus();
                return {{x: rect.x + rect.width/2, y: rect.y + rect.height/2, w: rect.width, h: rect.height}};
            }}
        }}
        return null;
    }}""")

    if not input_found:
        page.remove_listener("request", on_req)
        return False, None, captured

    # Type new title character by character
    await page.keyboard.type(new_title, delay=30)
    await asyncio.sleep(0.5)

    # Press Enter to confirm
    await page.keyboard.press("Enter")
    await asyncio.sleep(2)

    page.remove_listener("request", on_req)

    # Read new sidebar title
    new_sidebar_title = await page.evaluate(f"""() => {{
        const a = document.querySelector('a[href*="/app/{conv_id}"]');
        if (a) return a.textContent?.trim() || '';
        return null;
    }}""")

    return True, new_sidebar_title, captured


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

        # Get all convs
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) {
                    seen.add(m[1]); items.push({id:m[1], title:t.match(/^.{3,60}/)?.[0] || t.substring(0,40)});
                }
            }
            return items;
        }""")
        print(f"Total: {len(convs)} convs")

        # Test rename on first non-test conv
        test_title = f"[TEST] {convs[2]['title'][:35]}"
        print(f"\nRename '{convs[2]['title'][:40]}' → '{test_title}'")
        ok, result, captured = await rename_conv(page, convs[2]["id"], test_title)
        print(f"Result: OK={ok} sidebar='{result}'")

        # Check captured requests
        maziqc = [c for c in captured if "MaZiqc" in c.get("url", "")]
        print(f"\nMaZiqc calls: {len(maziqc)}")
        for c in maziqc:
            print(f"  URL: {c['url'][:200]}")
            if c.get("body"):
                print(f"  Body: {c['body'][:300]}")
        if not maziqc:
            print(f"  All captured:")
            for c in captured[:5]:
                print(f"    {c['url'][:150]} | body={c['body'][:100] if c.get('body') else 'NONE'}...")

        # Optionally set back
        if ok:
            print(f"\nRestoring '{convs[2]['title'][:40]}'...")
            ok2, _, _ = await rename_conv(page, convs[2]["id"], convs[2]["title"])
            print(f"Restore: OK={ok2}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
