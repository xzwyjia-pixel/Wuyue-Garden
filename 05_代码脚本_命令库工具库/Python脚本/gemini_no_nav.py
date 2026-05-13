"""
No navigation. Extract params from existing page state.
"""
import asyncio, json, urllib.parse, re
from playwright.async_api import async_playwright

BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9229")
        ctx = browser.contexts[0]
        page = ctx.pages[0]
        await asyncio.sleep(3)

        # Get params from page evaluate (JS globals)
        print("[获取] 页面参数...")
        params = await page.evaluate("""() => {
            const r = {};
            // Try to find XSRF/at token from various places
            try {
                // Search for batchexecute config
                const scripts = document.querySelectorAll('script[nonce]');
                for (const s of scripts) {
                    const t = s.textContent || '';
                    if (t.includes('batchexecute') || t.includes('f.sid')) {
                        // Extract f.sid
                        const fsid = t.match(/"f.sid":"([^"]+)"/);
                        if (fsid) r.fsid = fsid[1];
                        const bl = t.match(/"bl":"([^"]+)"/);
                        if (bl) r.bl = bl[1];
                        const at = t.match(/"at":"([^"]+)"/);
                        if (at) r.at = at[1];
                        break;
                    }
                }

                // Try WIZ_global_data
                if (window.WIZ_global_data) {
                    const gd = window.WIZ_global_data;
                    r.wizKeys = Object.keys(gd).filter(k => k.includes('sid') || k.includes('token') || k.includes('auth'));
                }

                // Search all script tags for at token
                for (const s of document.querySelectorAll('script')) {
                    if (s.textContent && s.textContent.includes('"SNlM0e"')) {
                        const m = s.textContent.match(/"SNlM0e"\s*:\s*"([^"]+)"/);
                        if (m) r.SNlM0e = m[1];
                    }
                    if (s.textContent && s.textContent.includes('"batchexecute"')) {
                        r.hasBatchUrl = true;
                        // Try to find the full batch URL
                        const urlMatch = s.textContent.match(/"batchexecute"\s*:\s*"[^"]*bardchat[^"]*"/i);
                        if (urlMatch) r.batchUrl = urlMatch[0];
                    }
                }
            } catch(e) { r.error = e.message; }
            return r;
        }""")
        print(json.dumps(params, indent=2, ensure_ascii=False))

        # Try getting cookies
        cookies = await page.evaluate("() => document.cookie")
        print(f"\nCookies: {cookies}")

        # Try getting at from performance API (captured requests)
        perf_data = await page.evaluate("""() => {
            try {
                const entries = performance.getEntriesByType('resource');
                const batchUrls = entries.filter(e => e.name.includes('batchexecute'));
                return batchUrls.slice(0, 3).map(e => ({
                    url: e.name.substring(0, 200),
                    duration: e.duration,
                }));
            } catch(e) { return []; }
        }""")
        if perf_data:
            print(f"\nPerformance API (batchexecute URLs):")
            for e in perf_data:
                print(f"  {e['url']}")
                # Extract at from URL
                if "&at=" in e['url']:
                    at_match = re.search(r'&at=([^&]+)', e['url'])
                    if at_match:
                        print(f"  >>> at: {at_match.group(1)[:40]}...")

        # Extract f.sid from the first URL
        for e in perf_data:
            parsed = urllib.parse.urlparse(e['url'])
            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("f.sid"):
                fsid = qs["f.sid"][0]
                bl = qs.get("bl", [""])[0]
                print(f"\nFound f.sid: {fsid}")
                print(f"Found bl: {bl}")

                # Build parameters
                base_p = {"rpcids":"MaZiqc","source-path":"/app","bl":bl,"f.sid":fsid,"hl":"zh-CN","rt":"c"}
                qs_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k,v in base_p.items())

                # Test MaZiqc list
                print(f"\n[测试] MaZiqc list [13,null,[0,null,50]]")
                rpc_call = json.dumps([["MaZiqc", "[13,null,[0,null,50]]", None, "generic"]])
                body_str = f"f.req={urllib.parse.quote(rpc_call)}&at=PLACEHOLDER"

                # Wait, we need at token. Let me try to get it from the page's fetch helper
                # Actually, let me use the gemini API directly via evaluate
                result = await page.evaluate("""async (urlBase, qs) => {
                    const url = urlBase + '?' + qs + '&_reqid=' + Date.now();
                    // Try with empty at first
                    try {
                        const resp = await fetch(url, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
                            body: 'f.req=' + encodeURIComponent(JSON.stringify([["MaZiqc","[13,null,[0,null,50]]",null,"generic"]]))
                        });
                        const text = await resp.text();
                        return {ok: resp.ok, status: resp.status, text: text.substring(0, 300)};
                    } catch(e) { return {ok:false, error: e.message}; }
                }""", [BATEXECUTE, qs_str])
                print(f"  结果: {json.dumps(result, ensure_ascii=False)[:300]}")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
