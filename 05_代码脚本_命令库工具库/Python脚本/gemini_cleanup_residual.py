"""
Clean residual test names: find "UI rename capture" convs, remove that text.
"""
import asyncio, re
from playwright.async_api import async_playwright

CDP_PORT = 9229

async def rename_conv(page, conv_id, new_title):
    await page.evaluate(f"""() => {{
        const a = document.querySelector('a[href*="/app/{conv_id}"]');
        if (a) {{ a.scrollIntoView({{block: 'center'}}); a.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}})); }}
    }}""")
    await asyncio.sleep(0.8)
    btn = await page.evaluate(f"""() => {{
        const a = document.querySelector('a[href*="/app/{conv_id}"]');
        const parent = (a?.closest('div, li') || a?.parentElement);
        const btn = parent?.querySelector('[data-test-id="actions-menu-button"]');
        if (!btn || btn.getBoundingClientRect().width === 0) return null;
        const r = btn.getBoundingClientRect(); return {{x: r.x + r.width/2, y: r.y + r.height/2}};
    }}""")
    if not btn: return False
    await page.mouse.click(btn["x"], btn["y"])
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
    await page.keyboard.type(new_title, delay=20)
    await asyncio.sleep(0.3)
    await page.keyboard.press("Enter")
    await asyncio.sleep(2)
    return True

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

        convs = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) {
                    seen.add(m[1]); items.push({id:m[1], title:t.substring(0,80)});
                }
            }
            return items;
        }""")

        targets = [(c["id"], c["title"]) for c in convs if "UI rename capture" in c["title"]]
        if not targets:
            print("No residual names found")
            await browser.close()
            return

        for conv_id, title in targets:
            new_title = re.sub(r'UI rename capture \d+\s*', '', title).strip()
            print(f"Clean: '{title[:50]}' -> '{new_title[:50]}'")
            ok = await rename_conv(page, conv_id, new_title)
            print(f"  {'OK' if ok else 'FAIL'}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
