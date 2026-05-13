"""
Extract all Gemini conversations from page state, then batch rename via MaZiqc.
"""
import asyncio, json, re, urllib.parse, sys, time
from pathlib import Path
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_gemini_takeout import classify

CDP_PORT = 9229
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"
SCRIPT_DIR = Path(__file__).resolve().parent

PREFIX_MAP = {
    "审计合规": "[AUD]", "直播运营": "[LIV]", "技术开发": "[DEV]",
    "文案创意": "[CPY]", "品牌设计": "[BRD]", "系统运维": "[OPS]",
    "方案咨询": "[CON]", "数据报表": "[DAT]",
}

DRY_RUN = "--dry-run" in sys.argv

async def main():
    async with async_playwright() as p:
        print(f"[连接] CDP Chrome ({CDP_PORT})...")
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto("https://gemini.google.com/app", timeout=30000)
            await asyncio.sleep(3)

        body_text = await page.inner_text("body")
        if "登录" in body_text or "Sign in" in body_text:
            print("[等待] 请在 Chrome 中登录 Gemini...")
            for _ in range(180):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt:
                    print("[OK] 已登录")
                    break

        # ── Extract at token from first batchexecute request ──
        print("\n[Phase 1] 获取 at token...")
        at_token = None
        at_future = asyncio.get_event_loop().create_future()

        async def on_req(req):
            if at_future.done():
                return
            if "/batchexecute" in req.url:
                pd = req.post_data
                if isinstance(pd, str) and "at=" in pd:
                    parsed = urllib.parse.parse_qs(pd)
                    if "at" in parsed and parsed["at"][0]:
                        at_future.set_result(parsed["at"][0])

        page.on("request", on_req)
        await page.goto("https://gemini.google.com/app", timeout=30000)
        await asyncio.sleep(5)

        try:
            at_token = await asyncio.wait_for(at_future, timeout=10)
            print(f"  at token: {at_token[:40]}...")
        except asyncio.TimeoutError:
            print("  [ERROR] 未能获取 at token")
            return
        finally:
            page.remove_listener("request", on_req)

        # ── Extract conversations from sidebar DOM + page data ──
        print("\n[Phase 2] 提取对话列表...")

        # Method A: Click sidebar, scroll to load all, capture IDs
        # First, scroll the sidebar to load all conversations
        print("  展开侧边栏...")
        for scroll_attempt in range(15):
            await page.evaluate("""() => {
                const els = document.querySelectorAll('[class*="scroll"], [class*="list"], nav, [role="list"]');
                for (const el of els) {
                    if (el.scrollHeight > el.clientHeight) {
                        el.scrollTop += el.scrollHeight * 0.3;
                    }
                }
            }""")
            await asyncio.sleep(1.5)

        # Get all sidebar links
        sidebar = await page.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="/app/"]');
            const items = [];
            const seen = new Set();
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const text = a.textContent?.trim() || '';
                const m = href.match(/\\/app\\/([^?&#]+)/);
                if (m && !seen.has(m[1]) && text.length > 1) {
                    seen.add(m[1]);
                    items.push({ convId: m[1], title: text.substring(0, 200) });
                }
            }
            return items;
        }""")
        print(f"  侧边栏: {len(sidebar)} 条对话")

        if not sidebar:
            print("  [ERROR] 未找到对话")
            return

        # Method B: Get at token (already done)

        # Phase 3: Build rename queue
        print("\n[Phase 3] 分类...")
        rename_queue = []
        skip_count = 0

        for item in sidebar:
            title = item["title"]
            conv_id = item["convId"]

            if not title or not title.strip():
                continue

            # Check if already prefixed
            has_prefix = any(title.startswith(p) for p in PREFIX_MAP.values())
            if has_prefix:
                skip_count += 1
                continue

            cat = classify(title)
            prefix = PREFIX_MAP.get(cat, "[OTH]")
            new_title = f"{prefix} {title}"
            rename_queue.append((conv_id, title, new_title, cat))

        print(f"  需改名: {len(rename_queue)} (跳过 {skip_count})")

        # Category breakdown
        if rename_queue:
            print()
            cats = {}
            for _, _, _, cat in rename_queue:
                cats[cat] = cats.get(cat, 0) + 1
            for cat in sorted(cats.keys()):
                pfx = PREFIX_MAP.get(cat, "")
                print(f"    {pfx} {cat}: {cats[cat]}")

            print(f"\n  预览 (前 15):")
            for _, old, new, _ in rename_queue[:15]:
                print(f"    {old[:45]:45s} → {new}")

        if DRY_RUN:
            print(f"\n[dry-run] {len(rename_queue)} 条将改名")
            return

        # Phase 4: Rename using MaZiqc
        print(f"\n[Phase 4] 批量改名 ({len(rename_queue)} 条)...")
        renamed = 0
        errors = 0
        start = time.time()
        total = len(rename_queue)

        for i, (conv_id, old_title, new_title, cat) in enumerate(rename_queue, 1):
            # Build MaZiqc RPC call for rename
            # Use conv_id directly as token (c_xxx format)
            rpc_params = json.dumps([20, conv_id, new_title])
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
                    return { ok: resp.ok, status: resp.status, text: text.substring(0, 300) };
                } catch (e) {
                    return { ok: false, error: e.message };
                }
            }""", [BATEXECUTE, body_str])

            if result.get("ok"):
                renamed += 1
                status = "✓"
            else:
                errors += 1
                status = "✗"

            elapsed = time.time() - start
            eta = (elapsed / i) * (total - i) if i > 0 else 0
            err_info = ""
            if not result.get("ok"):
                err_info = f" [{result.get('status', 'err')}] {result.get('error', result.get('text', ''))[:60]}"
            print(f"  [{i:4d}/{total}] {status} {old_title[:35]:35s} → {new_title[:40]:40s}{err_info}")
            sys.stdout.flush()

            await asyncio.sleep(1.5)

        t = time.time() - start
        print(f"\n  完成! {renamed}/{total} 成功, {errors} 失败 ({t:.0f}s)")

if __name__ == "__main__":
    asyncio.run(main())
