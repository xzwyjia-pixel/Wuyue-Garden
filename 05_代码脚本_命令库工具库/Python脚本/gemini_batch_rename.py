"""
Gemini 批量改名脚本 v2 — CDP + 逆向 MaZiqc API

流程:
  Phase 1: 发现 — 刷新 Gemini, 拦截 batchexecute 响应, 识别对话列表 RPC + at token
  Phase 2: 分类 — 用已有分类器给每条对话加前缀
  Phase 3: 改名 — 用 MaZiqc RPC 批量发改名请求 (page.evaluate fetch)

用法:
  # 终端 1: 启动 Chrome CDP (务必先登录 Gemini)
  powershell -File start_chrome_cdp.ps1

  # 终端 2: 运行本脚本
  cd 02-审计工具
  python gemini_batch_rename.py              # 正常执行
  python gemini_batch_rename.py --dry-run    # 仅预览不改
  python gemini_batch_rename.py --limit 10   # 只改前 10 条

参数:
  --dry-run      仅预览, 不改名
  --limit N      只处理前 N 条
  --prefix X     只处理指定前缀的分类
  --rpcid ID     手动指定对话列表 RPCID
  --at TOKEN     手动指定 at auth token
  --load JSON    从 gemini_rpc_capture.json 加载 RPC 数据 (跳过 Phase 1)

示例:
  python gemini_batch_rename.py --dry-run
  python gemini_batch_rename.py --limit 5
  python gemini_batch_rename.py --prefix [DEV]
  python gemini_batch_rename.py --rpcid "bBSb4e" --at "AOOh0PFZ...:1778422563373"
"""

import asyncio, sys, json, re, urllib.parse, time, os
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

CDP_PORT = 9229
GEMINI_URL = "https://gemini.google.com/app"
BATEXECUTE = "https://gemini.google.com/_/BardChatUi/data/batchexecute"
SCRIPT_DIR = Path(__file__).resolve().parent

# ── 分类器 ──────────────────────────────────────────────
sys.path.insert(0, str(SCRIPT_DIR))
from process_gemini_takeout import classify

PREFIX_MAP = {
    "审计合规": "[AUD]", "直播运营": "[LIV]", "技术开发": "[DEV]",
    "文案创意": "[CPY]", "品牌设计": "[BRD]", "系统运维": "[OPS]",
    "方案咨询": "[CON]", "数据报表": "[DAT]",
}
REVERSE_PREFIX = {v: k for k, v in PREFIX_MAP.items()}

# ── CLI ─────────────────────────────────────────────────
DRY_RUN = "--dry-run" in sys.argv
LIMIT = None
FILTER_PREFIX = None
RPCID_OVERRIDE = None
AT_OVERRIDE = None
LOAD_PATH = None

i = 0
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == "--limit" and i + 1 < len(sys.argv):
        LIMIT = int(sys.argv[i + 1])
        i += 1
    elif arg == "--prefix" and i + 1 < len(sys.argv):
        FILTER_PREFIX = sys.argv[i + 1]
        i += 1
    elif arg == "--rpcid" and i + 1 < len(sys.argv):
        RPCID_OVERRIDE = sys.argv[i + 1]
        i += 1
    elif arg == "--at" and i + 1 < len(sys.argv):
        AT_OVERRIDE = sys.argv[i + 1]
        i += 1
    elif arg == "--load" and i + 1 < len(sys.argv):
        LOAD_PATH = sys.argv[i + 1]
        i += 1
    i += 1


def parse_batch_response(body: str) -> list:
    """
    Parse Google batchexecute multi-chunk NDJSON response.
    Format: )]}'\n\n<size>\n<json>\n<size>\n<json>...
    Returns list of all parsed JSON objects.
    """
    # Strip security prefix
    body = re.sub(r"^\)\]}'\n?", "", body)
    # Split into chunks: \n<digits>\n<json>
    chunks = []
    pos = 0
    while pos < len(body):
        m = re.match(r'\n(\d+)\n', body[pos:])
        if not m:
            break
        size = int(m.group(1))
        json_start = pos + m.end()
        json_end = json_start + size
        chunk = body[json_start:json_end]
        try:
            chunks.append(json.loads(chunk))
        except json.JSONDecodeError:
            break
        pos = json_end
    return chunks


def strip_batcherror(body: str) -> str:
    """Legacy - kept for compat but use parse_batch_response for new code."""
    chunks = parse_batch_response(body)
    if chunks:
        return json.dumps(chunks[0])
    return ""


