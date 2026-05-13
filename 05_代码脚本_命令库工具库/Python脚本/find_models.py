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