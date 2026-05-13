"""
Minimal: capture REAL at from POST body, test MaZiqc list + rename immediately.
"""
import asyncio, json, urllib.parse, re, time
from playwright.async_api import async_playwright

BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

def parse_batch(body):
    body = re.sub(r"^\)\]}'\n?", "", body)
    pos, chunks = 0, []
    while pos < len(body):
        m = re.match(r'\n(\d+)\n', body[pos:])
        if not m: break
        size = int(m.group(1)); js = pos + m.end(); je = js + size
        try: chunks.append(json.loads(body[js:je]))
        except: break
        pos = je
    return chunks

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9229")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Capture ALL params from a real request
        print("[捕获] 真实请求参数...")
        real = {}

        async def on_req(req):
            if "/batchexecute" not in req.url or real.get("done"):
                return
            pd = req.post_data
            if isinstance(pd, str) and "at=" in pd:
                parsed = urllib.parse.parse_qs(pd)
                if "at" in parsed:
                    real["at"] = parsed["at"][0]
                    real["url"] = req.url
                    real["done"] = True

        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(8)
        page.remove_listener("request", on_req)

        if not real.get("at"):
            print("[FAIL] no at")
            return

        at = real["at"]
        pq = urllib.parse.parse_qs(urllib.parse.urlparse(real["url"]).query)
        fsid, bl = pq.get("f.sid",[""])[0], pq.get("bl",[""])[0]

        # Get last _reqid from performance API
        perf = await page.evaluate("""() => {
            try {
                const entries = performance.getEntriesByType('resource');
                const batchEntries = entries.filter(e => e.name.includes('batchexecute'));
                if (batchEntries.length > 0) {
                    const last = batchEntries[batchEntries.length - 1].name;
                    const m = last.match(/[?&]_reqid=(\d+)/);
                    return m ? parseInt(m[1]) : 0;
                }
            } catch(e) {}
            return 0;
        }""") or 0
        req_id = perf or int(time.time()*1000) % 10000000

        print(f"at: {at[:40]}...")
        print(f"f.sid: {fsid}")
        print(f"_reqid start: {req_id}")

        # Test: MaZiqc list recent
        req_id += 100000
        qs = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={req_id}&rt=c"
        rpc_call = json.dumps([["MaZiqc", "[13,null,[0,null,1]]", None, "generic"]])
        body = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                const t = await r.text(); return {ok:r.ok, text:t};
            } catch(e) { return {ok:false, error:e.message}; }
        }""", [f"{BATEXECUTE}?{qs}", body])

        if result.get("ok"):
            chunks = parse_batch(result["text"])
            if chunks and len(chunks[0]) > 0 and isinstance(chunks[0][0], list) and len(chunks[0][0]) > 2:
                inner = json.loads(chunks[0][0][2])
                convs = inner[2] if len(inner) > 2 and isinstance(inner[2], list) else []
                print(f"\n[列表] {len(convs)} 条:")
                for c in convs[:10]:
                    long_tok = c[0] if len(c) > 0 and len(str(c[0])) > 20 else None
                    title = str(c[1]) if len(c) > 1 else "?"
                    print(f"  tok={'长' if long_tok else '短'} {str(c[0])[:30]:30s} {title[:60]}")
            else:
                print(f"\n[列表] parse error, raw: {result['text'][:300]}")
        else:
            print(f"\n[列表] HTTP error")

        # If MaZiqc [13] returned long tokens, use one for rename test
        # Otherwise, intercept a hNvQHb response

        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
