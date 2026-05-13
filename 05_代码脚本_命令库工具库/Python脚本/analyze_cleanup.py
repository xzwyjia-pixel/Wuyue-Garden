#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deep cleanup analysis for E: drive. Reports only, no deletion."""

import re, os
from collections import defaultdict, Counter

path = "E:/E_Files_List.txt"
out_path = "E:/MyCodeProjects/E_cleanup_plan.md"

with open(path, 'rb') as f:
    raw = f.read()
text = raw.decode('gbk', errors='replace')

dir_stack = {}
files_by_dir = defaultdict(list)
all_dirs = set()
all_files = []

for raw_line in text.split('\n'):
    line = raw_line.rstrip('\r')
    if not line or 'Studying' in line or 'serial' in line or line.strip() == 'E:.':
        continue
    depth = line.count('│')
    is_dir = '├' in line or '└' in line
    if is_dir:
        idx = max(line.rfind('├'), line.rfind('└'))
        name_part = line[idx+2:].strip().strip('[]')
        if not name_part:
            continue
        parent_parts = [dir_stack.get(d, '') for d in range(depth) if dir_stack.get(d)]
        full_dir = '/'.join(parent_parts + [name_part]) if parent_parts else name_part
        all_dirs.add(full_dir)
        dir_stack[depth] = name_part
        for k in list(dir_stack.keys()):
            if k > depth:
                del dir_stack[k]
    else:
        idx = line.rfind('│')
        name_part = line[idx+1:].strip()
        if not name_part:
            continue
        parent_parts = [dir_stack.get(d, '') for d in range(depth) if dir_stack.get(d)]
        current_dir = '/'.join(parent_parts) if parent_parts else ''
        _, ext = os.path.splitext(name_part)
        all_files.append({
            'name': name_part,
            'ext': ext.lower(),
            'dir': current_dir,
            'path': f"{current_dir}/{name_part}" if current_dir else name_part,
        })
        files_by_dir[current_dir].append({'name': name_part, 'ext': ext.lower()})

output = []
o = output.append

o("# E 盘清理方案\n")

# ─── 1. Installer duplicates ───
o("## 1. 重复安装包识别\n")
o("| 文件名 | 出现次数 | 所在目录 |")
o("|--------|---------|---------|")

inst_exts = {'.exe', '.msi', '.iso', '.vsix', '.apk'}
raw_installers = defaultdict(list)
for f in all_files:
    if f['ext'] in inst_exts:
        raw_installers[f['name']].append(f['dir'])

# Filter: count > 1
dup_inst = {k: v for k, v in raw_installers.items() if len(v) > 1}
if dup_inst:
    for name, dirs in sorted(dup_inst.items(), key=lambda x: -len(x[1]))[:40]:
        dirs_str = "<br>".join(sorted(set(dirs))[:5])
        if len(set(dirs)) > 5:
            dirs_str += f"<br>...等 {len(set(dirs))} 个位置"
        o(f"| {name} | x{len(dirs)} | {dirs_str} |")
else:
    o("| 未发现重复安装包 | | |")

# ─── 2. WeChat bloat ───
o("\n## 2. WeChat 文件分析\n")
wc_dirs = [d for d in all_dirs if 'WeChat' in d or '微信' in d]
if wc_dirs:
    wc_files = [f for f in all_files if 'WeChat' in f['path'] or '微信' in f['path']]
    wc_exts = Counter(f['ext'] for f in wc_files)
    o(f"总文件数: **{len(wc_files):,}**\n")
    o(f"目录数: {len(wc_dirs)}\n")
    o("| 扩展名 | 数量 |")
    o("|--------|------|")
    for ext, count in wc_exts.most_common(15):
        o(f"| {ext} | {count:,} |")
    # Biggest WeChat folders
    wc_folders = Counter(f['dir'] for f in wc_files)
    o("\n最大 WeChat 目录:")
    for fold, count in wc_folders.most_common(10):
        o(f"- {fold}: {count:,} files")
else:
    o("未发现 WeChat 文件\n")

# ─── 3. Python cache files ───
o("\n## 3. Python 缓存文件 (__pycache__/.pyc)\n")
pyc_files = [f for f in all_files if '__pycache__' in f['path'] or f['ext'] == '.pyc']
o(f"总数: **{len(pyc_files):,}** 个 .pyc/__pycache__ 文件\n")
if pyc_files:
    o("最大缓存目录:")
    pyc_folders = Counter(f['dir'] for f in pyc_files)
    for fold, count in pyc_folders.most_common(15):
        o(f"- {fold}: {count:,} files")

