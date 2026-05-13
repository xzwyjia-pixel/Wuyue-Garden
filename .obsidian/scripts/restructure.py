#!/usr/bin/env python3
"""
Obsidian vault semantic restructure v2.
Safe approach: rename ALL files, reclassify ONLY inbox (1218 files),
preserve existing directory structure for 01-06.

Run: python restructure.py [--dry-run|--execute]
"""

import os, re, json, shutil, sys, hashlib
from datetime import datetime
from collections import defaultdict

VAULT = "E:/Obsidian"
EXCLUDE = {".obsidian", ".git", ".makemd", ".smart-env"}
EXCLUDE_DIRS = {os.path.join(VAULT, "07_素材资源_截图附件模板")}

STOP_WORDS = set("""
的了在是我有不和就这都也而啊吧吗嗯呢呀哦哈哇哟
the a an is it its are was were be been being have has had
do does did doing get got making make made will would can could
shall should may might must need dare this that these those
what which who whom when where why how all each every both
few more most some any no not only own same so than too very
just also well even still already yet now here there then
""".split())

DIRECTORIES = [
    "00_收件箱_Inbox",
    "01_个人系统_模板规则配置",
    "02_进行中项目_当前在做",
    "03_归档项目_历史完结",
    "04_工作知识库_文档政策方案",
    "05_代码脚本_命令库工具库",
    "06_AI对话归档_豆包GeminiClaude",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def unpack_content(raw):
    """Unpack JSON-wrapped content (Gemini/Claude exports)."""
    s = raw.strip()
    if s.startswith('{"') or s.startswith('[{'):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                if data and isinstance(data[0], dict) and 'content' in data[0]:
                    return '\n\n'.join(d.get('content', '') for d in data if isinstance(d, dict))
            if isinstance(data, dict):
                for key in ('content', 'text', 'body', 'markdown'):
                    if key in data and isinstance(data[key], str):
                        return data[key]
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return raw

def strip_frontmatter(content):
    """Robust YAML frontmatter removal."""
    if not content.startswith('---'):
        return content
    lines = content.split('\n')
    for i in range(1, min(len(lines), 100)):
        if lines[i].strip() == '---':
            return '\n'.join(lines[i+1:])
    return content

def get_frontmatter_field(content, field):
    """Get a value from YAML frontmatter by field name."""
    m = re.search(rf'^{field}:\s*(.+)', content[:2000], re.MULTILINE)
    return m.group(1).strip().strip('"\'') if m else ''

def extract_date(content, filename, filepath):
    """Extract date from frontmatter, filename, or mtime."""
    # Frontmatter date
    d = get_frontmatter_field(content, 'date')
    if d and re.match(r'\d{4}-\d{2}-\d{2}', d):
        return d[:10]
    # Date in body
    body = strip_frontmatter(content)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', body[:500])
    if m:
        return m.group(1)
    # Date in filename
    m = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', filename)
    if m:
        return m.group(1).replace('/', '-')
    return datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d')

def extract_title(content, filename):
    """First heading from body (after frontmatter)."""
    body = strip_frontmatter(content)[:3000]
    m = re.search(r'^#\s+(.+)', body, re.MULTILINE)
    if m:
        t = re.sub(r'[\[\]{}<>|*`#！？\\/:*?"\n\r]', '', m.group(1).strip())
        return re.sub(r'\s+', '_', t)[:50]
    # First meaningful line
    for line in body.split('\n')[:15]:
        line = line.strip()
        if line and len(line) > 3 and not line.startswith('[') and not line.startswith('>'):
            t = re.sub(r'[\[\]{}<>|*`#！？\\/:*?"\n\r]', '', line)[:50]
            return re.sub(r'\s+', '_', t)
    return ''

def extract_keywords(content, max_kw=3):
    """Top keywords from body content."""
    body = strip_frontmatter(content)[:3000]
    text = re.sub(r'```[\s\S]*?```', '', body)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'[#*_~>|\[\]()\-={}]', ' ', text)

    words = []
    words.extend(re.findall(r'[一-鿿]{3,}', text))  # CN 3+ chars
    words.extend(w.lower() for w in re.findall(r'[a-zA-Z]{4,}', text)  # EN 4+ chars
                 if w.lower() not in STOP_WORDS)
    words = [w for w in words if w not in STOP_WORDS]

    freq = defaultdict(int)
    for w in words:
        freq[w] += 1
    top = sorted(freq.items(), key=lambda x: -x[1])
    return [w for w, c in top[:max_kw]]

def generate_filename(fname, content, fpath):
    """YYYY-MM-DD_Title.md — clean, readable."""
    date = extract_date(content, fname, fpath)
    title_raw = extract_title(content, fname)
    # Windows-safe: strip forbidden chars
    title = re.sub(r'[\\/:*?"<>|！#？\n\r]', '', title_raw)[:50]
    kw = extract_keywords(content, max_kw=2)

    parts = [date]
    if title:
        parts.append(title)
    elif kw:
        parts.append(kw[0])
    else:
        parts.append('note')

    name = re.sub(r'_+', '_', '_'.join(parts)) + '.md'
    if len(name) > 220:
        base, ext = os.path.splitext(name)
        name = base[:215] + ext
    return name