def recursive_find_strings(obj, depth=0, max_depth=6):
    """Walk nested JSON, yield all string values.
    Used for heuristic conversation title detection."""
    if depth > max_depth:
        return
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from recursive_find_strings(v, depth + 1, max_depth)
    elif isinstance(obj, list):
        for item in obj:
            yield from recursive_find_strings(item, depth + 1, max_depth)


def looks_like_title(s: str) -> bool:
    """Heuristic: a string that looks like a user-entered conversation title."""
    if not isinstance(s, str) or len(s) < 3 or len(s) > 200:
        return False
    # Skip pure numbers, URLs, JSON fragments, code
    if re.match(r'^[\d\s,.%+\-/\\]+$', s):
        return False
    if re.match(r'^https?://', s):
        return False
    if re.match(r'^[{\[\"]', s) or s.startswith('function') or s.startswith('class '):
        return False
    # Must have at least one CJK or word char
    if not re.search(r'[一-鿿\w]', s):
        return False
    return True


def scan_for_conversations(body: str, min_count=3):
    """
    Try to extract conversation tokens + titles from batchexecute response body.
    Handles Google's nested JSON format:
      [["wrb.fr","RPCID","<real_data_as_json_string>",null,null,null,"generic"],...]
    Returns list of (token, title, confidence) | None if detection uncertain.
    """
    cleaned = parse_batch_response(body)
    if not cleaned:
        return None
    data = cleaned[0]  # First chunk has RPC responses

    candidates = []

    def _extract_convs(obj, depth=0):
        """Recursively extract [token, title] pairs from nested structures."""
        if depth > 8:
            return
        if isinstance(obj, str):
            # Try parsing string as JSON — handles nested batchexecute format
            if len(obj) > 50 and (obj[0] == '[' or obj[0] == '{'):
                try:
                    inner = json.loads(obj)
                    _extract_convs(inner, depth + 1)
                except json.JSONDecodeError:
                    pass
            return
        if isinstance(obj, list):
            # Check for [token, title, ...] format
            if len(obj) >= 2:
                first, second = obj[0], obj[1]
                if isinstance(first, str) and isinstance(second, str):
                    # c_ prefix token (short) or long base64 token
                    if (first.startswith("c_") or len(first) > 20) and looks_like_title(second):
                        candidates.append((first, second, 0.8))
                        return  # Don't recurse into matched conv entries
            # Check for dict items with token+title
            for item in obj:
                if isinstance(item, dict):
                    token = (item.get("conversationToken") or item.get("token")
                             or item.get("id") or item.get("conversationId"))
                    title = (item.get("title") or item.get("displayName")
                             or item.get("name") or item.get("displayName"))
                    if token and title and looks_like_title(str(title)):
                        candidates.append((str(token), str(title), 0.8))
            # Recurse into all items
            for item in obj:
                _extract_convs(item, depth + 1)
        elif isinstance(obj, dict):
            for v in obj.values():
                _extract_convs(v, depth + 1)

    _extract_convs(data)

    if len(candidates) >= min_count:
        return candidates
    return None


async def extract_at_token(page, timeout=20):
    """Get `at` token from POST body or URL of first batchexecute request."""
    future = asyncio.get_event_loop().create_future()

    async def on_request(req):
        if future.done():
            return
        url = req.url
        if "/batchexecute" in url:
            # Check POST body first
            try:
                post_data = req.post_data
                if post_data and "at=" in post_data:
                    parsed = urllib.parse.parse_qs(post_data)
                    if "at" in parsed and parsed["at"][0]:
                        future.set_result(parsed["at"][0])
                        return
            except Exception:
                pass
            # Fallback: check URL query string
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "at" in qs:
                future.set_result(qs["at"][0])

    page.on("request", on_request)
    try:
        return await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        return None
    finally:
        page.remove_listener("request", on_request)


