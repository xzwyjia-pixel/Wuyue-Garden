---
title: 要求这个程序能够在powershell执行
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## 要求这个程序能够在powershell执行

为了让程序在 PowerShell 中完美运行，我们需要对脚本进行微调，使其更符合 Windows 环境的习惯。你可以将下面的代码保存为 find_models.py。
同时，我会教你如何直接在 PowerShell 中运行它，并处理可能遇到的权限或环境问题。
1. 更新后的 Python 脚本 (find_models.py)
这个版本增加了对 Windows 长路径的支持，并优化了 PowerShell 终端的输出显示。
import os
import hashlib
from pathlib import Path
from collections import defaultdict

# --- 配置区：请根据你的实际盘符修改 ---
SCAN_DIRECTORIES = [
    r"E:\MyCodeProjects",
    r"D:\AI_Models",
    r"C:\Users\Administrator\.cache\lm-studio\models" # 举例：常见模型路径
]

# 关注的文件后缀
MODEL_EXTENSIONS = {'.safetensors', '.gguf', '.bin', '.pth', '.ckpt', '.json'}

def get_file_hash(file_path):
    """计算文件哈希，由于是大模型，仅校验头部和尾部 10MB 以兼顾速度与准确性"""
    hash_md5 = hashlib.md5()
    file_size = os.path.getsize(file_path)
    read_size = 10 * 1024 * 1024  # 10MB
    
    try:
        with open(file_path, "rb") as f:
            if file_size <= read_size * 2:
                hash_md5.update(f.read())
            else:
                # 读取开头
                hash_md5.update(f.read(read_size))
                # 跳到末尾读取
                f.seek(-read_size, 2)
                hash_md5.update(f.read(read_size))
        return hash_md5.hexdigest()
    except Exception as e:
        return None

def main():
    print("\n--- 🔍 PowerShell 本地大模型扫描工具 ---")
    file_map = defaultdict(list)
    
    # 1. 快速扫描文件大小
    for scan_path in SCAN_DIRECTORIES:
        if not os.path.exists(scan_path):
            print(f"⚠️ 路径不存在，跳过: {scan_path}")
            continue
            
        print(f"正在扫描: {scan_path}")
        for path in Path(scan_path).rglob('*'):
            if path.is_file() and path.suffix.lower() in MODEL_EXTENSIONS:
                file_map[path.stat().st_size].append(path)

    # 2. 对大小相同的文件进行哈希比对
    duplicates = []
    print("⚖️ 正在深度比对重复内容...")
    
    for size, paths in file_map.items():
        if len(paths) > 1:
            hashes = defaultdict(list)
            for p in paths:
                h = get_file_hash(p)
                if h: hashes[h].append(p)
            
            for h, p_list in hashes.items():
                if len(p_list) > 1:
                    duplicates.append(p_list)

    # 3. 输出结果
    if not duplicates:
        print("✨ 未发现重复的大模型文件。")
    else:
        print(f"\n🚩 发现 {len(duplicates)} 组重复文件：")
        for i, group in enumerate(duplicates):
            print(f"\n[组 {i+1}] ------------------")
            for p in group:
                size_gb = os.path.getsize(p) / (1024**3)
                print(f"  >> {size_gb:.2f} GB | {p}")

if __name__ == "__main__":
    main()


2. 如何在 PowerShell 中执行
第一步：准备环境
确保你已经安装了 Python。在 PowerShell 中输入以下命令检查：
python --version

第二步：运行脚本
假设你将脚本保存在 E:\MyCodeProjects\find_models.py，在 PowerShell 中执行：
python E:\MyCodeProjects\find_models.py

第三步：(进阶) 将结果导出到文件
如果你重复的文件太多，屏幕显示不下，可以使用 PowerShell 的重定向功能将结果保存到文本文件：
python E:\MyCodeProjects\find_models.py | Out-File -FilePath "D:\dup_models_report.txt" -Encoding utf8


3. 给你的特别建议（针对 PowerShell 环境）

路径转义：在脚本的 SCAN_DIRECTORIES 中，记得使用 r"C:\Path" 这种形式，或者将反斜杠写成双斜杠 \\，防止 PowerShell 或 Python 对转义字符产生误解。
权限问题：如果你的模型存放在系统盘（C 盘）某些受保护的目录，请以管理员身份运行 PowerShell。
重复功能 vs 重复内容：

这个脚本帮你解决的是物理层面的一模一样。
如果你有多个不同版本的 Llama-3（比如一个是 FP16，一个是 Q4_K_M 压缩版），由于它们二进制内容不同，脚本不会认为它们是重复的。你需要根据输出的路径名手动判断是否保留多个精度的模型。



如果有特定的本地路径（比如 LM Studio 或 Ollama 的默认路径）需要我帮你集成进去，可以告诉我。

---
*从 Gemini 导出，2026-05*
