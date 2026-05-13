"""
Explore Gemini UI: find rename elements, context menus, edit/pencil icons.
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

        # Wait for login
        body = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            print("Waiting sign-in...")
            for _ in range(60):
                await asyncio.sleep(1)
                if "登录" not in await page.inner_text("body"): break

        print(f"URL: {page.url}")

        # Click first conversation
        print("\n[1] Click first conversation...")
        conv = await page.evaluate("""() => {
            const a = document.querySelector('a[href*="/app/"]');
            if (!a) return null;
            a.click();
            return { href: a.getAttribute('href'), title: a.textContent?.trim() };
        }""")
        print(f"  Clicked: {json.dumps(conv, ensure_ascii=False)}")
        await asyncio.sleep(3)

        # Explore conversation header area for rename UI
        print("\n[2] Search rename UI elements...")
        ui = await page.evaluate("""() => {
            const results = [];

            // 1. Look for edit/pencil icons in SVG namespace
            const allSvgs = document.querySelectorAll('svg');
            for (const svg of allSvgs) {
                const parent = svg.closest('[role="button"], button, [role="menuitem"], [tabindex]');
                if (parent) {
                    const label = parent.getAttribute('aria-label') || parent.textContent?.trim() || '';
                    if (label.toLowerCase().includes('rename') || label.toLowerCase().includes('edit') || label.toLowerCase().includes('重命名') || label.toLowerCase().includes('编辑')) {
                        results.push({ type: 'edit-icon', label, tag: parent.tagName, attrs: {role: parent.getAttribute('role'), 'aria-label': parent.getAttribute('aria-label')} });
                    }
                }
                // Check title attr too
                const title = svg.getAttribute('title') || '';
                if (title.toLowerCase().includes('rename') || title.toLowerCase().includes('edit') || title.toLowerCase().includes('重命名')) {
                    results.push({ type: 'svg-title', title, parentTag: svg.parentElement?.tagName });
                }
            }

            // 2. Check for context menu / dropdown buttons near conversation title
            const titleArea = document.querySelector('h1, h2, [class*="title"], [class*="header"], [class*="heading"]');
            if (titleArea) {
                const siblings = titleArea.parentElement?.querySelectorAll('[role="button"], button, [role="menuitem"], [class*="menu"], [class*="more"], [class*="action"]') || [];
                for (const el of siblings) {
                    results.push({ type: 'title-area-button', text: el.textContent?.trim()?.substring(0, 30), tag: el.tagName, role: el.getAttribute('role'), 'aria-label': el.getAttribute('aria-label') });
                }
            }

            // 3. Find all clickable elements near top/header
            const headerRegion = document.querySelector('[class*="header"], [class*="Header"], header, [class*="topbar"], [class*="toolbar"], [class*="nav"]');
            if (headerRegion) {
                const buttons = headerRegion.querySelectorAll('[role="button"], button');
                for (const btn of buttons) {
                    results.push({ type: 'header-button', text: btn.textContent?.trim()?.substring(0, 30), tag: btn.tagName, 'aria-label': btn.getAttribute('aria-label') });
                }
            }

            // 4. Try to find the conversation title element itself and its container
            const titleEl = document.querySelector('h1');
            if (titleEl) {
                const container = titleEl.parentElement;
                results.push({ type: 'title-container', html: container.innerHTML.substring(0, 300) });
            }

            // 5. Search for data-testid or testid attributes
            const allElements = document.querySelectorAll('[data-testid], [data-test-id]');
            for (const el of allElements) {
                const tid = el.getAttribute('data-testid') || el.getAttribute('data-test-id') || '';
                if (tid.toLowerCase().includes('rename') || tid.toLowerCase().includes('edit') || tid.toLowerCase().includes('title')) {
                    results.push({ type: 'testid', testid: tid, text: el.textContent?.trim()?.substring(0, 30) });
                }
            }

            // 6. Search by text content
            const walker = document.createTreeWalker(document.body, 4, null, false);
            let node;
            while (node = walker.nextNode()) {
                const t = node.textContent?.trim() || '';
                if ((t === '重命名' || t === 'Rename' || t === 'Edit' || t === '编辑') && node.parentElement) {
                    results.push({ type: 'text-match', text: t, parentTag: node.parentElement.tagName, parentClass: node.parentElement.className?.substring(0, 100) });
                }
            }

            return results;
        }""")
        print(f"  Found {len(ui)} elements:")
        for u in ui:
            print(f"    {json.dumps(u, ensure_ascii=False)[:150]}")

        # If no rename UI found, try right-click context menu
        if not any(r.get("type") in ("edit-icon", "text-match") for r in ui):
            print("\n[3] Try right-click on conversation in sidebar...")
            rcm = await page.evaluate("""() => {
                const a = document.querySelector('a[href*="/app/"]');
                if (!a) return null;
                const rect = a.getBoundingClientRect();
                return { x: rect.x + rect.width/2, y: rect.y + rect.height/2 };
            }""")
            if rcm:
                print(f"  Right-click at ({rcm['x']:.0f}, {rcm['y']:.0f})")
                await page.mouse.click(rcm["x"], rcm["y"], button="right")
                await asyncio.sleep(2)
                context_menu = await page.evaluate("""() => {
                    const menus = document.querySelectorAll('[role="menu"], [class*="menu"], [class*="popup"], [class*="dropdown"]');
                    const items = [];
                    for (const menu of menus) {
                        if (menu.offsetParent !== null) { // visible
                            const opts = menu.querySelectorAll('[role="menuitem"], [role="menuitemradio"], [tabindex]');
                            for (const opt of opts) {
                                items.push({ text: opt.textContent?.trim()?.substring(0, 50), tag: opt.tagName, role: opt.getAttribute('role') });
                            }
                        }
                    }
                    return items;
                }""")
                if context_menu:
                    print(f"  Context menu items:")
                    for item in context_menu:
                        print(f"    {json.dumps(item, ensure_ascii=False)}")
                else:
                    print("  No visible context menu found")

        # Also try to find the conversation entry with more actions
        print("\n[4] Search sidebar entry for more-actions button...")
        more = await page.evaluate("""() => {
            const results = [];
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const container = a.parentElement;
                if (!container) continue;
                // Look for sibling buttons (three-dot menu, etc)
                const btns = container.querySelectorAll('[role="button"], button, [class*="more"], [class*="action"]');
                for (const btn of btns) {
                    results.push({
                        text: btn.textContent?.trim()?.substring(0, 30),
                        html: btn.innerHTML?.substring(0, 100),
                        aria: btn.getAttribute('aria-label')
                    });
                }
            }
            // Also try the more general sidebar container
            const sidebar = document.querySelector('[class*="sidebar"], [class*="Sidebar"], nav, [class*="nav"]');
            if (sidebar) {
                const btns = sidebar.querySelectorAll('[role="button"], button');
                for (const btn of btns) {
                    const label = btn.getAttribute('aria-label') || btn.textContent?.trim() || '';
                    if (label && !results.some(r => r.text === label.substring(0, 30))) {
                        results.push({
                            text: label.substring(0, 30),
                            html: btn.innerHTML?.substring(0, 80),
                            aria: btn.getAttribute('aria-label')
                        });
                    }
                }
            }
            return results;
        }""")
        if more:
            print(f"  Sidebar action buttons:")
            for m in more:
                print(f"    {json.dumps(m, ensure_ascii=False)[:120]}")

        # Try hovering then checking for tooltip/rename
        print("\n[5] Hover on conversation title (h1)...")
        title_info = await page.evaluate("""() => {
            const h1 = document.querySelector('h1');
            if (!h1) return null;
            const rect = h1.getBoundingClientRect();
            return { x: rect.x, y: rect.y, w: rect.width, h: rect.height, text: h1.textContent?.trim() };
        }""")
        if title_info:
            print(f"  Title: '{title_info['text']}' at ({title_info['x']:.0f}, {title_info['y']:.0f})")
            await page.mouse.move(title_info["x"] + title_info["w"]/2, title_info["y"] + title_info["h"]/2)
            await asyncio.sleep(1.5)
            hover_ui = await page.evaluate("""() => {
                const results = [];
                const h1 = document.querySelector('h1');
                if (!h1) return [];
                const container = h1.parentElement;
                if (container) {
                    const buttons = container.querySelectorAll('[role="button"], button, [class*="icon"], [class*="btn"], svg');
                    for (const btn of buttons) {
                        if (btn.offsetParent !== null) {
                            results.push({
                                tag: btn.tagName,
                                text: btn.textContent?.trim()?.substring(0, 30),
                                aria: btn.getAttribute('aria-label'),
                                class: btn.className?.substring(0, 80),
                                visible: true
                            });
                        }
                    }
                }
                return results;
            }""")
            if hover_ui:
                print(f"  Hover-visible elements:")
                for h in hover_ui:
                    print(f"    {json.dumps(h, ensure_ascii=False)[:120]}")
            else:
                print("  No hover-visible buttons near title")

        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
