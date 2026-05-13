"""
Test full UI-driven rename flow: click menu → click rename → type → Enter.
Also capture the resulting batchexecute call.
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

        # Capture any batchexecute request during rename
        captured = []
        async def on_req(req):
            if "/batchexecute" in req.url:
                try:
                    pd = req.post_data
                    captured.append({
                        "url": req.url[:300],
                        "method": req.method,
                        "body": pd[:500] if pd else None
                    })
                except: pass

        page.on("request", on_req)

        # Get sidebar convs
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) { seen.add(m[1]); items.push({id:m[1],title:t, href:h}); }
            }
            return items;
        }""")
        print(f"\n[Setup] {len(convs)} conversations")

        # Pick first few convs for test
        test_convs = convs[:3]
        print(f"  Testing first {len(test_convs)}")

        for i, conv in enumerate(test_convs):
            print(f"\n--- Conv {i+1}: '{conv['title'][:40]}' ---")

            # Scroll to make this conversation visible
            visible = await page.evaluate(f"""() => {{
                const a = document.querySelector('a[href*="/app/{conv['id']}"]');
                if (!a) return false;
                a.scrollIntoView({{block: 'center'}});
                return true;
            }}""")
            await asyncio.sleep(0.5)

            # Find actions menu button — it's SIBLING of <a>, not child
            btn_pos = await page.evaluate(f"""() => {{
                const convEl = document.querySelector('a[href*="/app/{conv['id']}"]');
                if (!convEl) return null;
                // Hover on conversation to reveal the actions button
                convEl.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
                // Button is sibling in same container. Search parent.
                const parent = convEl.closest('div, li') || convEl.parentElement;
                if (!parent) return null;
                const btn = parent.querySelector('[data-test-id="actions-menu-button"]');
                if (!btn) return null;
                const rect = btn.getBoundingClientRect();
                return {{
                    x: rect.x + rect.width/2,
                    y: rect.y + rect.height/2,
                    w: rect.width,
                    h: rect.height,
                    inView: rect.top >= 0
                }};
            }}""")

            if not btn_pos or btn_pos.get("y", 0) < 0:
                btn_pos = await page.evaluate(f"""() => {{
                    const convEl = document.querySelector('a[href*="/app/{conv['id']}"]');
                    if (!convEl) return {{error: 'no conv el'}};
                    const parent = convEl.closest('div, li') || convEl.parentElement;
                    if (!parent) return {{error: 'no parent'}};
                    const btn = parent.querySelector('[data-test-id="actions-menu-button"]');
                    if (!btn) return {{error: 'no button'}};
                    const rect = btn.getBoundingClientRect();
                    if (rect.width === 0) return {{error: 'hidden'}};
                    return {{x: rect.x + rect.width/2, y: rect.y + rect.height/2}};
                }}""")

            print(f"  Button pos: {json.dumps(btn_pos, ensure_ascii=False)}")

            if not btn_pos or btn_pos.get("error"):
                print(f"  SKIP: {btn_pos}")
                continue

            # Click the actions menu button
            await page.mouse.click(btn_pos["x"], btn_pos["y"])
            await asyncio.sleep(1)

            # Find and click "重命名" (rename) in the menu
            rename_clicked = await page.evaluate("""() => {
                const menus = document.querySelectorAll('[role="menu"], .mat-mdc-menu-panel, .cdk-overlay-pane');
                for (const menu of menus) {
                    if (menu.offsetParent === null) continue;
                    const items = menu.querySelectorAll('[role="menuitem"], button, [mat-menu-item]');
                    for (const item of items) {
                        const text = item.textContent?.trim() || '';
                        if (text.includes('重命名') || text.includes('Rename') || text.includes('rename')) {
                            item.click();
                            return { clicked: true, text };
                        }
                    }
                }
                return { clicked: false, reason: 'no menu visible' };
            }""")
            print(f"  Rename click: {json.dumps(rename_clicked, ensure_ascii=False)}")
            await asyncio.sleep(1)

            # Check for rename input (inline edit or dialog)
            rename_ui = await page.evaluate("""() => {
                // Check for text inputs that appeared
                const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
                for (const inp of inputs) {
                    if (inp.offsetParent !== null && inp.classList.contains('mat-input-element')) {
                        return { type: 'input', placeholder: inp.getAttribute('placeholder') || '', value: inp.value };
                    }
                }
                // Check for contenteditable
                const editables = document.querySelectorAll('[contenteditable="true"]');
                for (const e of editables) {
                    if (e.offsetParent !== null) {
                        return { type: 'contenteditable', text: e.textContent?.trim() || '' };
                    }
                }
                // Check for inline edit near title
                const titleEl = document.querySelector('[data-testid="conversation-title"]');
                if (titleEl) {
                    const parent = titleEl.closest('[class*="title"], div');
                    if (parent) {
                        const inp = parent.querySelector('input, [contenteditable]');
                        if (inp && inp.offsetParent !== null) {
                            return { type: 'inline-edit', tag: inp.tagName, value: inp.value || inp.textContent };
                        }
                    }
                }
                // Check for any dialog
                const dialogs = document.querySelectorAll('[role="dialog"], .mat-mdc-dialog-container');
                for (const d of dialogs) {
                    if (d.offsetParent !== null) {
                        return { type: 'dialog', html: d.innerHTML.substring(0, 200) };
                    }
                }
                return null;
            }""")
            print(f"  Rename UI: {json.dumps(rename_ui, ensure_ascii=False)}")

            if rename_ui:
                # Type new name
                new_name = f"[TEST] {conv['title'][:30]}"
                print(f"  Typing: '{new_name}'")

                if rename_ui.get("type") in ("input", "inline-edit"):
                    # Clear and type
                    await page.evaluate(f"""() => {{
                        const inp = document.querySelector('input[type="text"], input:not([type])');
                        if (inp) {{
                            inp.value = '';
                            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        }}
                    }}""")
                    await asyncio.sleep(0.3)
                    await page.keyboard.type(new_name, delay=50)
                    await asyncio.sleep(0.5)
                    # Press Enter
                    await page.keyboard.press("Enter")

                elif rename_ui.get("type") == "contenteditable":
                    await page.evaluate(f"""() => {{
                        const e = document.querySelector('[contenteditable="true"]');
                        if (e) e.textContent = '';
                    }}""")
                    await asyncio.sleep(0.3)
                    await page.keyboard.type(new_name, delay=50)
                    await asyncio.sleep(0.5)
                    await page.keyboard.press("Enter")
                else:
                    print(f"  Unknown rename UI type: {rename_ui.get('type')}")

                await asyncio.sleep(2)

                # Check result
                new_title = await page.evaluate("""() => {
                    const h1 = document.querySelector('h1');
                    if (h1) return h1.textContent?.trim();
                    const title = document.querySelector('[data-testid="conversation-title"]');
                    if (title) return title.textContent?.trim();
                    return null;
                }""")
                print(f"  Result title: '{new_title}'")
            else:
                print(f"  No rename UI appeared after clicking '重命名'")

        # Show captured requests
        maziqc_reqs = [c for c in captured if "MaZiqc" in c.get("url", "")]
        print(f"\n=== Captured {len(maziqc_reqs)} MaZiqc requests ===")
        for i, c in enumerate(maziqc_reqs[:5]):
            print(f"\n  [{i}]")
            print(f"    URL: {c['url'][:250]}")
            if c.get("body"):
                print(f"    Body: {c['body'][:300]}")

        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
