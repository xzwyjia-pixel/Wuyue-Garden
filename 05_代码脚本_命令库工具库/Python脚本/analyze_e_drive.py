#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse tree /F output (GBK encoded), analyze E: drive."""

import re, os
from collections import defaultdict, Counter

path = "E:/E_Files_List.txt"
out_path = "E:/MyCodeProjects/E_drive_analysis.md"

ext_counts = Counter()
cat_counts = defaultdict(int)
folder_file_counts = defaultdict(int)
all_folders = set()
name_counter = Counter()

with open(path, 'rb') as f:
    raw = f.read()
text = raw.decode('gbk', errors='replace')

dir_stack = {}  # depth -> dirname

for raw_line in text.split('\n'):
    line = raw_line.rstrip('\r')
    if not line:
        continue

    # Skip header
    if 'Studying' in line or 'serial' in line or line.strip() == 'E:.':
        continue

    # Count depth: number of │ (U+2502) characters = depth level
    depth = line.count('│')

    is_dir = False
    name_part = ''

    # Check if directory (has ├ or └)
    if '├' in line or '└' in line:
        is_dir = True
        # Find the branch character
        idx = max(line.rfind('├'), line.rfind('└'))
        name_part = line[idx+2:].strip()  # after ├─ or └─
        # Remove brackets
        name_part = name_part.strip('[]')
    else:
        # File line: find content after last │
        idx = line.rfind('│')
        name_part = line[idx+1:].strip()

    if not name_part:
        continue

    # Build parent path
    parent_parts = []
    for d in range(0, depth):
        p = dir_stack.get(d)
        if p:
            parent_parts.append(p)

    if is_dir:
        full_dir = '/'.join(parent_parts + [name_part]) if parent_parts else name_part
        all_folders.add(full_dir)
        dir_stack[depth] = name_part
        # Clear deeper levels
        for k in list(dir_stack.keys()):
            if k > depth:
                del dir_stack[k]
    else:
        current_dir = '/'.join(parent_parts) if parent_parts else ''
        if current_dir:
            folder_file_counts[current_dir] += 1

        _, ext = os.path.splitext(name_part)
        ext = ext.lower()
        ext_counts[ext] += 1

        base = os.path.splitext(name_part)[0]
        clean = re.sub(r'[_\-. ]?\d{8}.*$', '', base)
        clean = re.sub(r'[_\-. ]?(backup|备份|copy|副本|old)\d*$', '', clean, flags=re.I)
        name_counter[(clean, ext)] += 1

total = sum(ext_counts.values())

cat_map = {
    '.mp4': '视频', '.mov': '视频', '.avi': '视频', '.mkv': '视频', '.wmv': '视频',
    '.flv': '视频', '.webm': '视频', '.m4v': '视频', '.ts': '视频',
    '.mp3': '音频', '.wav': '音频', '.flac': '音频', '.aac': '音频', '.ogg': '音频',
    '.m4a': '音频', '.wma': '音频',
    '.jpg': '图片', '.jpeg': '图片', '.png': '图片', '.gif': '图片', '.bmp': '图片',
    '.webp': '图片', '.svg': '图片', '.ico': '图片', '.psd': '图片',
    '.doc': '文档', '.docx': '文档', '.xls': '文档', '.xlsx': '文档', '.ppt': '文档',
    '.pptx': '文档', '.pdf': '文档', '.txt': '文档', '.md': '文档', '.csv': '文档',
    '.html': '文档', '.json': '文档', '.xml': '文档', '.yaml': '文档', '.yml': '文档', '.epub': '文档',
    '.py': '代码', '.js': '代码', '.ts': '代码', '.jsx': '代码', '.tsx': '代码',
    '.java': '代码', '.cpp': '代码', '.go': '代码', '.rs': '代码', '.php': '代码',
    '.vue': '代码', '.css': '代码', '.scss': '代码', '.sh': '代码', '.bat': '代码',
    '.ps1': '代码', '.sql': '代码', '.ipynb': '代码',
    '.exe': '安装包', '.msi': '安装包', '.iso': '安装包',
    '.dmg': '安装包', '.pkg': '安装包', '.apk': '安装包', '.vsix': '安装包',
    '.zip': '压缩包', '.rar': '压缩包', '.7z': '压缩包',
}
for ext, count in ext_counts.items():
    cat = cat_map.get(ext, '其他')
    cat_counts[cat] += count

