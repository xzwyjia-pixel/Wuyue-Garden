---
title: PowerShell 7.6.1
PS C:\Windows\System32> python --version
Python 3.10.6
PS C:\Windows\System32> import os
>> import hashlib
>> from pathlib import Path
>> from collections import defaultdict
>>
>> # --- 配置区：请根据你的实际盘符修改 ---
>> SCAN_DIRECTORIES = [
>>     r"E:\MyCodeProjects",
>>     r"D:\AI_Models",
>>     r"C:\Users\Administrator\.cache\lm-studio\models" # 举例：常见模型路径
>> ]
>>
>> # 关注的文件后缀
>> MODEL_EXTENSIONS = {'.safetensors', '.gguf', '.bin', '.pth', '.ckpt', '.json'}
>>
>> def get_file_hash(file_path):
>>     """计算文件哈希，由于是大模型，仅校验头部和尾部 10MB 以兼顾速度与准确性"""
>>     hash_md5 = hashlib.md5()
>>     file_size = os.path.getsize(file_path)
>>     read_size = 10 * 1024 * 1024  # 10MB
>>
>>     try:
>>         with open(file_path, "rb") as f:
>>             if file_size <= read_size * 2:
>>                 hash_md5.update(f.read())
>>             else:
>>                 # 读取开头
>>                 hash_md5.update(f.read(read_size))
>>                 # 跳到末尾读取
>>                 f.seek(-read_size, 2)
>>                 hash_md5.update(f.read(read_size))
>>         return hash_md5.hexdigest()
>>     except Exception as e:
>>         return None
>>
>> def main():
>>     print("\n--- 🔍 PowerShell 本地大模型扫描工具 ---")
>>     file_map = defaultdict(list)
>>
>>     # 1. 快速扫描文件大小
>>     for scan_path in SCAN_DIRECTORIES:
>>         if not os.path.exists(scan_path):
>>             print(f"⚠️ 路径不存在，跳过: {scan_path}")
>>             continue
>>
>>         print(f"正在扫描: {scan_path}")
>>         for path in Path(scan_path).rglob('*'):
>>             if path.is_file() and path.suffix.lower() in MODEL_EXTENSIONS:
>>                 file_map[path.stat().st_size].append(path)
>>
>>     # 2. 对大小相同的文件进行哈希比对
>>     duplicates = []
>>     print("⚖️ 正在深度比对重复内容...")
>>
>>     for size, paths in file_map.items():
>>         if len(paths) > 1:
>>             hashes = defaultdict(list)
>>             for p in paths:
>>                 h = get_file_hash(p)
>>                 if h: hashes[h].append(p)
>>
>>             for h, p_list in hashes.items():
>>                 if len(p_list) > 1:
>>                     duplicates.append(p_list)
>>
>>     # 3. 输出结果
>>     if not duplicates:
>>         print("✨ 未发现重复的大模型文件。")
>>     else:
>>         print(f"\n🚩 发现 {len(duplicates)} 组重复文件：")
>>         for i, group in enumerate(duplicates):
>>             print(f"\n[组 {i+1}] ------------------")
>>             for p in group:
>>                 size_gb = os.path.getsize(p) / (1024**3)
>>                 print(f"  >> {size_gb:.2f} GB | {p}")
>>
>> if __name__ == "__main__":
>>     main()
ParserError:
Line |
   3 |  from pathlib import Path
     |  ~~~~
     | The 'from' keyword is not supported in this version of the language.
PS C:\Windows\System32>
source: gemini
date: 2026-05-09
category: 编程开发
tags: [gemini, 编程开发]
---

