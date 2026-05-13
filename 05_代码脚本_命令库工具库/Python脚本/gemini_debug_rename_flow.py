"""
Debug rename flow step by step with detailed logging.
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

        # Pick a conv without [TEST] prefix
        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1 && !t.includes('[TEST]')) {
                    seen.add(m[1]);
                    items.push({id:m[1], title:t.substring(0,50)});
                }
            }
            return items;
        }""")
        print(f"Found {len(convs)} non-test convs")
        if not convs:
            return

        target = convs[0]
        print(f"Target: '{target['title']}' (id={target['id']})")

        # STEP 1: Find the sidebar element and its structure
        print("\n[Step 1] Sidebar element structure:")
        struct = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (!a) return null;

            // Scroll into view
            a.scrollIntoView({{block: 'center'}});

            // Get full parent chain
            const chain = [];
            let el = a;
            for (let i = 0; i < 5 && el; i++) {{
                const tag = el.tagName;
                const cls = (el.className || '').substring(0, 60);
                const children = [];
                for (const child of el.children) {{
                    children.push({{tag: child.tagName, cls: (child.className || '').substring(0, 40), id: child.id, 'data-test-id': child.getAttribute('data-test-id')}});
                }}
                chain.push({{tag, cls, children: children.slice(0, 8), childCount: el.children.length}});
                el = el.parentElement;
            }}
            return chain;
        }}""")
        for level, s in enumerate(struct or []):
            print(f"  Level {level}: <{s['tag']}> class='{s['cls']}' children={s['childCount']}")
            for c in (s.get('children') or []):
                if c.get('data-test-id'):
                    print(f"    child: data-test-id='{c['data-test-id']}' <{c['tag']}>")

        # STEP 2: Dispatch mouseenter and check whether button appears
        print("\n[Step 2] Dispatch mouseenter...")
        await asyncio.sleep(0.5)
        await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (a) {{
                const evt = new MouseEvent('mouseenter', {{bubbles: true, cancelable: true}});
                a.dispatchEvent(evt);
            }}
        }}""")
        await asyncio.sleep(1)

        btn_visible = await page.evaluate(f"""() => {{
            const a = document.querySelector('a[href*="/app/{target['id']}"]');
            if (!a) return 'no a';
            const parent = a.closest('div, li') || a.parentElement;
            const btn = parent?.querySelector('[data-test-id="actions-menu-button"]');
            if (!btn) return 'no button';
            const rect = btn.getBoundingClientRect();
            return {{visible: rect.width > 0, x: rect.x, y: rect.y, w: rect.width, h: rect.height}};
        }}""")
        print(f"  Button after mouseenter: {json.dumps(btn_visible, ensure_ascii=False)}")

        if isinstance(btn_visible, dict) and btn_visible.get("visible"):
            # Click via mouse
            print(f"\n[Step 3] Click button at ({btn_visible['x'] + btn_visible['w']/2:.0f}, {btn_visible['y'] + btn_visible['h']/2:.0f})...")
            await page.mouse.click(
                btn_visible["x"] + btn_visible["w"]/2,
                btn_visible["y"] + btn_visible["h"]/2
            )
            await asyncio.sleep(1.5)

            # Check if menu appeared
            menu = await page.evaluate("""() => {
                const panels = document.querySelectorAll('.mat-mdc-menu-panel');
                for (const p of panels) {
                    if (p.offsetParent !== null) {
                        const items = [];
                        for (const btn of p.querySelectorAll('button')) {
                            items.push({
                                text: btn.textContent?.trim() || '',
                                raw: (btn.textContent || '').substring(0, 40)
                            });
                        }
                        return items;
                    }
                }
                // Try overlay
                const overlays = document.querySelectorAll('.cdk-overlay-pane');
                for (const ov of overlays) {
                    if (ov.offsetParent !== null) {
                        const items = [];
                        for (const btn of ov.querySelectorAll('button')) {
                            items.push({
                                text: btn.textContent?.trim() || '',
                                raw: (btn.textContent || '').substring(0, 40)
                            });
                        }
                        if (items.length) return items;
                    }
                }
                return null;
            }""")
            print(f"  Menu: {json.dumps(menu, ensure_ascii=False)}")

            if menu:
                # Find "重命名"
                rename_item = None
                for item in menu:
                    if "重命名" in item.get("text", ""):
                        rename_item = item
                        break

                if rename_item:
                    print(f"\n[Step 4] Click '重命名'...")
                    # Find and click the actual button element
                    await page.evaluate("""() => {
                        const panels = document.querySelectorAll('.mat-mdc-menu-panel, .cdk-overlay-pane');
                        for (const p of panels) {
                            if (p.offsetParent === null) continue;
                            const btns = p.querySelectorAll('button');
                            for (const btn of btns) {
                                if (btn.textContent?.includes('重命名')) {
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    }""")
                    await asyncio.sleep(1.5)

                    # Check for visible text input
                    inp_check = await page.evaluate("""() => {
                        const inputs = document.querySelectorAll('input');
                        const visible = [];
                        for (const inp of inputs) {
                            if (inp.offsetParent !== null) {
                                const rect = inp.getBoundingClientRect();
                                visible.push({
                                    type: 'input',
                                    value: inp.value?.substring(0, 40),
                                    class: inp.className?.substring(0, 80),
                                    rect: {x: ~~rect.x, y: ~~rect.y, w: ~~rect.width, h: ~~rect.height}
                                });
                            }
                        }
                        return visible;
                    }""")
                    print(f"  Visible inputs: {json.dumps(inp_check, ensure_ascii=False)}")

                    if inp_check:
                        # Find the rename input (should be near sidebar)
                        rename_inp = None
                        for inp in inp_check:
                            # Rename input is mat-mdc-input-element in sidebar area
                            if "mat-mdc-input" in inp.get("class", ""):
                                rename_inp = inp
                                break
                        if not rename_inp:
                            rename_inp = inp_check[0]

                        if rename_inp:
                            print(f"  Using input: {json.dumps(rename_inp, ensure_ascii=False)}")

                            # Clear and type
                            new_name = f"[TEST] {target['title'][:35]}"
                            print(f"  Typing: '{new_name}'")

                            await page.evaluate("""() => {
                                const inputs = document.querySelectorAll('input.mat-mdc-input-element');
                                for (const inp of inputs) {
                                    if (inp.offsetParent !== null) {
                                        inp.focus();
                                        inp.select();
                                        break;
                                    }
                                }
                            }""")
                            await asyncio.sleep(0.3)
                            await page.keyboard.type(new_name, delay=30)
                            await asyncio.sleep(0.5)
                            await page.keyboard.press("Enter")
                            await asyncio.sleep(2)

                            # Verify
                            new_title = await page.evaluate(f"""() => {{
                                const a = document.querySelector('a[href*="/app/{target['id']}"]');
                                if (a) return a.textContent?.trim() || '';
                                return null;
                            }}""")
                            print(f"  New sidebar title: '{new_title}'")

        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
