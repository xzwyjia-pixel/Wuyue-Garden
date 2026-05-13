#!/usr/bin/env python3
"""
obsidian_ops.py — 10 AI-Obsidian Bridge Features
用法: python obsidian_ops.py <command> [args]

Commands:
  voice    "text"    语音转笔记
  webclip  <url>     网页剪辑
  tag                批量标签/元数据
  wikilink           双链挖掘
  daily              每日笔记自动填充
  qa       "问题"   知识库问答
  ocr      <image>  图片 OCR 入库
  gitviz             Git 版本可视化
  sync     <dir>    跨 vault 同步
  annotate <file>    AI 批注模式
"""

import requests, sys, json, os, re, datetime, subprocess, urllib.parse
from pathlib import Path
import pytesseract
from PIL import Image

BASE = "http://127.0.0.1:27123"
HEADERS = {
    "Authorization": "Bearer 8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c",
    "Content-Type": "application/json",
}
INBOX = "收件箱"
VAULT_ROOT = Path("E:/Obsidian")
PY = sys.executable or "python"

# Tesseract OCR config
_PYT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_PYT_DATA = os.path.expanduser("~") + "/tessdata"
if os.path.exists(_PYT_PATH):
    pytesseract.pytesseract.tesseract_cmd = _PYT_PATH
if os.path.isdir(_PYT_DATA):
    os.environ.setdefault("TESSDATA_PREFIX", _PYT_DATA)


def _ensure_dirs():
    """Ensure standard vault directories exist."""
    for d in [INBOX, "日程安排", "知识库", "速查"]:
        local = VAULT_ROOT / d
        if not local.exists():
            local.mkdir(parents=True, exist_ok=True)
            print(f"✓ 创建目录: {d}")

# run on import
_ensure_dirs()

def _u(path):
    """URL-encode each path segment."""
    return urllib.parse.quote(path, safe='/:@!$&\'()*+,;=-._~')

def _get(path):
    r = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def _put(path, content):
    r = requests.put(f"{BASE}/vault/{_u(path)}", headers=HEADERS,
                     json={"content": content}, timeout=15)
    return r.status_code in (200, 201, 204)