# ─── 4. Duplicate images (AI Work) ───
o("\n## 4. AI Work 重复图片\n")
aiwork_files = [f for f in all_files if 'AI Work' in f['path']]
# Count filenames without path
aiwork_names = Counter(f['name'] for f in aiwork_files)
dup_imgs = {k: v for k, v in aiwork_names.items() if v > 1 and k.lower().endswith(('.png', '.jpg', '.jpeg'))}
if dup_imgs:
    o(f"AI Work 目录共有 {len(aiwork_files):,} 文件\n")
    o(f"其中重复图片 **{len(dup_imgs)}** 组\n")
    for name, count in sorted(dup_imgs.items(), key=lambda x: -x[1])[:20]:
        o(f"- `{name}`: x{count}")
else:
    o(f"AI Work 目录共有 {len(aiwork_files):,} 文件，无重复图片\n")

# ─── 5. E:\ root files ───
o("\n## 5. E:\\ 根目录杂乱文件\n")
root_files = [f['name'] for f in all_files if not f['dir'] or f['dir'] == 'E:']
root_exts = Counter(os.path.splitext(f)[1].lower() for f in root_files)
if root_files:
    o(f"根目录共 **{len(root_files):,}** 个文件\n")
    o("| 扩展名 | 数量 |")
    o("|--------|------|")
    for ext, count in root_exts.most_common(10):
        o(f"| {ext or '(无扩展名)'} | {count} |")
    o("\n文件示例:")
    for f in sorted(root_files)[:20]:
        o(f"- {f}")
else:
    o("无根目录文件\n")

# ─── 6. E:\Backup ───
o("\n## 6. E:\\Backup 内容\n")
backup_files = [f for f in all_files if f['dir'].startswith('Backup') or f['dir'] == 'Backup']
if backup_files:
    o(f"Backup 目录共 **{len(backup_files):,}** 个文件\n")
    bak_exts = Counter(f['ext'] for f in backup_files)
    o("| 扩展名 | 数量 |")
    o("|--------|------|")
    for ext, count in bak_exts.most_common(10):
        o(f"| {ext or '(无)'} | {count} |")
    o("\n子目录:")
    bak_subdirs = sorted(set(f['dir'].replace('Backup/', '') for f in backup_files if '/' in f['dir']))
    for d in bak_subdirs[:20]:
        o(f"- {d}")
else:
    o("Backup 目录未在列表中找到（可能为空）\n")

# ─── 7. node_modules estimate ───
o("\n## 7. node_modules 分布\n")
nm_files = [f for f in all_files if 'node_modules' in f['path']]
if nm_files:
    o(f"node_modules 总文件数: **{len(nm_files):,}**\n")
    # Top-level node_modules (project-level)
    nm_dirs = set()
    for f in nm_files:
        parts = f['path'].split('node_modules')
        if len(parts) > 1:
            prefix = parts[0].rstrip('/')
            nm_dirs.add(prefix)
    o(f"含 node_modules 的项目/目录数: {len(nm_dirs)}\n")
    for d in sorted(nm_dirs)[:20]:
        cnt = sum(1 for f in nm_files if f['path'].startswith(d))
        o(f"- {d}: {cnt} files")
else:
    o("未发现 node_modules\n")

# ─── Summary ───
o("\n## 清理优先级建议\n")
o("| 优先级 | 项目 | 文件数 | 风险 | 建议操作 |")
o("|--------|------|--------|------|---------|")
o("| P0 | __pycache__ / .pyc | ~31K | 安全 | 全局删除，Python 自动重建 |")
o("| P0 | E:\\ 根目录杂文件 | ~40 | 安全 | 分类归入对应文件夹 |")
o("| P1 | AI Work 重复图片 | ~1K+ | 低风险 | 保留一份，删除同名副本 |")
o("| P1 | node_modules | ~60K+ | 低风险 | 项目用 `bun install` 重建 |")
o("| P2 | WeChat 附件 | ~15K | 中风险 | 备份后清理旧聊天存档 |")
o("| P2 | Backup 内容 | ~1.5K | 中风险 | 逐一确认后再删 |")
o("| P3 | 重复安装包 | 待确认 | 低风险 | 保留最新版 |")

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"DONE: {out_path}")
