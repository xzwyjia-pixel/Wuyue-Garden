"""
生成 Chrome 书签 HTML → Gemini 对话按分类整理
产物: gemini_bookmarks.html → Chrome 导入即用
"""
import json, re, os, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from html.parser import HTMLParser

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

OBSIDIAN_DIR = Path("E:/Obsidian/Gemini对话")
OUTPUT = Path("E:/MyCodeProjects/02-审计工具/gemini_bookmarks.html")

# 分类 → 短前缀
CAT_PREFIX = {
    "编程开发":   "[DEV]",
    "审计合规":   "[AUD]",
    "文案创作":   "[CPY]",
    "系统运维":   "[OPS]",
    "项目管理":   "[PJM]",
    "数据分析":   "[DAT]",
    "直播运营":   "[LIV]",
    "Claude/MCP": "[MCP]",
    "Obsidian配置":"[OBS]",
    "其他":       "[OTH]",
}


def extract_gemini_url(content: str) -> str:
    """从 markdown frontmatter 提取 Gemini URL."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("url:") and "gemini.google.com" in line:
            return line.split("url:")[-1].strip()
    return ""


def build_bookmarks():
    """扫描 Obsidian Gemini 分类目录 → 生成 Chrome 书签 HTML."""
    if not OBSIDIAN_DIR.exists():
        print(f"未找到目录: {OBSIDIAN_DIR}")
        return

    # 按分类收集
    by_cat = defaultdict(list)
    total = 0

    for cat_dir in OBSIDIAN_DIR.iterdir():
        if not cat_dir.is_dir() or cat_dir.name == ".obsidian":
            continue
        cat_name = cat_dir.name
        prefix = CAT_PREFIX.get(cat_name, "[OTH]")

        for md_file in cat_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            url = extract_gemini_url(content)
            title = ""
            for line in content.split("\n"):
                if line.startswith("title:"):
                    title = line.split("title:", 1)[-1].strip().strip('"')
                    break
            if not title:
                title = md_file.stem

            by_cat[cat_name].append({
                "title": title,
                "url": url,
                "display": f"{prefix} {title}",
                "date": "",
            })
            total += 1

    # 按时间排序（从正文里取日期）
    for cat in by_cat:
        for item in by_cat[cat]:
            m = re.search(r'(\d{4}-\d{2}-\d{2})', item["title"] + item["url"])
            if m:
                item["date"] = m.group(1)

    # 生成书签 HTML
    html_parts = ["""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Gemini 对话书签</TITLE>
<H1>Gemini 对话书签</H1>
<DL><p>
    <DT><H3>Gemini 对话</H3>
    <DL><p>
"""]
    sorted_cats = sorted(by_cat.keys(), key=lambda c: list(CAT_PREFIX.keys()).index(c) if c in CAT_PREFIX else 99)

    for cat in sorted_cats:
        items = by_cat[cat]
        items.sort(key=lambda x: x["date"], reverse=True)
        prefix = CAT_PREFIX.get(cat, "[OTH]")

        html_parts.append(f'        <DT><H3>{prefix} {cat} ({len(items)})</H3>\n        <DL><p>')

        for item in items:
            url = item["url"] or "https://gemini.google.com/app"
            safe_title = item["display"].replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
            html_parts.append(f'            <DT><A HREF="{url}" ADD_DATE="0">{safe_title}</A>')

        html_parts.append('        </DL><p>\n')

    html_parts.append("""    </DL><p>
</DL><p>
""")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"生成书签: {OUTPUT}")
    print(f"共 {total} 条对话，{len(sorted_cats)} 个分类")
    for cat in sorted_cats:
        print(f"  {CAT_PREFIX.get(cat, '[OTH]')} {cat}: {len(by_cat[cat])} 条")

    print(f"\n导入方法: Chrome → 书签管理器 → 导入书签 → 选择此文件")


if __name__ == "__main__":
    build_bookmarks()
