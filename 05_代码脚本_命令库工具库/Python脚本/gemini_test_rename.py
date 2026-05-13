"""
Test: can we rename using short c_xxx token, or do we need long token?
"""
import asyncio, json, urllib.parse, sys
from pathlib import Path
from playwright.async_api import async_playwright

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"
PARENT_DIR = Path(__file__).resolve().parent

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

        # Get at token
        print("[获取] at token...")
        at_token = None
        future = asyncio.get_event_loop().create_future()
        async def on_req(req):
            if future.done(): return
            if "/batchexecute" in req.url:
                pd = req.post_data
                if isinstance(pd, str) and "at=" in pd:
                    parsed = urllib.parse.parse_qs(pd)
                    if "at" in parsed and parsed["at"][0]:
                        future.set_result(parsed["at"][0])
        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(5)
        try:
            at_token = await asyncio.wait_for(future, timeout=10)
            print(f"  at: {at_token[:40]}...")
        except asyncio.TimeoutError:
            print("  [FAIL] no at token")
            return
        finally:
            page.remove_listener("request", on_req)

        # Get a conversation ID from sidebar
        sidebar = await page.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="/app/"]');
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const text = a.textContent?.trim() || '';
                const m = href.match(/\\/app\\/([^?&#]+)/);
                if (m && text.length > 1) return { convId: m[1], title: text };
            }
            return null;
        }""")

        if not sidebar:
            print("[FAIL] no sidebar items")
            return

        conv_id = sidebar["convId"]
        print(f"\n[测试 1] 用 short token ({conv_id}) 改名...")
        test_title = f"[TEST] {sidebar['title']}"
        rpc_params = json.dumps([20, conv_id, test_title])
        rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url + '?rpcids=MaZiqc&source-path=%2Fapp&hl=zh-CN&rt=c', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body,
                });
                const text = await resp.text();
                return { ok: resp.ok, status: resp.status, text: text.substring(0, 500) };
            } catch (e) {
                return { ok: false, error: e.message };
            }
        }""", [BATEXECUTE, body_str])

        print(f"  ok: {result.get('ok')}, status: {result.get('status')}")
        if result.get("text"):
            print(f"  响应: {result['text'][:300]}")

        # Rename it back
        if result.get("ok"):
            print(f"\n[测试 2] 恢复原名...")
            rpc_params2 = json.dumps([20, conv_id, sidebar["title"]])
            rpc_call2 = json.dumps([["MaZiqc", rpc_params2, None, "generic"]])
            body_str2 = f"f.req={urllib.parse.quote(rpc_call2)}&at={urllib.parse.quote(at_token)}"
            result2 = await page.evaluate("""async (url, body) => {
                try {
                    const resp = await fetch(url + '?rpcids=MaZiqc&source-path=%2Fapp&hl=zh-CN&rt=c', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                        body: body,
                    });
                    const text = await resp.text();
                    return { ok: resp.ok, status: resp.status, text: text.substring(0, 200) };
                } catch (e) {
                    return { ok: false, error: e.message };
                }
            }""", [BATEXECUTE, body_str2])
            print(f"  恢复: ok={result2.get('ok')}")

        print("\n[结果] short token rename: ", "✓ 可行" if result.get("ok") else "✗ 不可行")

if __name__ == "__main__":
    asyncio.run(main())
