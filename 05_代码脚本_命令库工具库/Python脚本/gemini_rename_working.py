"""
Working rename: 1) click conv → get long token from hNvQHb 2) call MaZiqc via page's internal dispatch.
"""
import asyncio, json, sys, time, re
from pathlib import Path
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

        print("[1] Try calling MaZiqc rename via page's internal RPC...")

        # Find the RPC function
        rpc_info = await page.evaluate("""() => {
            // Try default_BardChatUi methods
            for (const key of Object.keys(window)) {
                if (key.includes('BardChatUi') || key.includes('bard_chat')) {
                    const obj = window[key];
                    if (obj && typeof obj === 'object') {
                        for (const m of Object.getOwnPropertyNames(obj)) {
                            try {
                                const fn = obj[m];
                                if (typeof fn === 'function' && fn.toString().includes('batchexecute')) {
                                    return { object: key, method: m };
                                }
                            } catch(e) {}
                        }
                    }
                }
            }
            return null;
        }""")
        print(f"  RPC 函数: {rpc_info}")

        # Try intercepting hNvQHb to get long token, then call MaZiqc via page dispatch
        print("\n[2] 获取 convId + long token...")
        conv_id = None
        sidebar = await page.evaluate("""() => {
            const a = document.querySelector('a[href*="/app/"]');
            if (!a) return null;
            const m = a.getAttribute('href').match(/\\/app\\/([^?&#]+)/);
            return m ? { id: m[1], title: a.textContent?.trim() } : null;
        }""")
        if not sidebar:
            print("  无对话")
            return
        conv_id = sidebar["id"]
        print(f"  convId: {conv_id}")

        # Click to load, intercept hNvQHb
        long_token = None
        h_fut = asyncio.get_event_loop().create_future()
        async def on_resp(resp):
            if h_fut.done(): return
            if "hNvQHb" in resp.url:
                try:
                    body = await resp.text()
                    m = re.search(r't[A-Za-z0-9+/]{50,}={0,2}', body)
                    if m: h_fut.set_result(m.group(0))
                except: pass

        page.on("response", on_resp)
        await page.evaluate("""() => document.querySelector('a[href*="/app/"]')?.click()""")
        try: long_token = await asyncio.wait_for(h_fut, timeout=10)
        except: pass
        finally: page.remove_listener("response", on_resp)

        if not long_token:
            print("  FAIL: no long token")
            return
        print(f"  long: {long_token[:60]}...")

        # Try calling MaZiqc via page's internal dispatch
        print(f"\n[3] MaZiqc rename...")
        new_title = "[TEST] rename test via dispatch"
        result = await page.evaluate(f"""async () => {{
            try {{
                // Try all known BardChatUi methods
                const results = [];
                for (const key of Object.keys(window)) {{
                    if (key.includes('BardChatUi') || (key.includes('bard') && window[key] && typeof window[key] === 'object')) {{
                        const obj = window[key];
                        for (const m of Object.getOwnPropertyNames(obj)) {{
                            try {{
                                const fn = obj[m];
                                if (typeof fn === 'function') {{
                                    const s = fn.toString();
                                    if (s.includes('MaZiqc') || s.includes('batchexecute')) {{
                                        results.push({{key, method: m, src: s.substring(0, 200)}});
                                    }}
                                }}
                            }} catch(e) {{}}
                        }}
                    }}
                }}
                return results;
            }} catch(e) {{ return []; }}
        }}""")
        if result:
            print(f"  MaZiqc RPC 方法:")
            for r in result:
                print(f"    {r['key']}.{r['method']}: {r['src'][:120]}...")

        # Try calling the method directly
        for r in result[:2]:
            key, method = r["key"], r["method"]
            print(f"\n  调用 {key}.{method}('MaZiqc', ...)...")
            try:
                call_result = await page.evaluate(f"""async () => {{
                    try {{
                        const obj = window['{key}'];
                        const fn = obj['{method}'];
                        const r = await fn('MaZiqc', ['[20,"{long_token}","{new_title}"]', null, 'generic']);
                        return {{ok: true, result: JSON.stringify(r).substring(0, 200)}};
                    }} catch(e) {{ return {{ok: false, error: e.message, stack: e.stack?.substring(0, 200)}}; }}
                }}""")
                print(f"    {json.dumps(call_result, ensure_ascii=False)[:200]}")
            except Exception as e:
                print(f"    error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