output = []
o = output.append
o("=" * 70)
o("  E 盘文件分析报告")
o("=" * 70)
o(f"  总文件数: {total:,}")
o(f"  总目录数: {len(all_folders):,}")
o("")

o("-" * 70)
o("  1. 文件类型分布 (Top 40)")
o("-" * 70)
for ext, count in ext_counts.most_common(40):
    o(f"  {ext:<12} {count:>8,}  {count/total*100:>5.1f}%")
rem = total - sum(c for _, c in ext_counts.most_common(40))
if rem:
    o(f"  {'其他':<12} {rem:>8,}")
o("")

o("-" * 70)
o("  2. 按类别统计")
o("-" * 70)
for cat in ['视频', '图片', '音频', '文档', '代码', '安装包', '压缩包', '其他']:
    c = cat_counts.get(cat, 0)
    if c:
        o(f"  {cat:<10} {c:>10,}  {c/total*100:>5.1f}%")
o("")

o("-" * 70)
o("  3. 文件数最多的目录 (Top 30)")
o("-" * 70)
for fold, fcount in sorted(folder_file_counts.items(), key=lambda x: -x[1])[:30]:
    o(f"  {fold:<55} {fcount:>8,} files")
o("")

o("-" * 70)
o("  4. 可能重复/备份的文件")
o("-" * 70)
skip_exts = {'.py', '.js', '.ts', '.md', '.json', '.txt', '.css', '.html', '.xml', '.yml', '.yaml'}
dup_found = 0
for (n, ext), count in name_counter.most_common(200):
    if count > 2 and n and ext not in skip_exts and len(n) > 3:
        dup_found += 1
        if dup_found <= 30:
            o(f"  x{count}  {n}{ext}")
if not dup_found:
    o("  未发现明显重复")
o("")

o("-" * 70)
o("  5. 可能不必要的目录 (node_modules/.git 等)")
o("-" * 70)
known_useless = {'node_modules', '.git', '.vs', '__pycache__', '.mypy_cache',
                 '.pytest_cache', '.claude', 'temp', 'tmp', '.cache'}
found = False
for fold in sorted(all_folders):
    parts = set(fold.lower().replace('\\', '/').split('/'))
    if parts & known_useless:
        fcount = folder_file_counts.get(fold, 0)
        found = True
        o(f"  {fold}  ({fcount} files)")
if not found:
    o("  未发现")
o("")

o("-" * 70)
o("  6. 建议目录层级结构")
o("-" * 70)
o("""  E:/
  ├── 01_工作/
  │   ├── MyCodeProjects/        # 开发项目
  │   ├── 高考规划分析/           # 高考规划
  │   └── 蒙AE270L/               # 车辆文档
  ├── 02_学习/
  │   ├── Tutorials/              # 教程
  │   ├── Books/                  # 电子书
  │   └── Certifications/        # 认证
  ├── 03_多媒体/
  │   ├── Videos/                 # 视频
  │   ├── Music/                  # 音频
  │   ├── Images/                 # 图片
  │   └── Projects/               # 剪辑工程
  ├── 04_工具/
  │   ├── Installers/             # 安装包
  │   └── Portable/               # 便携工具
  ├── 05_知识库/
  │   └── Obsidian/               # 笔记
  ├── 06_归档/
  │   ├── Backups/                # 备份
  │   └── Old_Projects/           # 旧项目
  └── 07_暂存/
      └── Inbox/                  # 待整理
""")

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"DONE: {out_path} -- {total} files, {len(all_folders)} dirs parsed")
