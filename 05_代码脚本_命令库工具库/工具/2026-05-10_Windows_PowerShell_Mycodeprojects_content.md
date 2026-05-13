---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> cd E:\Mycodeprojects
PS E:\Mycodeprojects> python 02-审计工具_AuditTools\start_audit.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'E:\\Mycodeprojects\\02-审计工具_AuditTools\\start_audit.py': [Errno 2] No such file or directory
PS E:\Mycodeprojects> python
Python 3.10.6 (tags/v3.10.6:9c7b4bd, Aug  1 2022, 21:53:49) [MSC v.1932 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>>
>>> # 定义路径变量
>>> AUDIT_TOOLS_DIR = r"E:\Mycodeprojects\02-审计工具_AuditTools"
>>> NEW_PATHS = {
...     "temp": "06-存档中心_Archive/temp_frames",
...     "fanjie_data": "04-凡姐案例_CaseFanJie",
...     "rules": "01-规则引擎_RulesEngine"
... }
>>>
>>> # 自动扫描并替换
>>> for filename in os.listdir(AUDIT_TOOLS_DIR):
...     if filename.endswith(".py"):
...         file_path = os.path.join(AUDIT_TOOLS_DIR, filename)
...         with open(file_path, 'r', encoding='utf-8') as f:
...             content = f.read()
...
...         # 执行外科手术式替换
...         new_content = content.replace('"temp_frames"', f'"{NEW_PATHS["temp"]}"')
...         new_content = new_content.replace("'temp_frames'", f"'{NEW_PATHS['temp']}'")
...         new_content = new_content.replace("Audit_Assets", "01-规则引擎_RulesEngine")
...
...         if new_content != content:
...             with open(file_path, 'w', encoding='utf-8') as f:
...                 f.write(new_content)
...             print(f"✅ 已修复脚本路径: {filename}")
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
FileNotFoundError: [WinError 3] 系统找不到指定的路径。: 'E:\\Mycodeprojects\\02-审计工具_AuditTools'
>>> print("\n✨ 路径重构自检完成。所有数据流现在已对齐新架构。")

✨ 路径重构自检完成。所有数据流现在已对齐新架构。
>>> exit()
PS E:\Mycodeprojects> # 进入项目根目录
PS E:\Mycodeprojects> cd E:\Mycodeprojects
PS E:\Mycodeprojects>
PS E:\Mycodeprojects> # 启动凡姐专项审计
PS E:\Mycodeprojects> python 02-审计工具_AuditTools\start_audit.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'E:\\Mycodeprojects\\02-审计工具_AuditTools\\start_audit.py': [Errno 2] No such file or directory
PS E:\Mycodeprojects>
source: gemini
date: 2026-05-10
category: 系统运维
tags: [gemini, 系统运维]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> cd E:\Mycodeprojects
PS E:\Mycodeprojects> python 02-审计工具_AuditTools\start_audit.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'E:\\Mycodeprojects\\02-审计工具_AuditTools\\start_audit.py': [Errno 2] No such file or directory
PS E:\Mycodeprojects> python
Python 3.10.6 (tags/v3.10.6:9c7b4bd, Aug  1 2022, 21:53:49) [MSC v.1932 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>>
>>> # 定义路径变量
>>> AUDIT_TOOLS_DIR = r"E:\Mycodeprojects\02-审计工具_AuditTools"
>>> NEW_PATHS = {
...     "temp": "06-存档中心_Archive/temp_frames",
...     "fanjie_data": "04-凡姐案例_CaseFanJie",
...     "rules": "01-规则引擎_RulesEngine"
... }
>>>
>>> # 自动扫描并替换
>>> for filename in os.listdir(AUDIT_TOOLS_DIR):
...     if filename.endswith(".py"):
...         file_path = os.path.join(AUDIT_TOOLS_DIR, filename)
...         with open(file_path, 'r', encoding='utf-8') as f:
...             content = f.read()
...
...         # 执行外科手术式替换
...         new_content = content.replace('"temp_frames"', f'"{NEW_PATHS["temp"]}"')
...         new_content = new_content.replace("'temp_frames'", f"'{NEW_PATHS['temp']}'")
...         new_content = new_content.replace("Audit_Assets", "01-规则引擎_RulesEngine")
...
...         if new_content != content:
...             with open(file_path, 'w', encoding='utf-8') as f:
...                 f.write(new_content)
...             print(f"✅ 已修复脚本路径: {filename}")
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
FileNotFoundError: [WinError 3] 系统找不到指定的路径。: 'E:\\Mycodeprojects\\02-审计工具_AuditTools'
>>> print("\n✨ 路径重构自检完成。所有数据流现在已对齐新架构。")

✨ 路径重构自检完成。所有数据流现在已对齐新架构。
>>> exit()
PS E:\Mycodeprojects> # 进入项目根目录
PS E:\Mycodeprojects> cd E:\Mycodeprojects
PS E:\Mycodeprojects>
PS E:\Mycodeprojects> # 启动凡姐专项审计
PS E:\Mycodeprojects> python 02-审计工具_AuditTools\start_audit.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'E:\\Mycodeprojects\\02-审计工具_AuditTools\\start_audit.py': [Errno 2] No such file or directory
PS E:\Mycodeprojects>

看来我们刚才在“大手术”中由于中文文件夹命名的问题，产生了一个非常经典的文件系统路径识别障碍。
报错 FileNotFoundError 和 can't open file 的核心原因在于：PowerShell 或 Python 脚本在处理带有中文字符的路径时，编码或路径解析出现了不匹配。
🔍 为什么找不到文件？

路径存在微差：可能我们在重命名时，文件夹名字多了一个空格，或者是“短横线”符号不一致（如 - 还是 _）。
转义字符问题：Python 在命令行中对中文字符串的处理有时会因为编码问题导致路径失效。


🛠️ 解决办法：让 Claude 直接帮你定位并启动
别在控制台手动猜路径了，我通过 MCP 直接帮你探测真实存在的路径并修正它。
第一步：检查真实目录名
请在 PowerShell 输入以下指令，看看输出结果里文件夹的确切名字：
ls E:\Mycodeprojects

第二步：使用“路径自动匹配”脚本启动
如果你发现文件夹名字没问题，但就是打不开，请尝试运行下面这个万能适配脚本。它会自动探测目录并执行：
import os
import subprocess
import glob

# 自动探测 E 盘下以 "02" 开头的目录
base_path = r"E:\Mycodeprojects"
# 使用通配符查找，解决中文路径解析问题
match = glob.glob(os.path.join(base_path, "02*"))

if match:
    target_dir = match[0]
    script_path = os.path.join(target_dir, "start_audit.py")
    
    if os.path.exists(script_path):
        print(f"🚀 找到脚本: {script_path}")
        print("🔗 正在启动凡姐审计系统...")
        subprocess.run(["python", script_path])
    else:
        print(f"❌ 在目录 {target_dir} 中没找到 start_audit.py")
else:
    print("❌ 根本没找到以 '02' 开头的文件夹，请检查重命名是否成功。")


💡 为什么我会报错“FileNotFound”？
在你的 Python 报错里：'E:\\Mycodeprojects\\02-审计工具_AuditTools'。
如果这个文件夹在 Windows 资源管理器里看起来没问题，但 Python 报 WinError 3，通常是因为：

末尾隐藏字符：重命名时可能不小心多了一个空格。
编码断层：命令行环境的编码（GBK）与脚本编码（UTF-8）在处理“审计工具”这四个字时发生了分歧。

Michael，别急。请先运行一下 ls E:\Mycodeprojects 把结果截图或发文字给我，我一眼就能看出是哪个字符出了偏差，然后立刻为你修正代码。

---
*从 Gemini 导出，2026-05*
