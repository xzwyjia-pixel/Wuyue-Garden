"""
Check Gemini conversation state: list test-prefixed convs.
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
                    seen.add(m[1]);
                    items.push({id:m[1], title:t.substring(0, 60)});
                }
            }
            return items;
        }""")
        print(f"Total: {len(convs)} convs")

        test_prefixed = [c for c in convs if c['title'].startswith('[TEST]') or c['title'].startswith('[TST]') or c['title'].startswith('[DEV]')]
        print(f"\nTest/DEV prefixed: {len(test_prefixed)}")
        for c in test_prefixed:
            print(f"  {c['id']:20s} '{c['title']}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
