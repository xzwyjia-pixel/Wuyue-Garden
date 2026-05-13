"""
Final test: batchexecute with SNlM0e (at) token.
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
        await asyncio.sleep(2)

        # Extract SNlM0e (at token), f.sid, bl from page
        params = await page.evaluate("""() => {
            const r = {};
            for (const s of document.querySelectorAll('script')) {
                const t = s.textContent || '';
                const m = t.match(/"SNlM0e":"([^"]+)"/);
                if (m) r.at = m[1];
            }
            try {
                const entries = performance.getEntriesByType('resource');
                for (const e of entries) {
                    if (e.name.includes('batchexecute') && e.name.includes('MaZiqc')) {
                        r.url = e.name;
                        break;
                    }
                }
                if (!r.url) {
                    for (const e of entries) {
                        if (e.name.includes('batchexecute')) {
                            r.url = e.name;
                            break;
                        }
                    }
                }
            } catch(e) {}
            return r;
        }""")

        if not params.get("at"):
            print("[FAIL] no SNlM0e")
            return

        at_token = params["at"]
        batch_url = params.get("url", "")

        # Extract f.sid and bl from URL
        parsed = urllib.parse.urlparse(batch_url)
        qs = urllib.parse.parse_qs(parsed.query)
        fsid = qs.get("f.sid", [""])[0]
        bl = qs.get("bl", [""])[0]

        print(f"at: {at_token[:40]}...")
        print(f"f.sid: {fsid}")
        print(f"bl: {bl}")

        req_id = 100000

        # Test 1: List pinned convs [13,null,[1,null,1]]
        req_id += 1
        params_qs = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={req_id}&rt=c"
        rpc_call = json.dumps([["MaZiqc", "[13,null,[1,null,1]]", None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{params_qs}", body_str])

        if result.get("ok"):
            chunks = parse_batch(result["text"])
            if chunks and len(chunks[0]) > 0 and len(chunks[0][0]) > 2:
                inner = json.loads(chunks[0][0][2])
                convs = inner[2] if len(inner) > 2 and isinstance(inner[2], list) else []
                print(f"\n[列表 固定] {len(convs)} 条:")
                for c in convs:
                    print(f"  {c[0][:30]:30s} {str(c[1])[:60]}")

        # Test 2: List recent [13,null,[0,null,1]]
        req_id += 1
        params_qs = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={req_id}&rt=c"
        rpc_call = json.dumps([["MaZiqc", "[13,null,[0,null,1]]", None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{params_qs}", body_str])

        if result.get("ok"):
            chunks = parse_batch(result["text"])
            if chunks and len(chunks[0]) > 0 and len(chunks[0][0]) > 2:
                inner = json.loads(chunks[0][0][2])
                convs = inner[2] if len(inner) > 2 and isinstance(inner[2], list) else []
                print(f"\n[列表 最近] {len(convs)} 条:")
                for c in convs[:5]:
                    print(f"  {c[0][:30]:30s} {str(c[1])[:60]}")
        else:
            print(f"\n[列表 最近] error: {result.get('status')} {result.get('text','')[:100]}")

        # Test 3: Rename with LONG token (known from earlier capture)
        req_id += 1
        params_qs = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={req_id}&rt=c"
        # This long token is from the earlier MaZiqc rename response
        long_token = "tCs0BAY3EoXxpjm3ZJ1eJpwywHl/c/RR2qJVFN3mDSK12x3yI36y3H0q7pvIiowWoQnFEDn8EXr2hCMiNjgKwajq3Cuh+vkwS5gYPW2rOiKbxqGZJaX2bMETNqv3g5UQ/XSwPfG8L5nEc8BS/qjVENngqhwAkEEv0i7e1wF5EKgjG+Nm6g8kEjgB5W4/o498ygcYJ/l3ZoyFY8hKQu6WhTpAL7pNe4ZKEabHRz4wdjX0e6KttM1o1fD6JDeqTu+7++Xde6i5J5vIZqFTpsUNFhBAC"
        rpc_params = json.dumps([20, long_token, "[TEST] na"])
        rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{params_qs}", body_str])

        if result.get("ok"):
            print(f"\n[改名 LONG TOKEN] OK! status: {result['status']}")
            print(f"  body: {result['text'][:200]}")
        else:
            print(f"\n[改名 LONG TOKEN] error: {result.get('status')} {result.get('text','')[:100]}")

        # Test 4: Rename with SHORT token (c_xxx)
        req_id += 1
        params_qs = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={req_id}&rt=c"
        rpc_params = json.dumps([20, "c_1e571b3941650ebe", "[TEST] short"])
        rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
        body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const resp = await fetch(url, {method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
                    body: body});
                return {ok: resp.ok, status: resp.status, text: await resp.text()};
            } catch(e) { return {ok:false, error: e.message}; }
        }""", [f"{BATEXECUTE}?{params_qs}", body_str])

        if result.get("ok"):
            print(f"\n[改名 SHORT TOKEN] OK! status: {result['status']}")
            print(f"  body: {result['text'][:200]}")
        else:
            print(f"\n[改名 SHORT TOKEN] error: {result.get('status')} {result.get('text','')[:100]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
