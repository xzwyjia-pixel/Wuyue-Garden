#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Organize loose files in D:/01_客户项目 into appropriate subdirectories."""

import os, shutil
from pathlib import Path

BASE = Path("D:/01_客户项目")

def move_to_dir(folder, files, target_subdir):
    """Move files into folder/target_subdir/"""
    dest = folder / target_subdir
    dest.mkdir(exist_ok=True)
    for f in files:
        src = folder / f
        if src.exists() and src.is_file():
            # Handle duplicates
            dst = dest / f
            if dst.exists():
                stem = dst.stem
                suffix = dst.suffix
                dst = dest / f"{stem}_dup{suffix}"
            shutil.move(str(src), str(dst))
            print(f"  mv {f} → {target_subdir}/")

# ───────── 01 芯陆 ─────────
f = BASE / "01 北京芯陆信息科技有限公司"
if f.exists():
    print("=== 01 芯陆 ===")
    move_to_dir(f, ["1.ai","1 (2).ai","2.ai","1.eps","1 (2).eps","2.eps"], "设计素材")
    move_to_dir(f, ["北京芯陆信息系统有限公司招商银行开户资料.rar",
                     "批量回单打印，110945802110901，共33笔.zip"], "财务文档")
    move_to_dir(f, ["大模型算力购置竞争性谈判项目.zip"], "合同协议")
    # Find the xlsx with garbled name
    for x in f.iterdir():
        if x.is_file() and x.suffix == '.xlsx' and '芯陆' not in x.stem:
            # check if it's the tax declaration file
            if '所得' in x.name or '申报' in x.name or '__' in x.name:
                move_to_dir(f, [x.name], "财务文档")

# ───────── 02 京源 ─────────
f = BASE / "02 北京京源天地科技发展有限公司"
if f.exists():
    print("=== 02 京源 ===")
    move_to_dir(f, ["200415-其他地铁公司及专家通讯录.xlsm",
                     "200730-其他地铁公司及专家通讯录.xlsm"], "工作文档")
    move_to_dir(f, ["200730_北交大MBA学生通讯录.xlsm"], "学习资料")
    move_to_dir(f, ["1_0002(2).pdf", "布丁扫描2026-03-23 14.30.47.pdf"], "工作文档")
    move_to_dir(f, ["上海天诚合同发票-88000元.jpg"], "商务合同")
    move_to_dir(f, ["京源天地.ai"], "品牌标识")

# ───────── 06 万源智信 ─────────
f = BASE / "06 北京万源智信科技有限公司"
if f.exists():
    print("=== 06 万源智信 ===")
    # Group by subdir: contracts go to 商务合同
    contract_exts = {'.pdf', '.doc', '.docx', '.rar'}
    contract_files = [x.name for x in f.iterdir() if x.is_file() and x.suffix.lower() in contract_exts]
    if not (f / "商务合同").exists():
        (f / "商务合同").mkdir()
    if contract_files:
        move_to_dir(f, contract_files, "商务合同")

# ───────── 09 石化盈科 ─────────
f = BASE / "09 石化盈科信息技术有限责任公司"
if f.exists():
    print("=== 09 石化盈科 ===")
    loose = [x.name for x in f.iterdir() if x.is_file()]
    if loose:
        move_to_dir(f, loose, "文档资料")

# ───────── 10 机房迁移 ─────────
f = BASE / "10 数据机房迁移项目"
if f.exists():
    print("=== 10 机房迁移 ===")
    (f / "方案与指南").mkdir(exist_ok=True)
    (f / "报价").mkdir(exist_ok=True)
    move_to_dir(f, ["数据中心机房迁移项目详细计划制定指南.pdf",
                     "数据中心机房迁移项目详细计划制定指南.docx",
                     "成功数据中心机房迁移案例及具体细节.pdf",
                     "在数据中心机房迁移项目中.pdf",
                     "数据中心机房迁移项目.pdf"], "方案与指南")
    move_to_dir(f, ["数据中心机房迁移项目报价指南.pdf",
                     "数据中心机房迁移项目报价指南.docx",
                     "New Microsoft Word Document (2).pdf",
                     "New Microsoft Word Document (2).docx"], "报价")