## PowerShell 7.6.1
PS C:\Windows\System32> python --version
Python 3.10.6
PS C:\Windows\System32> import os
>> import hashlib
>> from pathlib import Path
>> from collections import defaultdict
>>
>> # --- 配置区：请根据你的实际盘符修改 ---
>> SCAN_DIRECTORIES = [
>>     r"E:\MyCodeProjects",
>>     r"D:\AI_Models",
>>     r"C:\Users\Administrator\.cache\lm-studio\models" # 举例：常见模型路径
>> ]
>>
>> # 关注的文件后缀
>> MODEL_EXTENSIONS = {'.safetensors', '.gguf', '.bin', '.pth', '.ckpt', '.json'}
>>
>> def get_file_hash(file_path):
>>     """计算文件哈希，由于是大模型，仅校验头部和尾部 10MB 以兼顾速度与准确性"""
>>     hash_md5 = hashlib.md5()
>>     file_size = os.path.getsize(file_path)
>>     read_size = 10 * 1024 * 1024  # 10MB
>>
>>     try:
>>         with open(file_path, "rb") as f:
>>             if file_size <= read_size * 2:
>>                 hash_md5.update(f.read())
>>             else:
>>                 # 读取开头
>>                 hash_md5.update(f.read(read_size))
>>                 # 跳到末尾读取
>>                 f.seek(-read_size, 2)
>>                 hash_md5.update(f.read(read_size))
>>         return hash_md5.hexdigest()
>>     except Exception as e:
>>         return None
>>
>> def main():
>>     print("\n--- 🔍 PowerShell 本地大模型扫描工具 ---")
>>     file_map = defaultdict(list)
>>
>>     # 1. 快速扫描文件大小
>>     for scan_path in SCAN_DIRECTORIES:
>>         if not os.path.exists(scan_path):
>>             print(f"⚠️ 路径不存在，跳过: {scan_path}")
>>             continue
>>
>>         print(f"正在扫描: {scan_path}")
>>         for path in Path(scan_path).rglob('*'):
>>             if path.is_file() and path.suffix.lower() in MODEL_EXTENSIONS:
>>                 file_map[path.stat().st_size].append(path)
>>
>>     # 2. 对大小相同的文件进行哈希比对
>>     duplicates = []
>>     print("⚖️ 正在深度比对重复内容...")
>>
>>     for size, paths in file_map.items():
>>         if len(paths) > 1:
>>             hashes = defaultdict(list)
>>             for p in paths:
>>                 h = get_file_hash(p)
>>                 if h: hashes[h].append(p)
>>
>>             for h, p_list in hashes.items():
>>                 if len(p_list) > 1:
>>                     duplicates.append(p_list)
>>
>>     # 3. 输出结果
>>     if not duplicates:
>>         print("✨ 未发现重复的大模型文件。")
>>     else:
>>         print(f"\n🚩 发现 {len(duplicates)} 组重复文件：")
>>         for i, group in enumerate(duplicates):
>>             print(f"\n[组 {i+1}] ------------------")
>>             for p in group:
>>                 size_gb = os.path.getsize(p) / (1024**3)
>>                 print(f"  >> {size_gb:.2f} GB | {p}")
>>
>> if __name__ == "__main__":
>>     main()
ParserError:
Line |
   3 |  from pathlib import Path
     |  ~~~~
     | The 'from' keyword is not supported in this version of the language.
PS C:\Windows\System32>

看起来你是在 PowerShell 的命令行界面里直接粘贴了 Python 代码。
这是一个常见的误区：PowerShell 是一个外壳程序（Shell），它只能理解 PowerShell 命令；而 from...import... 是 Python 的语法。当你直接粘贴进去时，PowerShell 会尝试解析这些代码，结果自然会报错 ParserError。
要成功执行，请按照以下三个步骤操作：

第一步：将代码保存为文件
你不能直接把整段代码塞进 PowerShell。

在桌面或你的项目目录（如 E:\MyCodeProjects）下，新建一个记事本文件。
将代码全部粘贴进去。
保存文件，重命名为 find_models.py (确保后缀是 .py 而不是 .txt)。

第二步：在 PowerShell 中定位到该目录
打开 PowerShell，使用 cd 命令进入你保存文件的目录：
# 假设你保存在 E 盘的这个目录下
cd E:\MyCodeProjects

第三步：调用 Python 解释器运行
输入以下命令并回车：
python find_models.py


💡 为什么你刚才的操作报错了？

PowerShell：就像一个调度员，负责管理文件、启动程序（比如执行 git 或 python）。
Python：就像一个翻译官，只有当你先喊出 python 这个名字后，它才会开始听懂你后面给它的 .py 文件里的内容。

快捷提示：
如果你想直接在 PowerShell 里快速测试几行 Python，你需要先输入 python 并回车，看到提示符变成 >>> 后，再粘贴 Python 代码。但对于这么长的程序，保存为 .py 文件是最稳妥且标准的方法。
你可以先试着保存文件并运行，如果有路径权限问题，我再帮你调整。

---
*从 Gemini 导出，2026-05*