def _read(path, prefer_local=True):
    """Read note content. Try local filesystem first (fast for batch ops)."""
    if prefer_local:
        local = VAULT_ROOT / path
        if local.exists():
            return local.read_text(encoding="utf-8")
    r = requests.get(f"{BASE}/vault/{_u(path)}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    ct = r.headers.get("Content-Type", "")
    if "application/json" in ct:
        return r.json()["content"]
    return r.text

def _list():
    return _get("/vault/")["files"]

def _mkdir(path):
    r = requests.post(f"{BASE}/vault/{_u(path)}", headers=HEADERS, timeout=15)
    return r.status_code in (200, 201, 204)

def _del(path):
    r = requests.delete(f"{BASE}/vault/{_u(path)}", headers=HEADERS, timeout=15)
    return r.status_code == 204

def _walk_vault(root=None):
    """Return list of .md file paths (relative to VAULT_ROOT).
    Uses local filesystem for speed. Limits to root subdir if given."""
    base = VAULT_ROOT
    search = base / root if root else base
    if not search.exists():
        print(f"⚠ 目录不存在: {search}")
        return []
    files = []
    for md in sorted(search.rglob("*.md")):
        rel = md.relative_to(base)
        files.append(str(rel.as_posix()))
    return files


# ── 1. 语音转笔记 ──

def cmd_voice(args):
    """Usage: voice <text> [title]"""
    if not args:
        print("❌ voice <text> [title]")
        return
    text = args[0]
    title = args[1] if len(args) > 1 else f"语音笔记_{datetime.date.today()}"
    note = f"""---
created: {datetime.datetime.now().isoformat()}
type: voice-note
tags: [语音]
---

# {title}

> 语音转写

{text}
"""
    path = f"{INBOX}/{title}.md"
    ok = _put(path, note)
    print(f"{'✓' if ok else '✗'} {path}")


# ── 2. 网页剪辑 ──

def cmd_webclip(args):
    """Usage: webclip <url> [title]"""
    if not args:
        print("❌ webclip <url> [title]")
        return
    url = args[0]
    title = args[1] if len(args) > 1 else f"网页_{datetime.date.today()}"
    try:
        import trafilatura
        fetched = trafilatura.fetch_url(url)
        if not fetched:
            # fallback: raw html text extract
            import html
            import requests as rq
            raw = rq.get(url, timeout=20, headers={
                "User-Agent": "Mozilla/5.0"}).text
            text = re.sub(r'<[^>]+>', ' ', raw)
            text = html.unescape(re.sub(r'\s+', ' ', text)).strip()[:5000]
        else:
            text = trafilatura.extract(fetched, output_format="markdown",
                                       include_links=True, include_images=False) or ""
    except ImportError:
        import html
        import requests as rq
        raw = rq.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0"}).text
        text = re.sub(r'<[^>]+>', ' ', raw)
        text = html.unescape(re.sub(r'\s+', ' ', text)).strip()[:5000]
    note = f"""---
source: {url}
clipped: {datetime.datetime.now().isoformat()}
tags: [网页剪辑]
---

# {title}

来源: {url}

---
{text}
"""
    path = f"{INBOX}/{title}.md"
    ok = _put(path, note)
    print(f"{'✓' if ok else '✗'} {path}")


# ── 3. 批量标签/元数据 ──

# 内容 → 标签映射规则
TAG_RULES = [
    (r'伟联|VLink|私有云|超融合|信创|海光|Hygon', ['项目/伟联']),
    (r'苏苏|清晨烟火|直播|视频号|宝妈', ['项目/苏苏直播']),
    (r'华德福|Waldorf|Steiner|教育|育儿', ['知识/教育']),
    (r'curl|API|REST|requests|JSON|endpoint', ['技术/API']),
    (r'python|脚本|自动化|script|cli', ['技术/Python']),
    (r'obsidian|笔记|vault|知识库|markdown|md', ['工作流/Obsidian']),
    (r'规则甄查|审计|合规|audit|compliance', ['项目/规则甄查']),
    (r'招标|控标|集成商|SI|水利', ['项目/伟联']),
    (r'直播|短视频|运营|流量|权重|算法', ['项目/苏苏直播']),
]

def _infer_tags(content, title):
    found = set()
    combined = f"{title}\n{content}"
    for pattern, tags in TAG_RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            found.update(tags)
    if not found:
        found.add("inbox")
    return sorted(found)

def cmd_tag(args):
    """批量扫描 vault 文件，按内容语义添加 tags 和 frontmatter"""
    dry = "--dry" in args or "-n" in args
    print(f"{'[DRY RUN]' if dry else ''} 扫描 vault 标签...")
    files = _walk_vault()
    updated = 0
    for fp in files:
        if not fp.endswith(".md"):
            continue
        content = _read(fp)
        # skip if has frontmatter with tags
        has_tags = bool(re.search(r'^tags:\s*\[', content, re.MULTILINE))
        if has_tags and not dry:
            continue
        tags = _infer_tags(content, fp)
        title = Path(fp).stem
        # add/update frontmatter
        new_content = f"""---
created: {datetime.date.today().isoformat()}
tags: [{', '.join(tags)}]
title: {title}
---

{content}
"""
        if not dry:
            _put(fp, new_content)
        updated += 1
        print(f"  {'~' if dry else '✓'} {fp} → {tags}")
    print(f"\n总计: {updated} 文件{' (模拟)' if dry else '已更新'}")


# ── 4. 双链挖掘 ──

def _extract_keywords(content):
    """Extract meaningful Noun phrases for link matching."""
    # Chinese segments 2-6 chars, English words capitalized 3+ chars
    words = set()
    cn = re.findall(r'[一-鿿]{2,6}', content)
    words.update(cn)
    # Title-case English terms
    en = re.findall(r'\b[A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,}){0,2}', content)
    words.update(en)
    return {w for w in words if len(w) >= 2}

def cmd_wikilink(args):
    """扫描全部笔记，发现隐含关联，插入 [[wikilinks]]"""
    dry = "--dry" in args or "-n" in args
    min_score = int(args[args.index("--min") + 1]) if "--min" in args else 2
    print(f"{'[DRY RUN]' if dry else ''} 挖掘双链...")

    files = _walk_vault()
    # build kw → [file] index
    kw_index = {}
    note_kws = {}
    for fp in files:
        if not fp.endswith(".md"):
            continue
        content = _read(fp)
        kws = _extract_keywords(content)
        note_kws[fp] = kws
        for kw in kws:
            kw_index.setdefault(kw, []).append(fp)

    linked = 0
    for fp, kws in note_kws.items():
        content = _read(fp)
        existing_links = set(re.findall(r'\[\[([^\]]+)\]\]', content))
        candidates = []
        for kw in kws:
            # find notes whose filename/title matches this keyword
            for candidate in kw_index.get(kw, []):
                stem = Path(candidate).stem
                if stem in existing_links or stem == Path(fp).stem:
                    continue
                candidates.append((kw, stem))
        # dedupe by stem
        seen = set()
        to_link = []
        for kw, stem in candidates:
            if stem not in seen:
                seen.add(stem)
                to_link.append((kw, stem))
        if to_link and not dry:
            new_content = content
            for kw, stem in to_link:
                # avoid double-wrapping and code blocks
                link = f"[[{stem}]]"
                if link not in new_content:
                    # replace first plain occurrence
                    new_content = new_content.replace(kw, link, 1)
            if new_content != content:
                _put(fp, new_content)
                linked += 1
                print(f"  ✓ {fp}: {len(to_link)} links added")
        elif to_link:
            linked += 1
            print(f"  ~ {fp}: {[s for _, s in to_link]}")
    print(f"\n总计: {linked} 文件{' (模拟)' if dry else '已添加双链'}")


# ── 5. 每日笔记自动填充 ──

def cmd_daily(args):
    """自动创建今日笔记（带周报/日报模板）"""
    today = datetime.date.today()
    weekday = today.strftime("%A")
    title = f"日报_{today.isoformat()}"
    note = f"""---
created: {today.isoformat()}
type: daily
tags: [日报, {today.strftime('%Y年%#m月')}]
---

# {title} ({weekday})

## ✅ 今日任务
- [ ]

## 📝 工作记录
-

## 💡 灵感/备注
-

## 📊 明日计划
- [ ]

---
*自动创建于 {datetime.datetime.now().isoformat()}*
"""
    path = f"日程安排/{title}.md"
    ok = _put(path, note)
    print(f"{'✓' if ok else '✗'} {path}")


# ── 6. 知识库问答 ──

def cmd_qa(args):
    """Usage: qa <question> — 读取 vault 搜索相关内容后回答"""
    if not args:
        print("❌ qa <question>")
        return
    question = " ".join(args)
    print(f"🔍 检索: {question}")
    files = _walk_vault()
    results = []
    for fp in files:
        if not fp.endswith(".md"):
            continue
        content = _read(fp)
        # simple keyword match scoring
        q_words = set(re.findall(r'[一-鿿\w]+', question.lower()))
        c_words = set(re.findall(r'[一-鿿\w]+', content.lower()))
        score = len(q_words & c_words)
        if score >= 1:
            results.append((score, fp, content[:500]))
    results.sort(reverse=True)
    top = results[:5]
    if not top:
        print("未找到相关笔记。")
        return
    print(f"\n找到 {len(results)} 条相关，展示前 {len(top)}:\n")
    for score, fp, snippet in top:
        print(f"── [{score}] {fp}")
        # extract relevant paragraph
        lines = snippet.split("\n")
        relevant = [l for l in lines if any(w in l for w in re.findall(
            r'[一-鿿]{2,}', question))]
        if relevant:
            for l in relevant[:3]:
                print(f"   {l.strip()[:200]}")
        else:
            print(f"   {lines[0][:200]}")
        print()


# ── 7. 图片 OCR 入库 ──

def cmd_ocr(args):
    """Usage: ocr <image_path> [title] — OCR 图片内容存入笔记"""
    if not args:
        print("❌ ocr <image_path> [title]")
        return
    img_path = Path(args[0])
    if not img_path.exists():
        print(f"✗ 文件不存在: {img_path}")
        return
    title = args[1] if len(args) > 1 else f"OCR_{img_path.stem}"
    try:
        img = Image.open(str(img_path))
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
    except Exception as e:
        print(f"⚠ OCR 失败: {e}")
        text = f"[图片待处理: {img_path}]"
    note = f"""---
created: {datetime.datetime.now().isoformat()}
type: ocr
source: {img_path}
tags: [OCR]
---

# {title}

## OCR 识别结果

```
{text.strip()}
```
"""
    path = f"{INBOX}/{title}.md"
    ok = _put(path, note)
    print(f"{'✓' if ok else '✗'} {path}")
    if text.strip() and "[图片待OCR]" not in text:
        print(f"识别文字: {len(text)} 字符")


# ── 8. Git 版本可视化 ──

def _git(args, cwd):
    """Run git with binary capture to handle Chinese filenames on Windows."""
    p = subprocess.Popen(["git"] + args, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(timeout=15)
    return out.decode("utf-8", errors="replace"), err.decode("utf-8", errors="replace"), p.returncode

def cmd_gitviz(args):
    """分析 vault Git 历史，展示笔记演变脉络"""
    vault = str(VAULT_ROOT)
    if not (Path(vault) / ".git").exists():
        print(f"✗ 不是 Git 仓库: {vault}")
        return
    days = 30
    if args and args[0].isdigit():
        days = int(args[0])

    print(f"📊 最近 {days} 天变化统计:\n")
    since = f"--since='{days} days ago'"
    try:
        out, _, _ = _git(["log", "--oneline", since], vault)
        commits = [l for l in out.strip().split("\n") if l.strip()]
        print(f"提交数: {len(commits)}")

        # files changed (using git diff --name-only)
        out2, _, _ = _git(
            ["diff", "--name-only", f"@{'{'}1.{days}.days.ago{'}'}",
             "--diff-filter=AMDR"], vault)
        changed = [l for l in out2.strip().split("\n") if l.strip()]
        print(f"变动文件: {len(changed)}")

        # top active files
        from collections import Counter
        file_counts = Counter()
        out3, _, _ = _git(
            ["log", "--name-only", "--pretty=format:", since], vault)
        for f in out3.strip().split("\n"):
            f = f.strip()
            if f and f.endswith(".md"):
                file_counts[f] += 1
        print("\n最活跃笔记:")
        for f, cnt in file_counts.most_common(15):
            print(f"  {cnt:3d} 次  {f}")

        # author stats
        out4, _, _ = _git(["shortlog", "-sn", since], vault)
        print(f"\n贡献者:\n{out4}")

        # generate summary note
        summary = f"""---
created: {datetime.datetime.now().isoformat()}
type: git-report
tags: [git, 版本可视化]
---

# Git 版本报告 ({datetime.date.today()})

## 概览
- 统计周期: 最近 {days} 天
- 提交数: {len(commits)}
- 变动文件: {len(changed)}

## 活跃文件
| 次数 | 文件 |
|------|------|
""" + "\n".join(f"| {cnt} | {f} |" for f, cnt in file_counts.most_common(20))

        report_path = f"速查/Git报告_{datetime.date.today()}.md"
        _put(report_path, summary)
        print(f"\n✓ 报告已保存: {report_path}")

    except subprocess.TimeoutExpired:
        print("✗ Git 命令超时")
    except FileNotFoundError:
        print("✗ Git 未安装")


# ── 9. 跨 vault 同步 ──

def cmd_sync(args):
    """Usage: sync <source_dir> [target_dir] — 将外部 markdown 文件同步到 Obsidian"""
    if not args:
        print("❌ sync <source_dir> [target_dir]")
        return
    src = Path(args[0])
    if not src.exists():
        print(f"✗ 源目录不存在: {src}")
        return
    target_dir = args[1] if len(args) > 1 else "知识库"
    import shutil
    dest_base = VAULT_ROOT / target_dir
    dest_base.mkdir(parents=True, exist_ok=True)

    count = 0
    for md in sorted(src.rglob("*.md")):
        # skip hidden dirs
        if any(p.startswith(".") for p in md.parts):
            continue
        dest = dest_base / md.name
        shutil.copy2(str(md), str(dest))
        count += 1
        print(f"  ✓ {dest.name}")
    print(f"\n同步完成: {count} 文件 → {dest_base}")


# ── 10. AI 批注模式 ──

def cmd_annotate(args):
    """Usage: annotate <file_path> — 读取笔记，追加 AI 洞察批注"""
    if not args:
        print("❌ annotate <file_path>")
        return
    path = args[0]
    try:
        content = _read(path)
    except requests.HTTPError:
        # try local
        local = VAULT_ROOT / path
        if local.exists():
            content = local.read_text(encoding="utf-8")
        else:
            print(f"✗ 找不到文件: {path}")
            return

    # extract key sections and add insights
    lines = content.split("\n")
    insights = []

    # detect paragraphs that could use analysis
    for i, line in enumerate(lines):
        line_s = line.strip()
        # detect list items about decisions
        if re.match(r'^[-*\d+.]+\s+(决定|选择|采用|使用|建议|推荐)\s*[:：]', line_s):
            insights.append((i, line_s, "decision"))

    # build annotated version
    if insights:
        annotated = content + "\n\n---\n## 🤖 AI 洞察\n\n"
        for line_no, text, kind in insights:
            if kind == "decision":
                annotated += f"> [!AI-insight] 决策分析\n> 行 {line_no + 1}: 「{text.strip()[:80]}」\n> 建议考虑替代方案并记录决策理由。\n\n"
        annotated += f"*AI 批注于 {datetime.datetime.now().isoformat()}*\n"
        if _put(path, annotated):
            print(f"✓ 已添加 {len(insights)} 条 AI 批注 → {path}")
        else:
            print(f"✗ 写入失败: {path}")
    else:
        print("未发现需要批注的决策点。")


# ── CLI Router ──

CMDS = {
    "voice": cmd_voice,
    "webclip": cmd_webclip,
    "tag": cmd_tag,
    "wikilink": cmd_wikilink,
    "daily": cmd_daily,
    "qa": cmd_qa,
    "ocr": cmd_ocr,
    "gitviz": cmd_gitviz,
    "sync": cmd_sync,
    "annotate": cmd_annotate,
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        print("可用命令: " + ", ".join(CMDS))
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    CMDS[cmd](args)

if __name__ == "__main__":
    main()
