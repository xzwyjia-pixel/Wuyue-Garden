---
title: PS C:\Users\think> python
source: gemini
date: 2026-05-10
category: 技术开发
subcategory: Python
old_category: 编程开发
tags: [gemini, 技术开发, Python]
---

## PS C:\Users\think> python

## PS C:\Users\think> python
Python 3.10.6 (tags/v3.10.6:9c7b4bd, Aug  1 2022, 21:53:49) [MSC v.1932 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> import shutil
>>> import stat
>>> from pathlib import Path
>>>
>>> # 1. 定义安全白名单（绝对不能删的文件夹）
>>> WHITE_LIST = [
...     'python', 'pip', 'claude', 'cursor', 'microsoft', 'apple', 'nvidia',
...     'torch', 'opencv', 'ghc', 'npm', 'roaming', 'google', 'anaconda', 'miniconda'
... ]
>>>
>>> # 2. 定义已知流氓软件黑名单关键词
>>> BLACK_LIST_KEYWORDS = ['360', 'coolfile', 'viewer', 'helper', 'assistant', 'zhushou']
>>>
>>> def force_remove(path):
...     """处理只读文件导致的权限问题"""
...     def handle_error(func, path, exc_info):
...         os.chmod(path, stat.S_IWRITE)
...         func(path)
...     if os.path.exists(path):
...         shutil.rmtree(path, onerror=handle_error)
...
>>> def scan_and_cleanup():
...     appdata_paths = [os.getenv('APPDATA'), os.getenv('LOCALAPPDATA')]
...     program_files = [os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')]
...
...     to_delete = []
...     print("🔍 正在扫描 AppData 残留...")
...
>>>     for base_path in appdata_paths:
  File "<stdin>", line 1
    for base_path in appdata_paths:
IndentationError: unexpected indent
>>>         if not base_path: continue
  File "<stdin>", line 1
    if not base_path: continue
IndentationError: unexpected indent
>>>         for folder in os.listdir(base_path):
  File "<stdin>", line 1
    for folder in os.listdir(base_path):
IndentationError: unexpected indent
>>>             folder_lower = folder.lower()
  File "<stdin>", line 1
    folder_lower = folder.lower()
IndentationError: unexpected indent
>>>             folder_path = os.path.join(base_path, folder)
  File "<stdin>", line 1
    folder_path = os.path.join(base_path, folder)
IndentationError: unexpected indent
>>>
>>>             if not os.path.isdir(folder_path): continue
  File "<stdin>", line 1
    if not os.path.isdir(folder_path): continue
IndentationError: unexpected indent
>>>             if any(safe in folder_lower for safe in WHITE_LIST): continue
  File "<stdin>", line 1
    if any(safe in folder_lower for safe in WHITE_LIST): continue
IndentationError: unexpected indent
>>>
>>>             # 逻辑 A：黑名单直接判定
>>>             if any(key in folder_lower for key in BLACK_LIST_KEYWORDS):
  File "<stdin>", line 1
    if any(key in folder_lower for key in BLACK_LIST_KEYWORDS):
IndentationError: unexpected indent
>>>                 to_delete.append(folder_path)
  File "<stdin>", line 1
    to_delete.append(folder_path)
IndentationError: unexpected indent
>>>                 continue
  File "<stdin>", line 1
    continue
IndentationError: unexpected indent
>>>
>>>             # 逻辑 B：检查 C 盘主程序是否存在
>>>             # 如果在 Program Files 中找不到同名目录，判定为残留
>>>             exists_in_pc = any(os.path.exists(os.path.join(pf, folder)) for pf in program_files)
  File "<stdin>", line 1
    exists_in_pc = any(os.path.exists(os.path.join(pf, folder)) for pf in program_files)
IndentationError: unexpected indent
>>>
>>>             if not exists_in_pc:
  File "<stdin>", line 1
    if not exists_in_pc:
IndentationError: unexpected indent
>>>                 # 排除掉 AppData 内部运行的合法程序
>>>                 # 这里我们采用保守策略：只有在黑名单内，或者你明确想删的才列入
>>>                 pass
  File "<stdin>", line 1
    pass
IndentationError: unexpected indent
>>>
>>>     if not to_delete:
  File "<stdin>", line 1
    if not to_delete:
IndentationError: unexpected indent
>>>         print("✅ 未发现明显流氓软件残留。")
  File "<stdin>", line 1
    print("✅ 未发现明显流氓软件残留。")
IndentationError: unexpected indent
>>>         return
  File "<stdin>", line 1
    return
IndentationError: unexpected indent
>>>
>>>     print("\n🚩 发现以下疑似残留文件夹：")
  File "<stdin>", line 1
    print("\n🚩 发现以下疑似残留文件夹：")
IndentationError: unexpected indent
>>>     for p in to_delete:
  File "<stdin>", line 1
    for p in to_delete:
IndentationError: unexpected indent
>>>         print(f"[待删] {p}")
  File "<stdin>", line 1
    print(f"[待删] {p}")
IndentationError: unexpected indent
>>>
>>>     confirm = input("\n⚠️ 是否确认强制删除以上所有文件夹？(Y/N): ")
  File "<stdin>", line 1
    confirm = input("\n⚠️ 是否确认强制删除以上所有文件夹？(Y/N): ")
IndentationError: unexpected indent
>>>     if confirm.lower() == 'y':
  File "<stdin>", line 1
    if confirm.lower() == 'y':
IndentationError: unexpected indent
>>>         for p in to_delete:
  File "<stdin>", line 1
    for p in to_delete:
IndentationError: unexpected indent
>>>             try:
  File "<stdin>", line 1
    try:
IndentationError: unexpected indent
>>>                 force_remove(p)
  File "<stdin>", line 1
    force_remove(p)
IndentationError: unexpected indent
>>>                 print(f"🗑️ 已清理: {p}")
  File "<stdin>", line 1
    print(f"🗑️ 已清理: {p}")
IndentationError: unexpected indent
>>>             except Exception as e:
  File "<stdin>", line 1
    except Exception as e:
IndentationError: unexpected indent
>>>                 print(f"❌ 清理失败 {p}: {e}")
  File "<stdin>", line 1
    print(f"❌ 清理失败 {p}: {e}")
IndentationError: unexpected indent
>>>     else:
  File "<stdin>", line 1
    else:
IndentationError: unexpected indent
>>>         print("操作已取消。")
  File "<stdin>", line 1
    print("操作已取消。")
IndentationError: unexpected indent
>>>
>>> if __name__ == "__main__":
...     scan_and_cleanup()
... exit()
  File "<stdin>", line 3
    exit()
    ^^^^
SyntaxError: invalid syntax
>>>

看来你在直接粘贴代码到 Python 交互式命令行（就是带 >>> 的那个界面）时遇到了缩进错误（IndentationError）。
这是因为 Python 交互式环境对多行代码的粘贴非常敏感，尤其是当函数体内部包含循环和判断时，直接粘贴很容易导致格式错乱。
🛠️ 最稳妥的解决办法：直接运行脚本文件
不要一行行粘贴到交互式窗口。请按照以下步骤操作，这能一次性成功：

第一步：创建脚本文件
在你的 PowerShell 窗口中（或者直接在 E:\MyCodeProjects 目录下），运行这一行命令来创建一个干净的 .py 文件：
# 先退出当前的 Python 环境
exit()

# 创建脚本并写入代码
New-Item -Path "cleanup_tool.py" -ItemType "File"

第二步：将代码写入文件
用记事本打开这个新创建的 cleanup_tool.py，把下面的代码完整粘贴进去并保存：
import os
import shutil
import stat
from pathlib import Path

# 1. 安全白名单
WHITE_LIST = [
    'python', 'pip', 'claude', 'cursor', 'microsoft', 'apple', 'nvidia', 
    'torch', 'opencv', 'ghc', 'npm', 'roaming', 'google', 'anaconda', 'miniconda'
]

# 2. 流氓软件关键词
BLACK_LIST_KEYWORDS = ['360', 'coolfile', 'viewer', 'helper', 'assistant', 'zhushou']

def force_remove(path):
    def handle_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    if os.path.exists(path):
        shutil.rmtree(path, onerror=handle_error)

def scan_and_cleanup():
    appdata_paths = [os.getenv('APPDATA'), os.getenv('LOCALAPPDATA')]
    program_files = [os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')]
    
    to_delete = []
    print("🔍 正在扫描 AppData 残留...")

    for base_path in appdata_paths:
        if not base_path or not os.path.exists(base_path): continue
        for folder in os.listdir(base_path):
            folder_lower = folder.lower()
            folder_path = os.path.join(base_path, folder)
            
            if not os.path.isdir(folder_path): continue
            if any(safe in folder_lower for safe in WHITE_LIST): continue
            
            if any(key in folder_lower for key in BLACK_LIST_KEYWORDS):
                to_delete.append(folder_path)
                continue

    if not to_delete:
        print("✅ 未发现明显流氓软件残留。")
        return

    print("\n🚩 发现以下疑似残留文件夹：")
    for p in to_delete:
        print(f"[待删] {p}")

    confirm = input("\n⚠️ 是否确认强制删除以上所有文件夹？(Y/N): ")
    if confirm.lower() == 'y':
        for p in to_delete:
            try:
                force_remove(p)
                print(f"🗑️ 已清理: {p}")
            except Exception as e:
                print(f"❌ 清理失败 {p}: {e}")
    else:
        print("操作已取消。")

if __name__ == "__main__":
    scan_and_cleanup()

第三步：在控制台直接运行
保存文件后，在 PowerShell 中执行：
python cleanup_tool.py


💡 为什么会失败？
Python 交互式窗口（REPL）在处理 for 或 if 时，期望你输入完一部分就立即执行。当你粘贴一大段带缩进的代码时，它分不清哪里是函数的开始，哪里是循环的结束。
按照上面的“脚本运行法”，就不会再有缩进问题了！

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / Python · 2026-05-10*
