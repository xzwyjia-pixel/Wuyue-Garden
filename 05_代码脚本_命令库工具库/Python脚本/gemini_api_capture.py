"""
Gemini rename API 抓包 — 等 120 秒让用户手动操作
"""
import asyncio, sys, json, re
from playwright.async_api import async_playwright

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
CDP_PORT = 9229
GEMINI_URL = "https://gemini.google.com/app"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        page = browser.contexts[0].pages[0]
        if "gemini" not in page.url:
            await page.goto(GEMINI_URL, timeout=30000)
        await asyncio.sleep(3)

        # 检查登录
        body = await page.inner_text("body")
        if "登录" in body:
            print("[等待登录]")
            for _ in range(120):
                await asyncio.sleep(1)
                if "登录" not in await page.inner_text("body"):
                    break

        captured = []

        # 用 route 拦截才能读到完整 body
        async def on_route(route):
            req = route.request
            url = req.url
            if "/batchexecute" in url:
                pd = route.request.post_data
                body = (await pd() if callable(pd) else pd) or ""
                method = req.method
                hdrs = {k: v for k, v in dict(req.headers).items() if k in ("content-type",)}
                captured.append({"url": url, "method": method, "body": body[:3000], "headers": hdrs})
                print(f"\n[REQ] {method} {url[:80]}")
                print(f"  body: {body[:500]}")
            await route.continue_()

        await page.route("**/batchexecute**", on_route)

        async def on_response(resp):
            url = resp.url
            if "/batchexecute" in url:
                try:
                    body = await resp.text()
                except:
                    body = ""
                print(f"[RESP] {resp.status}")
                print(f"  body: {body[:400]}")

        page.on("response", on_response)

        print("=" * 60)
        print("请在打开的 Chrome 中操作:")
        print("1. 找到一条对话 → 右键 Rename → 改成 `[TEST] xxx`")
        print("2. 按回车确认")
        print("3. 看这里输出的 API 请求信息")
        print("=" * 60)

        await asyncio.sleep(120)

        print(f"\n\n=== 共捕获 {len(captured)} 个请求 ===")
        for i, c in enumerate(captured):
            print(f"\n--- {i+1} ---")
            print(f"URL: {c['url']}")
            print(f"Method: {c['method']}")
            if c['headers']:
                print(f"Headers: {json.dumps(c['headers'], ensure_ascii=False)}")
            if c['body']:
                try:
                    parsed = json.loads(c['body'])
                    print(f"Body (JSON): {json.dumps(parsed, ensure_ascii=False)[:500]}")
                except:
                    print(f"Body (raw): {c['body'][:500]}")

        json.dump(captured, open("gemini_api_capture.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("\n已保存: gemini_api_capture.json")


if __name__ == "__main__":
    asyncio.run(main())
