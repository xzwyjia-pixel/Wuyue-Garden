"""
Gemini batch rename: refresh page → get tokens → click each conv → get long token → rename.
"""
import asyncio, json, urllib.parse, sys, time, re
from pathlib import Path
from playwright.async_api import async_playwright

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from process_gemini_takeout import classify

PREFIX_MAP = {"审计合规":"[AUD]","直播运营":"[LIV]","技术开发":"[DEV]","文案创意":"[CPY]","品牌设计":"[BRD]","系统运维":"[OPS]","方案咨询":"[CON]","数据报表":"[DAT]"}
DRY_RUN = "--dry-run" in sys.argv
LIMIT = None
for i, a in enumerate(sys.argv):
    if a == "--limit" and i+1 < len(sys.argv): LIMIT = int(sys.argv[i+1])

def parse_batch(body):
    body = re.sub(r"^\)\]}'\n?", "", body)
    pos = 0
    chunks = []
    while pos < len(body):
        m = re.match(r'\n(\d+)\n', body[pos:])
        if not m: break
        size = int(m.group(1))
        js = pos + m.end()
        je = js + size
        try: chunks.append(json.loads(body[js:je]))
        except: break
        pos = je
    return chunks

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Navigate and capture at token + f.sid
        print("[1/5] 获取 tokens...")
        at_token, fsid, bl = None, None, None
        fut = asyncio.get_event_loop().create_future()

        async def on_req(req):
            if fut.done(): return
            if "/batchexecute" in req.url:
                pd = req.post_data
                if isinstance(pd, str) and "at=" in pd:
                    parsed = urllib.parse.parse_qs(pd)
                    if "at" in parsed: fut.set_result(parsed["at"][0])

        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(8)
        page.remove_listener("request", on_req)

        try: at_token = await asyncio.wait_for(fut, timeout=10)
        except: print("[FAIL] no at token"); return
        print(f"  at: {at_token[:40]}...")

        # Get f.sid from performance API
        perf = await page.evaluate("""() => {
            try {
                const e = performance.getEntriesByType('resource').find(e => e.name.includes('batchexecute'));
                return e ? e.name : null;
            } catch(e) { return null; }
        }""")
        if not perf: print("[FAIL] no perf entry"); return
        pq = urllib.parse.parse_qs(urllib.parse.urlparse(perf).query)
        fsid = pq.get("f.sid", [""])[0]
        bl = pq.get("bl", [""])[0]
        if not fsid: print("[FAIL] no f.sid"); return
        print(f"  f.sid: {fsid}")

        # Get convIds from sidebar
        print("\n[2/5] 提取对话列表...")
        for s in range(10):
            await page.evaluate("""() => {
                const els = document.querySelectorAll('[class*="scroll"],[class*="list"],nav');
                for (const el of els) if (el.scrollHeight > el.clientHeight) el.scrollTop += el.scrollHeight * 0.3;
            }""")
            await asyncio.sleep(1)
        sidebar = await page.evaluate("""() => {
            const items = []; const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/app/"]')) {
                const h = a.getAttribute('href')||'', t = a.textContent?.trim()||'';
                const m = h.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && t.length > 1) { seen.add(m[1]); items.push({id:m[1],title:t}); }
            }
            return items;
        }""")
        print(f"  {len(sidebar)} 条对话")
        if not sidebar: return

        # Build rename queue
        print("\n[3/5] 分类...")
        queue = []
        for s in sidebar:
            if not s["title"]: continue
            if any(s["title"].startswith(p) for p in PREFIX_MAP.values()): continue
            cat = classify(s["title"])
            prefix = PREFIX_MAP.get(cat, "[OTH]")
            queue.append({"id": s["id"], "title": s["title"], "new": f"{prefix} {s['title']}", "cat": cat})

        print(f"  需改名: {len(queue)}")
        cats = {}
        for q in queue: cats[q["cat"]] = cats.get(q["cat"], 0) + 1
        for c, n in sorted(cats.items()): print(f"    {PREFIX_MAP.get(c,'[OTH]')} {c}: {n}")
        for q in queue[:10]: print(f"    {q['title'][:40]:40s} → {q['new']}")
        if len(queue) > 10: print(f"    ... ({len(queue)-10} 更多)")

        if DRY_RUN: print(f"\n[dry-run] {len(queue)} 条"); return
        if LIMIT: queue = queue[:LIMIT]

        # Click each, get long token, rename
        print(f"\n[4/5] 逐个获取长 token + 改名 ({len(queue)} 条)...")
        renamed, errors = 0, 0
        total = len(queue)
        start_t = time.time()
        req_id = int(time.time() * 1000)

        for i, item in enumerate(queue, 1):
            conv_id = item["id"]
            old_title = item["title"]
            new_title = item["new"]

            # Click conversation, intercept hNvQHb for long token
            long_token = None
            h_fut = asyncio.get_event_loop().create_future()

            async def on_h_resp(resp):
                if h_fut.done(): return
                if "/batchexecute" in resp.url and "hNvQHb" in resp.url:
                    try:
                        body = await resp.text()
                        # Search for long token pattern in full body
                        matches = re.findall(r't[A-Za-z0-9+/]{50,}={0,2}', body)
                        if matches:
                            h_fut.set_result(matches[0])
                        else:
                            h_fut.set_result(None)
                    except: h_fut.set_result(None)

            page.on("response", on_h_resp)
            await page.evaluate(f"""() => {{
                const a = document.querySelector('a[href*="/app/{conv_id}"]');
                if (a) a.click();
            }}""")

            try: long_token = await asyncio.wait_for(h_fut, timeout=8)
            except: long_token = None
            finally: page.remove_listener("response", on_h_resp)

            if not long_token:
                print(f"  [{i:4d}/{total}] ✗ {old_title[:35]:35s} → no long token")
                errors += 1
                continue

            # Rename via MaZiqc
            req_id += 100000
            qs = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(bl)}&f.sid={urllib.parse.quote(fsid)}&hl=zh-CN&_reqid={req_id}&rt=c"
            rpc_params = json.dumps([20, long_token, new_title])
            rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
            body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

            result = await page.evaluate("""async (url, body) => {
                try {
                    const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                    return {ok:r.ok, status:r.status, text: (await r.text()).substring(0,200)};
                } catch(e) { return {ok:false, error:e.message}; }
            }""", [f"{BATEXECUTE}?{qs}", body_str])

            if result.get("ok") and result.get("status") == 200:
                renamed += 1
                print(f"  [{i:4d}/{total}] ✓ {old_title[:35]:35s} → {new_title[:40]}")
            else:
                errors += 1
                print(f"  [{i:4d}/{total}] ✗ {old_title[:35]:35s} → rename failed ({result.get('status','?')})")

            elapsed = time.time() - start_t
            eta = (elapsed / i) * (total - i) if i > 0 else 0
            await asyncio.sleep(1.5)

        print(f"\n[5/5] 完成! {renamed}/{total} 成功, {errors} 失败 ({time.time()-start_t:.0f}s)")

if __name__ == "__main__":
    asyncio.run(main())
