"""
Quick debug: extract at token and conversation data from Gemini page state.
"""
import asyncio, json, re
from playwright.async_api import async_playwright

CDP_PORT = 9229

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(3)

        # Wait for login
        body = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            print("[等待] Login required...")
            for _ in range(60):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt:
                    break

        # Try various methods to extract at token
        print("\n=== Method 1: page.evaluate cookie/localStorage ===")
        cookies = await page.evaluate("""() => {
            const results = {};
            try {
                // Check for auth cookies
                const allCookies = document.cookie.split(';').map(c => c.trim());
                results.cookies = allCookies.filter(c => c.includes('auth') || c.includes('token') || c.includes('sid') || c.includes('AT'));
                // Check sessionStorage
                results.sessionKeys = Object.keys(sessionStorage).filter(k => k.includes('token') || k.includes('auth') || k.includes('at'));
                // Check localStorage
                results.localKeys = Object.keys(localStorage).filter(k => k.includes('token') || k.includes('auth') || k.includes('at'));
                for (const key of results.localKeys) {
                    results[key] = localStorage.getItem(key)?.substring(0, 100);
                }
            } catch(e) { results.error = e.message; }
            return results;
        }""")
        print(json.dumps(cookies, indent=2, ensure_ascii=False))

        print("\n=== Method 2: Intercept a batchexecute request ===")
        captured = {}

        async def on_request(req):
            if "/batchexecute" in req.url:
                try:
                    post_data = req.post_data if isinstance(req.post_data, str) else None
                    headers = req.headers if isinstance(req.headers, dict) else {}
                    captured[req.url[:150]] = {
                        "url_at": "at=" in req.url,
                        "post_len": len(post_data) if post_data else 0,
                        "has_at_in_post": "at=" in post_data if post_data else False,
                        "has_freq": "f.req=" in post_data if post_data else False,
                        "content_type": headers.get("content-type", ""),
                    }
                    if post_data and "at=" in post_data:
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(post_data)
                        captured[req.url[:150]]["at_token_found"] = parsed.get("at", [""])[0][:50]
                except Exception as e:
                    captured[req.url[:150]] = {"error": str(e)}

        page.on("request", on_request)

        # Refresh to trigger requests
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(8)

        print(f"Captured {len(captured)} batchexecute requests:")
        for url, info in list(captured.items())[:10]:
            print(f"  {info}")
            if "at_token_found" in info:
                print(f"  >>> AT TOKEN: {info['at_token_found']}")

        if not any("at_token_found" in v for v in captured.values()):
            print("\n=== Method 3: Try from page local data ===")
            # Look for __INITIAL_STATE__ or similar
            page_data = await page.evaluate("""() => {
                const results = {};
                // Search common globals
                const keys = ['__INITIAL_STATE__', '__DATA__', '__NEXT_DATA__', '__NUXT__', 'initialState'];
                for (const k of keys) {
                    try {
                        const v = window[k];
                        if (v) results[k] = JSON.stringify(v).substring(0, 500);
                    } catch(e) {}
                }
                // Search for at= in script content
                const scripts = document.querySelectorAll('script');
                for (const s of scripts) {
                    if (s.textContent && s.textContent.includes('"at"')) {
                        const match = s.textContent.match(/"at"\s*:\s*"([^"]+)"/);
                        if (match) results['script_at'] = match[1].substring(0, 50);
                    }
                }
                return results;
            }""")
            print(json.dumps(page_data, indent=2, ensure_ascii=False))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
