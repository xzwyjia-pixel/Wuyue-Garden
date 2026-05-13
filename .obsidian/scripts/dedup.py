#!/usr/bin/env python3
"""Find duplicate md/txt files by content hash. Lists dedup candidates.
Run: python dedup.py
Use --delete to actually remove duplicates (keeps first in each group).
"""
import os, hashlib, sys
from collections import defaultdict

VAULT = "E:/Obsidian"
EXCLUDE = {".obsidian", ".git", ".makemd", ".smart-env"}
EXCLUDE_DIRS = {os.path.join(VAULT, "07_素材资源_截图附件模板")}

def file_hash(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read(1024*1024)).hexdigest()  # first 1MB
    except:
        return None

def main():
    dry = '--delete' not in sys.argv
    if dry: print("=== DRY RUN ===")

    by_hash = defaultdict(list)
    total = 0

    for root, dirs, fnames in os.walk(VAULT):
        rel = os.path.relpath(root, VAULT)
        if any(p in EXCLUDE for p in rel.split(os.sep)): continue
        if any(root.startswith(d) for d in EXCLUDE_DIRS): continue

        for fname in fnames:
            if not (fname.endswith('.md') or fname.endswith('.txt')): continue
            total += 1
            fpath = os.path.join(root, fname)
            h = file_hash(fpath)
            if h:
                by_hash[h].append((fpath, fname))

    print(f"Scanned: {total} files")
    print(f"Unique: {len(by_hash)} content groups")

    dupes = {h: flist for h, flist in by_hash.items() if len(flist) > 1}
    total_deleted = 0
    total_saved = 0

    for h, flist in sorted(dupes.items(), key=lambda x: -len(x[1])):
        print(f"\n--- {len(flist)} files, hash {h[:12]} ---")
        for fpath, fname in flist:
            sz = os.path.getsize(fpath)
            keep = "(KEEP)" if fpath == flist[0][0] else "(DEL)"
            print(f"  {keep} {sz:>8}B  {os.path.relpath(fpath, VAULT)}")
            if fpath != flist[0][0]:
                total_saved += sz
                if not dry:
                    os.remove(fpath)

    if dry:
        print(f"\nWould delete: {sum(len(v)-1 for v in dupes.values())} files")
        print(f"Would free: ~{total_saved:,} bytes ({total_saved/1024/1024:.1f} MB)")
    else:
        print(f"\nDeleted: {sum(len(v)-1 for v in dupes.values())} files")
        print(f"Freed: ~{total_saved:,} bytes ({total_saved/1024/1024:.1f} MB)")

if __name__ == '__main__':
    main()
