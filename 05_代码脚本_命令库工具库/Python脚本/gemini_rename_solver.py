"""
Complete solution: MaZiqc [13] list → short c_xxx tokens → MUAZcd rename.
Extracts params from live page, no UI clicking needed for rename.
"""
import asyncio, json, urllib.parse, re, time, sys
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
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(5)

        body_text = await page.inner_text("body")
        if "登录" in body_text or "Sign in" in body_text:
            for _ in range(60):
                await asyncio.sleep(1)
                if "登录" not in await page.inner_text("body"): break

        print("[1/5] Extracting params from page...")
        params = {}
        async def on_req(req):
            if "/batchexecute" not in req.url or params.get("done"):
                return
            try:
                pd = req.post_data
                if pd and "at=" in pd:
                    bqp = urllib.parse.parse_qs(pd)
                    if "at" in bqp:
                        params["at"] = bqp["at"][0]
                        parsed_url = urllib.parse.urlparse(req.url)
                        qp = urllib.parse.parse_qs(parsed_url.query)
                        params["bl"] = qp.get("bl", [""])[0]
                        params["fsid"] = qp.get("f.sid", [""])[0]
                        params["reqid"] = int(qp.get("_reqid", ["0"])[0])
                        params["done"] = True
            except: pass

        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(8)
        page.remove_listener("request", on_req)

        if not params.get("at"):
            print("  FAIL: no at token")
            return
        print(f"  at:   {params['at'][:40]}...")
        print(f"  bl:   {params['bl'][:40]}...")
        print(f"  fsid: {params['fsid']}")

        # MaZiqc [13] list conversations
        print("\n[2/5] MaZiqc list conversations...")
        req_id = params["reqid"] + 100000
        qs_list = f"rpcids=MaZiqc&source-path=%2Fapp&bl={urllib.parse.quote(params['bl'])}&f.sid={urllib.parse.quote(params['fsid'])}&hl=zh-CN&_reqid={req_id}&rt=c"
        # [13,null,[0,null,1]] = recent convs | [13,null,[1,null,1]] = pinned
        rpc_list = json.dumps([["MaZiqc", "[13,null,[0,null,1]]", None, "generic"]])
        body_list = f"f.req={urllib.parse.quote(rpc_list)}&at={urllib.parse.quote(params['at'])}"

        result = await page.evaluate("""async (url, body) => {
            try {
                const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                return {ok:r.ok, status:r.status, text: (await r.text()).substring(0, 50000)};
            } catch(e) { return {ok:false, error:e.message}; }
        }""", [f"{BATEXECUTE}?{qs_list}", body_list])

        if not result.get("ok"):
            print(f"  LIST FAIL: {json.dumps(result, ensure_ascii=False)[:200]}")
            return

        chunks = parse_batch(result["text"])
        convs = []
        if chunks and len(chunks[0]) > 0 and isinstance(chunks[0][0], list) and len(chunks[0][0]) > 2:
            inner_raw = chunks[0][0][2]
            if isinstance(inner_raw, str):
                inner = json.loads(inner_raw)
            else:
                inner = inner_raw
            if inner and len(inner) > 2 and isinstance(inner[2], list):
                for c in inner[2]:
                    if len(c) > 0 and isinstance(c[0], str) and c[0].startswith("c_"):
                        title = str(c[1]) if len(c) > 1 else ""
                        convs.append({"id": c[0], "title": title})
        print(f"  Found {len(convs)} conversations")

        if not convs:
            print(f"  Raw: {result['text'][:300]}")
            return

        # Classify
        print("\n[3/5] Classifying...")
        queue = []
        for c in convs:
            if not c["title"]: continue
            if any(c["title"].startswith(p) for p in PREFIX_MAP.values()): continue
            cat = classify(c["title"])
            prefix = PREFIX_MAP.get(cat, "[OTH]")
            queue.append({"id": c["id"], "title": c["title"], "new": f"{prefix} {c['title']}", "cat": cat})

        print(f"  Need rename: {len(queue)}/{len(convs)}")
        cats = {}
        for q in queue: cats[q["cat"]] = cats.get(q["cat"], 0) + 1
        for c_name, n in sorted(cats.items()): print(f"    {PREFIX_MAP.get(c_name,'[OTH]')} {c_name}: {n}")
        for q in queue[:5]: print(f"    '{q['title'][:40]}' -> '{q['new'][:45]}'")
        if len(queue) > 5: print(f"    ... ({len(queue)-5} more)")

        if DRY_RUN:
            print(f"\n[dry-run] {len(queue)} to rename")
            return
        if LIMIT: queue = queue[:LIMIT]

        # MUAZcd rename
        print(f"\n[4/5] MUAZcd rename ({len(queue)} convs)...")
        renamed, errors = 0, 0
        total = len(queue)
        start_t = time.time()

        for i, item in enumerate(queue, 1):
            # Construct MUAZcd params
            # Format: [null,[["title"]],["c_TOKEN","NEW_TITLE"]]
            muazcd_params = json.dumps([None, [["title"]], [item["id"], item["new"]]])
            rpc_call = json.dumps([["MUAZcd", muazcd_params, None, "generic"]])
            body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(params['at'])}"

            req_id += 100000
            qs = f"rpcids=MUAZcd&source-path=%2Fapp%2F{item['id']}&bl={urllib.parse.quote(params['bl'])}&f.sid={urllib.parse.quote(params['fsid'])}&hl=zh-CN&_reqid={req_id}&rt=c"

            result = await page.evaluate("""async (url, body) => {
                try {
                    const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}, body});
                    return {ok:r.ok, status:r.status, text: (await r.text()).substring(0, 200)};
                } catch(e) { return {ok:false, error:e.message}; }
            }""", [f"{BATEXECUTE}?{qs}", body_str])

            if result.get("ok") and result.get("status") == 200:
                renamed += 1
                print(f"  [{i:4d}/{total}] OK {item['title'][:35]} -> {item['new'][:40]}")
            else:
                errors += 1
                print(f"  [{i:4d}/{total}] FAIL {item['title'][:35]} ({result.get('status','?')})")
                if errors <= 3:
                    print(f"    resp: {result.get('text','')[:200]}")

            elapsed = time.time() - start_t
            eta = (elapsed / i) * (total - i) if i > 0 else 0

        print(f"\n[5/5] Done! {renamed}/{total} success, {errors} failed ({time.time()-start_t:.0f}s)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
