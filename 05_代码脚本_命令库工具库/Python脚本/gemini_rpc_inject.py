"""
Inject rename requests via page's OWN RPC mechanism.
GWS (Google Web Server) batchexecute uses a specific API on window or document.
"""
import asyncio, json, sys, time
from pathlib import Path
from playwright.async_api import async_playwright

CDP_PORT = 9229

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Check if already on gemini
        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(3)

        body = await page.inner_text("body")
        if "登录" in body or "Sign in" in body:
            for _ in range(60):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt: break

        # Find page's RPC mechanism
        print("[查找] 页面 RPC 机制...")
        rpc_mechanism = await page.evaluate("""() => {
            const results = {};
            // Check for gapi.client
            if (typeof gapi !== 'undefined' && gapi.client) results.gapi = true;
            // Check for __googleRpc or similar
            for (const key of Object.keys(window)) {
                if (key.includes('Rpc') || key.includes('rpc') || key.includes('batch')) {
                    results[key] = typeof window[key];
                }
            }
            // Check for _BardChatUi or boq internals
            for (const key of Object.keys(window)) {
                if (key.includes('Bard') || key.includes('bard') || key.includes('Gemini') || key.includes('gemini')) {
                    try {
                        const val = window[key];
                        if (val && typeof val === 'object') {
                            const methods = Object.getOwnPropertyNames(val).filter(m => typeof val[m] === 'function').slice(0,5);
                            results[key] = { type: 'object', methods: methods };
                        }
                    } catch(e) {}
                }
            }
            // Check for _BARD_API_ or similar
            for (const key of ['_BARD_API_', '_gemini_', 'gemini_', 'bard_']) {
                if (window[key]) results[key + '_exists'] = true;
            }
            // Check the gws dispatcher pattern
            try {
                const scripts = document.querySelectorAll('script[nonce]');
                for (const s of scripts) {
                    if (s.textContent && s.textContent.includes('rpcids=')) {
                        results.has_rpcid_pattern = true;
                    }
                    if (s.textContent && s.textContent.includes('batchexecute')) {
                        results.has_batch = true;
                    }
                }
                // Try to find the RPC executor function
                // Common GWS pattern: window.gws_rpc or similar
                for (const key of Object.getOwnPropertyNames(window)) {
                    if (key.startsWith('gws') || key.startsWith('_gws') || key.startsWith('google')) {
                        const v = window[key];
                        if (v && typeof v === 'function' && v.toString().includes('batchexecute')) {
                            results['rpc_function'] = key;
                        }
                    }
                }
            } catch(e) {}
            return results;
        }""")
        print(json.dumps(rpc_mechanism, indent=2))

        # Get convIds from sidebar
        sidebar = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) { seen.add(m[1]); items.push({id:m[1],title:t}); }
            }
            return items;
        }""")
        print(f"\n侧边栏: {len(sidebar)} 条")

        # For each conversation, try to get name/rename via intercept
        # Intercept the hNvQHb response and extract long token
        print(f"\n[测试] 点开 '{sidebar[0]['title'][:30] if sidebar else 'N/A'}' ...")
        long_token = None
        fut = asyncio.get_event_loop().create_future()

        async def on_resp(resp):
            if fut.done(): return
            if "hNvQHb" in resp.url:
                try:
                    body = await resp.text()
                    import re
                    m = re.search(r't[A-Za-z0-9+/]{50,}={0,2}', body)
                    if m:
                        fut.set_result(m.group(0))
                except: pass

        page.on("response", on_resp)
        await page.evaluate("""() => document.querySelector('a[href*="/app/"]')?.click()""")
        try:
            long_token = await asyncio.wait_for(fut, timeout=10)
            print(f"  长 token 提取: {'成功' if long_token else '失败'}")
            if long_token:
                print(f"  token: {long_token[:60]}...")
        except asyncio.TimeoutError:
            print("  hNvQHb 未捕获")

        if not long_token:
            # Try to extract from page JS state after clicking
            page_state = await page.evaluate("""() => {
                try {
                    // Search all window properties for long token pattern
                    const results = [];
                    for (const key of Object.keys(window)) {
                        try {
                            const v = JSON.stringify(window[key]);
                            const m = v.match(/t[A-Za-z0-9+/]{80,}={0,2}/);
                            if (m) results.push({key, token: m[0].substring(0, 60)});
                        } catch(e) {}
                    }
                    return results.slice(0, 5);
                } catch(e) { return []; }
            }""")
            if page_state:
                print(f"  JS state 中找到 {len(page_state)} 个 token:")
                for ps in page_state:
                    print(f"    {ps['key']}: {ps['token']}...")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
