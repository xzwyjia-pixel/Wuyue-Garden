"""
Minimal test: replicate exact Gemini batchexecute call including f.sid.
"""
import asyncio, json, urllib.parse, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

def parse_batch(body: str) -> list:
    body = re.sub(r"^\)\]}'\n?", "", body)
    chunks = []
    pos = 0
    while pos < len(body):
        m = re.match(r'\n(\d+)\n', body[pos:])
        if not m: break
        size = int(m.group(1))
        jstart = pos + m.end()
        jend = jstart + size
        try:
            chunks.append(json.loads(body[jstart:jend]))
        except json.JSONDecodeError:
            break
        pos = jend
    return chunks

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Capture ONE real batchexecute request to get exact URL format
        batch_urls = []

        async def on_req(req):
            if "/batchexecute" in req.url:
                batch_urls.append(req.url)

        page.on("request", on_req)

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(8)
        else:
            # Refresh to trigger requests
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(8)

        page.remove_listener("request", on_req)

        # Extract URL pattern from captured MaZiqc requests
        at_token = None
        maziqc_urls = [u for u in batch_urls if "MaZiqc" in u]
        print(f"批处理 URL 数: {len(batch_urls)}")
        print(f"MaZiqc URL 数: {len(maziqc_urls)}")

        for u in maziqc_urls:
            parsed = urllib.parse.urlparse(u)
            print(f"\n  完整URL: {u}")
            print(f"  查询参数: {urllib.parse.parse_qs(parsed.query)}")

        # Also capture POST body for at token
        body_text = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            pass  # already logged in

        # Now try replicating with captured URL params
        if maziqc_urls:
            url = maziqc_urls[0]
            # Extract all query params
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)

            # Build same URL but with our rpcids
            qs["rpcids"] = ["MaZiqc"]
            new_qs = "&".join(f"{k}={urllib.parse.quote(v[0])}" for k, v in qs.items())
            base_url = f"{BATEXECUTE}?{new_qs}"

            print(f"\n\n再生的 URL: {base_url}")

            # Get at token from cookie or request
            # Try page.evaluate cookies
            cookies = await page.evaluate("() => document.cookie")
            print(f"Cookies: {cookies}")

            # Try to extract at from the initial URL
            initial_urls = [u for u in batch_urls if "ESY5D" in u or "L5adhe" in u]
            for u in initial_urls[:1]:
                # Try getting post data
                pass

        # Try one more thing: extract the actual batchexecute base URL from a script
        script_data = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            for (const s of scripts) {
                if (s.textContent && s.textContent.includes('batchexecute') && s.textContent.includes('f.sid')) {
                    const m = s.textContent.match(/https:[^"']*batchexecute[^"']*/);
                    if (m) return m[0];
                    // Try finding config object with batchexecute
                    const m2 = s.textContent.match(/"batchexecuteBaseUrl"\s*:\s*"([^"]+)"/);
                    if (m2) return m2[1];
                    // Any reference to the endpoint
                    if (s.textContent.includes('BardChatUi/data/batchexecute')) {
                        return s.textContent.substring(0, 1000);
                    }
                }
            }
            return null;
        }""")
        if script_data:
            print(f"\n脚本中的 batch 配置: {script_data[:500]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
