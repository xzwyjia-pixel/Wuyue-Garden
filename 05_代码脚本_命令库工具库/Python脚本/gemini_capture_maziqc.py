"""
Capture MaZiqc request params on page load.
Also test: can we open a conversation, get long token from hNvQHb, then rename?
"""
import asyncio, json, urllib.parse, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(3)

        body = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            print("[等待] 登录...")
            for _ in range(180):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt:
                    break

        # Capture ALL batchexecute requests AND responses
        print("[捕获] MaZiqc 请求/响应...")
        captured_reqs = []
        captured_resps = {}
        at_token = None

        async def on_req(req):
            nonlocal at_token
            if "/batchexecute" not in req.url:
                return
            pd = req.post_data
            if isinstance(pd, str):
                if "at=" in pd and not at_token:
                    parsed = urllib.parse.parse_qs(pd)
                    if "at" in parsed and parsed["at"][0]:
                        at_token = parsed["at"][0]
                if "MaZiqc" in pd:
                    try:
                        decoded = urllib.parse.parse_qs(pd)
                        freq = decoded.get("f.req", [""])[0]
                        if freq:
                            # Pretty print
                            params = json.loads(urllib.parse.unquote(freq))
                            captured_reqs.append({
                                "url": req.url[:200],
                                "params": params,
                                "params_pretty": json.dumps(params, ensure_ascii=False)[:500],
                            })
                    except Exception as e:
                        captured_reqs.append({"url": req.url[:200], "error": str(e)})

        async def on_resp(resp):
            if "/batchexecute" not in resp.url:
                return
            parsed = urllib.parse.urlparse(resp.url)
            qs = urllib.parse.parse_qs(parsed.query)
            rpcids = qs.get("rpcids", [])
            if "MaZiqc" in rpcids:
                try:
                    body = await resp.text()
                except:
                    return
                captured_resps[f"MaZiqc_{len(captured_resps)}"] = {
                    "url": resp.url[:200],
                    "body_len": len(body),
                    "body_preview": body[:500],
                }

        page.on("request", on_req)
        page.on("response", on_resp)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(10)

        print(f"\nat_token: {at_token[:40] if at_token else 'NONE'}...")
        print(f"\nMaZiqc 请求 ({len(captured_reqs)}):")
        for i, r in enumerate(captured_reqs):
            print(f"\n  [{i}] {r.get('params_pretty', r.get('error', '?'))[:500]}")

        print(f"\nMaZiqc 响应 ({len(captured_resps)}):")
        for k, v in captured_resps.items():
            print(f"\n  [{k}] len={v['body_len']}")
            print(f"  body: {v['body_preview'][:500]}")

        # Try clicking a conversation to see hNvQHb
        print(f"\n\n[测试] 点开第一个对话捕获 hNvQHb...")
        hnvqhb_resp = None
        future = asyncio.get_event_loop().create_future()

        async def on_h_resp(resp):
            if future.done(): return
            parsed = urllib.parse.urlparse(resp.url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "hNvQHb" in qs.get("rpcids", []):
                try:
                    body = await resp.text()
                    future.set_result({"body": body[:2000], "url": resp.url})
                except:
                    pass

        page.on("response", on_h_resp)

        await page.evaluate("""() => {
            const a = document.querySelector('a[href*="/app/"]');
            if (a) a.click();
        }""")

        try:
            hnvqhb_resp = await asyncio.wait_for(future, timeout=8)
            print(f"  hNvQHb captured! len={len(hnvqhb_resp['body'])}")
            # Show the raw body
            print(f"  raw: {hnvqhb_resp['body'][:500]}")
        except asyncio.TimeoutError:
            print("  no hNvQHb captured")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