# ───────── 12 耐斯普特 ─────────
f = BASE / "12 耐斯普特（北京）电气技术有限公司"
if f.exists():
    print("=== 12 耐斯普特 ===")
    # Separate contracts from product docs and photos
    contract_keywords = ['合同', '京源', '速科', 'NPT-']
    product_keywords = ['样本', '宣传册', '业绩', '机柜']
    other_keywords = ['报关单', '微信公众号']

    contract_files = []; product_files = []; photo_files = []; other_files = []

    for x in f.iterdir():
        if not x.is_file():
            continue
        name = x.name
        lo = name.lower()
        if name.startswith('IMG_') and x.suffix.lower() in ('.jpg','.jpeg','.png'):
            photo_files.append(name)
        elif any(kw in name for kw in contract_keywords):
            contract_files.append(name)
        elif any(kw in name for kw in product_keywords):
            product_files.append(name)
        elif any(kw in name for kw in other_keywords):
            other_files.append(name)
        else:
            other_files.append(name)

    if contract_files:
        move_to_dir(f, contract_files, "合同")
    if product_files:
        move_to_dir(f, product_files, "产品资料")
    if photo_files:
        move_to_dir(f, photo_files, "现场照片")
    if other_files:
        move_to_dir(f, other_files, "其他")

# ───────── 14 其他客户 ─────────
f = BASE / "14 其他客户"
if f.exists():
    print("=== 14 其他客户 ===")
    loose = [x.name for x in f.iterdir() if x.is_file()]
    if loose:
        move_to_dir(f, loose, "杂项")

# ───────── 15 水库照片 ─────────
f = BASE / "15 水库实地拍摄照片"
if f.exists():
    print("=== 15 水库照片 ===")
    # Group by month from filename (2025_01_21_...)
    by_month = {}
    for x in f.iterdir():
        if x.is_file():
            parts = x.stem.split('_')
            month_key = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else "其他"
            by_month.setdefault(month_key, []).append(x.name)
    for month, files in sorted(by_month.items()):
        (f / month).mkdir(exist_ok=True)
        move_to_dir(f, files, month)

# ───────── 16 南京浦镇 ─────────
f = BASE / "16 南京浦镇车辆有限公司"
if f.exists():
    print("=== 16 南京浦镇 ===")
    (f / "方案介绍").mkdir(exist_ok=True)
    (f / "视频").mkdir(exist_ok=True)
    (f / "其他").mkdir(exist_ok=True)
    move_to_dir(f, ["100%有轨电车方案(PZ).pdf",
                     "2025-有轨电车简介.pptx",
                     "DRT与有轨电车产品平台对比(1).pptx",
                     "有轨电车方案介绍（PZ）.pptx",
                     "轨道交通行业院校专业与职业对应关系.pptx",
                     "绝缘栅双极型晶体管（IGBT）.pptx"], "方案介绍")
    move_to_dir(f, ["中车公司介绍.mp4", "城轨生产车间.mp4"], "视频")
    move_to_dir(f, ["薪资与发展潜力分析表.xlsx"], "其他")

# ───────── 17 华德福 ─────────
f = BASE / "17 华德福教育艺术"
if f.exists():
    print("=== 17 华德福 ===")
    # 433 JPG photos + some date-based subdirs already exist
    # Group remaining JPGs by month
    existing_dirs = {d.name for d in f.iterdir() if d.is_dir()}
    by_month = {}
    for x in f.iterdir():
        if x.is_file() and x.suffix.lower() in ('.jpg','.jpeg','.png','.heic'):
            parts = x.stem.split('_')
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                month_key = f"{parts[0]}_{parts[1]}"
            else:
                month_key = "其他照片"
            by_month.setdefault(month_key, []).append(x.name)

    for month, files in sorted(by_month.items()):
        if month not in existing_dirs:
            (f / month).mkdir(exist_ok=True)
        move_to_dir(f, files, month)

print("\nDONE")