async def load_all_sidebar(page):
    """Scroll sidebar to load all conversation items.
    Returns list of {href, text, token_hint} dicts."""
    sidebar_items = await page.evaluate("""() => {
        // Find conversation links in sidebar
        const links = document.querySelectorAll('a[href*="/app/"]');
        const items = [];
        const seen = new Set();
        for (const a of links) {
            const href = a.getAttribute('href') || '';
            const text = a.textContent?.trim() || '';
            const match = href.match(/\\/app\\/([^?&#]+)/);
            if (match && !seen.has(match[1]) && text.length > 1) {
                seen.add(match[1]);
                items.push({
                    href: href,
                    text: text.substring(0, 200),
                    convId: match[1],
                });
            }
        }
        return items;
    }""")

    # Try scrolling the sidebar container to reveal more items
    for scroll_attempt in range(10):
        prev_count = len(sidebar_items)
        added = await page.evaluate("""() => {
            // Find scrollable sidebar container
            const scrollables = document.querySelectorAll('[class*="scroll"], [class*="list"], nav, [role="list"]');
            let target = null;
            for (const el of scrollables) {
                if (el.scrollHeight > el.clientHeight) {
                    target = el;
                    break;
                }
            }
            if (!target) return false;
            target.scrollTop += 500;
            return true;
        }""")
        if not added:
            break
        await asyncio.sleep(2)
        new_items = await page.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="/app/"]');
            const items = [];
            const seen = new Set();
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const text = a.textContent?.trim() || '';
                const match = href.match(/\\/app\\/([^?&#]+)/);
                if (match && !seen.has(match[1]) && text.length > 1) {
                    seen.add(match[1]);
                    items.push({
                        href: href,
                        text: text.substring(0, 200),
                        convId: match[1],
                    });
                }
            }
            return items;
        }""")
        if len(new_items) > len(sidebar_items):
            sidebar_items = new_items
        else:
            break

    return sidebar_items


async def resolve_short_to_long_token(page, short_id):
    """
    Click a conversation by its short ID, intercept batchexecute to get long token,
    then rename it.

    Returns long token or None.
    """
    future = asyncio.get_event_loop().create_future()

    async def on_response(resp):
        url = resp.url
        if "/batchexecute" not in url or future.done():
            return
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        rpcids = qs.get("rpcids", [])
        if "MaZiqc" in rpcids or not any(r in str(rpcids) for r in ["getConvers", "loadConvers", "fetchConvers", "listConvers"]):
            return
        try:
            body = await resp.text()
        except:
            return
        convs = scan_for_conversations(body, min_count=1)
        if convs:
            future.set_result(convs[0])

    page.on("response", on_response)
    try:
        await page.evaluate(f"""() => {{
            const link = document.querySelector('a[href*="/app/{short_id}"]');
            if (link) link.click();
        }}""")
        return await asyncio.wait_for(future, timeout=5)
    except asyncio.TimeoutError:
        return None
    finally:
        page.remove_listener("response", on_response)


async def rename_conversation(page, token, new_title, at_token):
    """Send MaZiqc rename request via page.evaluate fetch."""
    rpc_params = json.dumps([20, token, new_title])
    rpc_call = json.dumps([["MaZiqc", rpc_params, None, "generic"]])
    body_str = f"f.req={urllib.parse.quote(rpc_call)}&at={urllib.parse.quote(at_token)}"

    result = await page.evaluate(
        """async (url, body) => {
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
        }""",
        [BATEXECUTE, body_str]
    )
    return result


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
async def main():
    async with async_playwright() as p:
        # ── Connect ──────────────────────────────────────
        print(f"[连接] CDP Chrome ({CDP_PORT})...")
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if "gemini" not in page.url:
            await page.goto(GEMINI_URL, timeout=30000)
            await asyncio.sleep(3)

        # ── Wait for login ───────────────────────────────
        body_text = await page.inner_text("body")
        if "登录" in body_text or "Sign in" in body_text:
            print("[等待] 请在 Chrome 中登录 Gemini...")
            for _ in range(180):
                await asyncio.sleep(1)
                bt = await page.inner_text("body")
                if "登录" not in bt and "Sign in" not in bt:
                    print("[OK] 已登录")
                    break

        # ══════════════════════════════════════════════════
        #  PHASE 1: DISCOVER RPCs
        # ══════════════════════════════════════════════════

        # ── Phase 1 vars ────────────────────────────────
        captured_responses = {}
        at_token = None
        conversation_list = None

        # If --load from previous capture
        if LOAD_PATH:
            load_p = Path(LOAD_PATH)
            if not load_p.exists():
                load_p = SCRIPT_DIR / LOAD_PATH
            if load_p.exists():
                print(f"\n[加载] RPC 数据: {load_p}")
                capture_data = json.loads(load_p.read_text(encoding="utf-8"))
                at_token = capture_data.get("at_token") or AT_OVERRIDE
                found = capture_data.get("found_conversations") or capture_data.get("conversations")
                if found and isinstance(found, dict):
                    rpcid = found.get("rpcids", [None])[0]
                    print(f"  对话列表 RPCID: {rpcid}, {found.get('count', '?')} 条")
                else:
                    # Maybe raw RPC capture with rpc samples
                    pass
            else:
                print(f"[WARN] 文件不存在: {load_p}")
            return  # Load mode: just print info, user runs main script for actual rename

        print(f"\n{'='*60}")
        print("Phase 1: 发现对话列表 RPC")
        print(f"{'='*60}")

        async def on_batch_request(req):
            nonlocal at_token
            if at_token:
                return
            url = req.url
            if "/batchexecute" not in url:
                return
            try:
                post_data = req.post_data
                if post_data and "at=" in post_data:
                    parsed = urllib.parse.parse_qs(post_data)
                    if "at" in parsed and parsed["at"][0]:
                        at_token = parsed["at"][0]
            except Exception:
                pass

        async def on_batch_response(resp):
            nonlocal at_token, conversation_list
            url = resp.url
            if "/batchexecute" not in url:
                return

            parsed_url = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed_url.query)
            rpcids = qs.get("rpcids", [])

            if not at_token and "at" in qs:
                at_token = qs["at"][0]

            try:
                body = await resp.text()
            except:
                return

            for rpcid in rpcids:
                if rpcid not in captured_responses:
                    captured_responses[rpcid] = []
                captured_responses[rpcid].append(body[:2000])
                if len(captured_responses[rpcid]) > 5:
                    captured_responses[rpcid] = captured_responses[rpcid][-5:]

            # Try to auto-detect conversation list
            if not conversation_list and rpcids:
                detected = scan_for_conversations(body, min_count=3)
                if detected:
                    conversation_list = detected
                    print(f"\n  [!!!] 发现对话列表! RPCID={rpcids[0]}, {len(detected)} 条")

        page.on("request", on_batch_request)
        page.on("response", on_batch_response)

        # Refresh to trigger conversation list fetch
        print("\n  刷新页面以捕获对话列表 RPC...")
        await page.goto(GEMINI_URL, timeout=30000)
        await asyncio.sleep(8)

        # If the conversation list wasn't found in initial load,
        # wait longer and try to scroll sidebar
        if not conversation_list:
            print("  等待更多数据加载...")
            for i in range(5):
                await asyncio.sleep(2)
                # Try scrolling
                await page.evaluate("""() => {
                    const els = document.querySelectorAll('[class*="scroll"], [class*="list"]');
                    for (const el of els) {
                        if (el.scrollHeight > el.clientHeight) {
                            el.scrollTop += el.clientHeight / 2;
                        }
                    }
                }""")
                if conversation_list:
                    break

        print(f"\n  捕获到 {len(captured_responses)} 个不同 RPC:")
        for rpcid, bodies in sorted(captured_responses.items()):
            preview = strip_batcherror(bodies[0])[:150] if bodies else ""
            # Show first 100 chars of meaningful data
            preview_clean = preview.replace('\n', ' ').strip()[:120]
            print(f"    {rpcid}: {len(bodies)} 次 | {preview_clean}")

        # If still no conversation list, fall back to sidebar DOM
        if not conversation_list:
            print("\n  RPC 扫描未识别对话列表, 尝试侧边栏 DOM 提取...")
            sidebar_items = await load_all_sidebar(page)
            print(f"  侧边栏发现 {len(sidebar_items)} 个对话链接")

            if sidebar_items:
                # We have short IDs from URLs, but need long tokens for rename
                print("  短ID → 长token 映射需要逐个点开对话 (较慢)...")
                print("  改用 RPC 拦截方式获取长 token")

                # Alternative: try to extract from JS global state
                js_data = await page.evaluate("""() => {
                    // Search for conversation data in various globals
                    const results = {};
                    for (const key of Object.getOwnPropertyNames(window)) {
                        try {
                            const val = window[key];
                            if (val && typeof val === 'object') {
                                const s = JSON.stringify(val).substring(0, 200);
                                if (s.includes('conversation') || s.includes('MaZiqc')) {
                                    results[key] = s.substring(0, 300);
                                }
                            }
                        } catch(e) {}
                    }
                    return results;
                }""")
                if js_data:
                    print(f"  JS 全局中发现潜在对话数据 ({len(js_data)} 个):")
                    for k, v in list(js_data.items())[:5]:
                        print(f"    {k}: {v[:100]}")
                else:
                    print("  JS 全局中未发现对话数据")

        # Apply overrides from CLI
        if AT_OVERRIDE:
            at_token = AT_OVERRIDE
            print(f"\n  [CLI] at token: {at_token[:30]}...")

        if RPCID_OVERRIDE:
            print(f"\n  [CLI] RPCID 覆盖: {RPCID_OVERRIDE}")
            # Try to find this RPCID in captured responses
            if RPCID_OVERRIDE in captured_responses:
                print(f"  在捕获数据中找到该 RPCID ({len(captured_responses[RPCID_OVERRIDE])} 次)")
            else:
                print(f"  警告: 该 RPCID 未在本次捕获中出现")

        # Save captured RPC data for analysis
        rpc_capture_path = SCRIPT_DIR / "gemini_rpc_capture.json"
        json.dump({
            "at_token": at_token,
            "rpcids": list(captured_responses.keys()),
            "rpc_samples": captured_responses,
            "conversation_list_found": conversation_list is not None,
        }, open(rpc_capture_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\n  RPC 数据已保存: {rpc_capture_path.name}")

        if not at_token:
            print("\n[ERROR] 未获取到 at token")
            print("  使用 --at TOKEN 手动指定")
            return

        if not conversation_list:
            print("\n[ERROR] 未识别对话列表")
            print("  运行 gemini_discover_rpc.py 手动捕获后重试")
            print("  或使用 --rpcid ID --at TOKEN 手动指定")
            if captured_responses:
                print(f"\n  捕获到 {len(captured_responses)} 个 RPC, 检查 gemini_rpc_capture.json")
            return

        # ══════════════════════════════════════════════════
        #  PHASE 2: CLASSIFY
        # ══════════════════════════════════════════════════
        print(f"\n{'='*60}")
        print("Phase 2: 分类对话")
        print(f"{'='*60}")

        # Deduplicate by token
        seen_tokens = set()
        unique_convs = []
        for token, title, *rest in conversation_list:
            if token not in seen_tokens:
                seen_tokens.add(token)
                unique_convs.append((token, title))

        print(f"  共 {len(unique_convs)} 条对话")

        # Build rename queue
        rename_queue = []
        skip_count = 0
        for token, title in unique_convs:
            if not title or not title.strip():
                continue

            # Check if already prefixed
            has_prefix = False
            for prefix in PREFIX_MAP.values():
                if title.startswith(prefix):
                    has_prefix = True
                    break

            if has_prefix:
                skip_count += 1
                continue

            cat = classify(title)
            prefix = PREFIX_MAP.get(cat, "[OTH]")
            new_title = f"{prefix} {title}"
            rename_queue.append((token, title, new_title, cat))

        print(f"  需改名: {len(rename_queue)} (已跳过 {skip_count} 条已有前缀)")

        # Apply filters
        if FILTER_PREFIX:
            rename_queue = [x for x in rename_queue if PREFIX_MAP.get(x[3]) == FILTER_PREFIX or x[3] == FILTER_PREFIX]
            print(f"  过滤后: {len(rename_queue)} 条 ({FILTER_PREFIX})")

        if LIMIT:
            rename_queue = rename_queue[:LIMIT]
            print(f"  限制前 {LIMIT} 条")

        # Show category breakdown
        if rename_queue:
            print()
            for cat in sorted(set(x[3] for x in rename_queue)):
                count = sum(1 for x in rename_queue if x[3] == cat)
                pfx = PREFIX_MAP.get(cat, "")
                print(f"    {pfx} {cat}: {count} 条")

            print(f"\n  改名预览 (前 15 条):")
            print(f"  {'─'*60}")
            for token, old, new, cat in rename_queue[:15]:
                print(f"    {old[:40]:40s} → {new}")
            if len(rename_queue) > 15:
                print(f"    ... 还有 {len(rename_queue) - 15} 条")

        if not rename_queue:
            print("\n  无需要改名的对话")
            return

        if DRY_RUN:
            print(f"\n[dry-run] 预览完成, {len(rename_queue)} 条将改名")
            print("  移除 --dry-run 执行实际改名")
            return

        # ══════════════════════════════════════════════════
        #  PHASE 3: RENAME
        # ══════════════════════════════════════════════════
        print(f"\n{'='*60}")
        print("Phase 3: 批量改名")
        print(f"{'='*60}")

        renamed = 0
        errors = 0
        start_time = time.time()
        total = len(rename_queue)

        for i, (token, old_title, new_title, cat) in enumerate(rename_queue, 1):
            result = await rename_conversation(page, token, new_title, at_token)

            if result.get("ok"):
                renamed += 1
                status = "✓"
            else:
                errors += 1
                status = "✗"

            elapsed = time.time() - start_time
            eta = (elapsed / i) * (total - i) if i > 0 else 0
            pct = i / total * 100

            err_info = ""
            if not result.get("ok"):
                err_info = f"  [{result.get('status', 'err')}] {result.get('error', result.get('text', ''))[:60]}"

            print(f"  [{i:4d}/{total}] {status} {old_title[:35]:35s} → {new_title[:40]:40s} {err_info}")
            sys.stdout.flush()

            # Rate limiting: 1-2s between requests
            await asyncio.sleep(1.5)

        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"  完成! {renamed}/{total} 成功, {errors} 失败")
        print(f"  耗时: {total_time:.0f}s ({total_time/total:.1f}s/条)")
        print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