def extract_subfolder(rel_dir):
    """Get first subfolder below top-level dir. rel_dir is directory path (no filename)."""
    parts = rel_dir.replace('\\', '/').split('/')
    if len(parts) >= 2 and parts[1]:
        return parts[1]
    return ''

# ── Inbox classification (conservative) ──

INBOX_RULES = [
    (6, "Gemini", ["source: gemini", "source_gemini", "source: claude", "source_claude",
                   "你是一个.*ai", "你是一个.*助手", "作为ai助手",
                   "请生成", "帮我写", "给我生成",
                   "这是你第.*次回答", "重新输出", "帮我整理"]),
    (2, "直播复盘", ["直播", "douyin", "抖音", "带货", "直播间", "曝光", "进入率"]),
    (2, "审计项目", ["审计", "hclg", "kaldi", "asr", "交换机", "路由器"]),
    (4, "参考文档", ["指南", "教程", "参考文档", "说明书", "操作指南",
                     "技术规格"]),
    (4, "Prompts", ["prompt:", "提示词:", "system prompt"]),
    (1, "模板", ["模板", "template", "日记模板", "周记模板"]),
]

def classify_inbox(content, fname):
    """Classify an inbox file. Returns (dir_idx, subfolder) or (0, '待分类')."""
    front = content[:3000].lower()
    body = strip_frontmatter(content)[:5000].lower()
    text = front + '\n' + body + '\n' + fname.lower()

    for idx, sub, patterns in INBOX_RULES:
        for p in patterns:
            if p.lower() in text or re.search(p.lower(), text):
                return idx, sub
    return 0, '待分类'

# ── Main ──

def scan():
    files = []
    total = sum(1 for root, dirs, fnames in os.walk(VAULT) for f in fnames
                if (f.endswith('.md') or f.endswith('.txt'))
                and not any(p in EXCLUDE for p in os.path.relpath(root, VAULT).split(os.sep))
                and not any(root.startswith(d) for d in EXCLUDE_DIRS))
    log(f"Total files: {total}")

    idx = 0
    for root, dirs, fnames in os.walk(VAULT):
        rel = os.path.relpath(root, VAULT)
        parts = rel.split(os.sep)
        if any(p in EXCLUDE for p in parts): continue
        if any(root.startswith(d) for d in EXCLUDE_DIRS): continue

        for fname in fnames:
            if not (fname.endswith('.md') or fname.endswith('.txt')): continue
            idx += 1
            if idx % 1000 == 0: log(f"  {idx}/{total}")
            fpath = os.path.join(root, fname)

            try:
                sz = os.path.getsize(fpath)
                raw = ''
                if sz < 512*1024:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        raw = f.read()
                # Unpack JSON-wrapped content (Gemini exports)
                content = unpack_content(raw) if raw else ''
            except:
                content = ''

            # Determine target directory
            in_inbox = rel.startswith('00_收件箱_Inbox')
            if in_inbox:
                dir_idx, subfolder = classify_inbox(content, fname)
            else:
                # Preserve existing directory structure
                dir_idx = None
                for di, d in enumerate(DIRECTORIES):
                    if rel.startswith(d):
                        dir_idx = di
                        subfolder = extract_subfolder(rel)
                        if not subfolder:
                            subfolder = ''
                        break
                if dir_idx is None:
                    dir_idx, subfolder = 0, '待分类'

            new_name = generate_filename(fname, content, fpath)

            files.append({
                'path': fpath,
                'rel': rel,
                'filename': fname,
                'stem': os.path.splitext(fname)[0],
                'new_name': new_name,
                'dir_idx': dir_idx,
                'subfolder': subfolder,
            })

    log(f"Scan done: {len(files)} files")
    return files

def resolve_collisions(files):
    """Append _2, _3 etc for duplicate new names."""
    by_name = defaultdict(list)
    for f in files:
        by_name[f['new_name']].append(f)
    for n, flist in by_name.items():
        if len(flist) > 1:
            base, ext = os.path.splitext(n)
            for i, f in enumerate(flist[1:], 2):
                f['new_name'] = f"{base}_{i}{ext}"

def build_wikilink_map(files):
    """Old stem → new stem."""
    m = {}
    for f in files:
        old = f['stem']
        new = os.path.splitext(f['new_name'])[0]
        if old != new:
            m[old.lower()] = new
    return m

