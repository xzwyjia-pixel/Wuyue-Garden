"""
Gemini 网页端对话批量加前缀
用 Playwright 打开 Gemini → 扫描对话列表 → 按分类匹配 → 加前缀改名

用法:
  1. 关掉所有 Chrome
  2. 双击 start_chrome_cdp.ps1
  3. 在 Gemini 网页登录
  4. python gemini_prefix_rename.py
"""
import asyncio, sys, json, re, zipfile
from pathlib import Path
from collections import defaultdict
from playwright.async_api import async_playwright

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

CDP_PORT = 9229
GEMINI_URL = "https://gemini.google.com/app"

CAT_PREFIX = {
    "[DEV]": "编程开发",
    "[AUD]": "审计合规",
    "[CPY]": "文案创作",
    "[OPS]": "系统运维",
    "[PJM]": "项目管理",
    "[DAT]": "数据分析",
    "[LIV]": "直播运营",
    "[MCP]": "Claude/MCP",
    "[OBS]": "Obsidian配置",
    "[OTH]": "其他",
}

CATEGORY_RULES = [
    ("[DEV]", ["python", "javascript", "typescript", "代码", "bug", "api", "react",
                "vue", "前端", "后端", "git", "docker", "sql", "node", "pip"]),
    ("[AUD]", ["审计", "合规", "规则", "风险", "违禁词", "广告法", "限流", "封号",
                "规则甄查", "红绿灯", "政策"]),
    ("[CPY]", ["文案", "写作", "文章", "创作", "改写", "标题", "脚本", "短剧",
                "故事", "内容", "小红书", "抖音", "prompt", "提示词"]),
    ("[OPS]", ["powershell", "环境变量", "配置", "终端", "shell", "profile",
                "安装", "部署", "cmd"]),
    ("[PJM]", ["项目", "计划", "方案", "ppt", "汇报", "roadmap", "进度", "管理"]),
    ("[DAT]", ["数据", "分析", "报表", "excel", "sql", "可视化", "统计", "爬虫"]),
    ("[LIV]", ["直播", "小桃", "凡姐", "带货", "转化", "ROI", "流量", "粉丝", "直播间"]),
    ("[MCP]", ["claude", "mcp", "json-rpc", "工具调用", "sonnet", "deepseek", "gptsapi"]),
    ("[OBS]", ["obsidian", "vault", "双链", "markdown", "插件", "知识库"]),
]

# 已经在类名中的前缀 → 跳过
EXISTING_PREFIXES = tuple(CAT_PREFIX.keys())


def classify(title: str) -> str:
    title_lower = title.lower()
    scores = {}
    for prefix, kws in CATEGORY_RULES:
        scores[prefix] = sum(1 for k in kws if k in title_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] >= 2 else "[OTH]"


async def get_visible_conversations(page) -> list:
    """扫描 Gemini 侧边栏对话列表，返回 (title, element) 列表."""
    convs = []

    # 尝试多种选择器找对话项
    for sel in ["a[href*='/app/']", "[class*=conversation]", "[role=listitem]",
                 "nav a", "[class*=history] a"]:
        try:
            els = await page.query_selector_all(sel)
            if els and len(els) > 2:
                for el in els:
                    href = await el.get_attribute("href") or ""
                    if "/app/" not in href and "google" in href:
                        continue
                    text = (await el.inner_text()).strip()
                    if text and len(text) > 2 and text != "New chat" and "Google" not in text:
                        convs.append({"title": text, "element": el, "href": href})
                if convs:
                    break
        except:
            continue

    return convs


async def rename_conversation(page, conv, new_title: str) -> bool:
    """点击对话 → 触发改名 → 输入新标题."""
    try:
        # 点击打开对话
        await conv["element"].click()
        await asyncio.sleep(2)

        # 找改名入口 (通常是右上角菜单 → Rename 或双击标题)
        # 方法1: 双击对话标题
        header_sels = ["[class*=header]", "[class*=title]", "h1", "[class*=conversation-title]"]
        for sel in header_sels:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = (await el.inner_text()).strip()
                    if text and len(text) > 2 and text == conv["title"]:
                        await el.click(click_count=2)
                        await asyncio.sleep(0.5)
                        break
            except:
                continue

        # 检查是否有输入框出现
        input_sels = ["input[class*=rename]", "input[type=text]", "[contenteditable=true]"]
        input_el = None
        for sel in input_sels:
            try:
                input_el = await page.query_selector(sel)
                if input_el:
                    break
            except:
                continue

        if not input_el:
            # 方法2: 右键菜单 → Rename
            try:
                await conv["element"].click(button="right")
                await asyncio.sleep(0.5)
                # 找 "Rename" 按钮
                rename_btn = await page.query_selector("text=Rename")
                if rename_btn:
                    await rename_btn.click()
                    await asyncio.sleep(0.5)
                    input_el = await page.query_selector("input[class*=rename]")
            except:
                pass

        if not input_el:
            print(f"  [!] 无法触发改名: {conv['title'][:30]}")
            return False

        # 清空并输入新标题
        await input_el.fill("")
        await asyncio.sleep(0.3)
        await input_el.fill(new_title)
        await asyncio.sleep(0.3)

        # 确认 (回车或点击空白)
        await input_el.press("Enter")
        await asyncio.sleep(1)
        print(f"  [OK] {conv['title'][:25]:>25} → {new_title[:40]}")
        return True

    except Exception as e:
        print(f"  [ERR] {str(e)[:60]}")
        return False


async def main():
    print("=" * 50)
    print("Gemini 对话批量加前缀")
    print("=" * 50)
    print("连接 Chrome CDP...")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        print("CDP 连接成功")

        # 找 Gemini 页面或新建
        page = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "gemini" in pg.url:
                    page = pg
                    break
        if not page:
            page = browser.contexts[0].pages[0] if browser.contexts[0].pages else await browser.contexts[0].new_page()

        await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        print(f"当前页面: {await page.title()}")

        # 检查登录 — 等最多 60 秒
        body = await page.inner_text("body")
        if "登录" in body:
            print("等待登录 Gemini (最多 60 秒)...")
            for _ in range(60):
                await asyncio.sleep(1)
                body = await page.inner_text("body")
                if "登录" not in body:
                    print("登录成功!")
                    break
            else:
                print("登录超时，退出")
                return

        # 滚动加载更多对话
        print("加载对话列表...")
        for _ in range(3):
            await page.keyboard.press("PageDown")
            await asyncio.sleep(1)

        convs = await get_visible_conversations(page)
        print(f"侧边栏可见对话: {len(convs)}")

        if not convs:
            print("未找到对话列表，请确保侧边栏可见")
            await asyncio.sleep(30)
            return

        # 分类并改名
        renamed = 0
        skipped = 0
        for i, conv in enumerate(convs):
            title = conv["title"]
            # 跳过已有前缀的
            if title.startswith(EXISTING_PREFIXES):
                skipped += 1
                continue

            prefix = classify(title)
            new_title = f"{prefix} {title}"[:100]
            print(f"[{i+1}/{len(convs)}]", end=" ")

            ok = await rename_conversation(page, conv, new_title)
            if ok:
                renamed += 1
            await asyncio.sleep(1)

        print(f"\n完成! 改名 {renamed} 条，跳过 {skipped} 条(已有前缀)")
        print("提示: 滚动加载更多对话后再次运行可继续改名")

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