def update_wikilinks(files, mapping, dry_run=True):
    """Replace [[old]] → [[new]] in all files."""
    changes = 0
    lc = {}
    for old, new in mapping.items():
        lc[old] = new
        lc[old.replace('_', ' ')] = new
        lc[old.replace('_', ' ').replace('-', ' ')] = new

    for f in files:
        try:
            with open(f['path'], 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
        except:
            continue

        new_content = content
        modified = False
        for link in re.findall(r'\[\[([^\]]+)\]\]', content):
            bare = link.split('|')[0]
            key = bare.lower().replace('\\', '/')
            if key in lc:
                alias = f'|{link.split("|")[1]}' if '|' in link else ''
                new_content = new_content.replace(f'[[{link}]]', f'[[{lc[key]}{alias}]]')
                modified = True

        if modified:
            changes += 1
            if not dry_run:
                with open(f['path'], 'w', encoding='utf-8') as fh:
                    fh.write(new_content)

    log(f"Wikilink updates: {changes} files")
    return changes

def execute(files, dry_run=True):
    """Rename + move files."""
    moves = []
    for f in files:
        target = os.path.join(VAULT, DIRECTORIES[f['dir_idx']], f['subfolder'], f['new_name'])
        if f['path'] != target:
            moves.append((f['path'], target, f))
    log(f"Moves/renames: {len(moves)}")

    if not dry_run:
        for old, new, f in moves:
            os.makedirs(os.path.dirname(new), exist_ok=True)
            shutil.move(old, new)
    return moves

def cleanup(dry_run=True):
    """Remove empty dirs."""
    removed = []
    for root, dirs, fnames in os.walk(VAULT, topdown=False):
        if root == VAULT: continue
        rel = os.path.relpath(root, VAULT)
        if any(p in EXCLUDE for p in rel.split(os.sep)): continue
        if not os.listdir(root):
            removed.append(rel)
            if not dry_run:
                os.rmdir(root)
    log(f"Empty dirs: {len(removed)}")
    return removed

def report(files, moves, changes, inbox_count, dupes):
    lines = ["# Obsidian Vault Restructure Report",
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
             "## 1. 总体统计",
             f"- 总文件数: {len(files)}",
             f"- 需移动/改名: {len(moves)}",
             f"- Wikilink 更新: {changes} 个文件",
             f"- 重复分组: {len(dupes)}",
             f"- Inbox 待分类: {inbox_count}\n",
             "## 2. 新目录结构"]

    for i, d in enumerate(DIRECTORIES):
        df = [f for f in files if f['dir_idx'] == i]
        sfs = set(f['subfolder'] for f in df)
        lines.append(f"\n### {d} ({len(df)} files)")
        for sf in sorted(sfs):
            cnt = len([f for f in df if f['subfolder'] == sf])
            lines.append(f"  - {sf}/ ({cnt})")
    lines.append("")

    renamed = [m for m in moves if os.path.basename(m[0]) != os.path.basename(m[1])]
    lines.append(f"## 3. 改名文件（前 50）\n")
    for old, new, _ in renamed[:50]:
        lines.append(f"  {os.path.relpath(old, VAULT)}")
        lines.append(f"  → {os.path.relpath(new, VAULT)}\n")
    if len(renamed) > 50:
        lines.append(f"  ...及 {len(renamed)-50} 个更多\n")

    inbox = [f for f in files if f['dir_idx'] == 0]
    lines.append(f"## 4. 待复核 (Inbox: {len(inbox)} 个)\n")
    for f in inbox[:30]:
        lines.append(f"  - {f['subfolder']}/{f['new_name']} (原: {f['rel']})")
    if len(inbox) > 30:
        lines.append(f"  ...及 {len(inbox)-30} 个\n")

    lines.append("## 5. 维护规则\n"
                 "- 新笔记放 00_收件箱_Inbox/待分类/\n"
                 "- 定期运行本脚本重新分类 inbox\n"
                 "- 命名格式: YYYY-MM-DD_核心主题.md\n")

    return '\n'.join(lines)

def main():
    dry = '--execute' not in sys.argv
    if dry: log("=== DRY RUN ===")

    files = scan()

    # Count inbox
    inbox_count = len([f for f in files if f['dir_idx'] == 0])

    # Detect duplicate content
    dupes = defaultdict(list)
    for f in files:
        dupes[f['stem']].append(f)
    dupes = {k: v for k, v in dupes.items() if len(v) > 1}
    log(f"Duplicate filename groups: {len(dupes)}")

    resolve_collisions(files)

    mapping = build_wikilink_map(files)
    log(f"Name changes: {len(mapping)}")

    changes = update_wikilinks(files, mapping, dry)
    moves = execute(files, dry)
    removed = cleanup(dry)

    rpt = report(files, moves, changes, inbox_count, dupes)
    rpt_path = os.path.join(VAULT, ".obsidian", "scripts", "restructure-report.md")
    with open(rpt_path, 'w', encoding='utf-8') as f:
        f.write(rpt)
    log(f"Report: {rpt_path}")

    if dry: log("\n=== DRY RUN DONE. Run with --execute to apply ===")

if __name__ == '__main__':
    main()
