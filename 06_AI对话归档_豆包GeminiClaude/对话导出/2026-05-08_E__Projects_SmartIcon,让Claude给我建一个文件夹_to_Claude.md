---
title: E:\Projects\SmartIcon,让Claude给我建一个文件夹
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## E:\Projects\SmartIcon,让Claude给我建一个文件夹

既然你已经身处 Claude Code 环境，且明确了路径，现在我们就利用它的本地文件操作权限来初始化环境。
请在你的 Claude Code 终端中输入以下指令。它会自动执行 mkdir，进入目录，并开始编写我们之前讨论的核心注入引擎。

向 Claude Code 发送指令：
cd E:\Projects\SmartIcon
Create the directory if it doesn't exist. 

Then, create 'engine.py' with this high-effort implementation:

1. ADMIN CHECK: Include a function to check if the script is running with admin rights.
2. ATTRIBUTE LOGIC: Use ctypes to set the folder attribute to READONLY (0x01).
3. DESKTOP.INI: Create a 'desktop.ini' file with:
   - Encoding: UTF-16 LE (with BOM).
   - Attributes: Hidden (0x02) and System (0x04).
   - Content: [.ShellClassInfo] Section with IconResource and InfoTip.
4. SHELL REFRESH: Implement SHChangeNotify to force Windows Explorer to update the icon immediately.
5. CLEANUP: Implement a function to remove customization.

After creating the file, please attempt to run a small test: 
Create a folder named 'TestFolder', set a custom icon (if you can find a .ico on system or just use shell32.dll index), and verify it works.


🚀 为什么这对接下来的流程至关重要？

路径锁定：让 Claude 明确在 E:\Projects\SmartIcon 工作，后续所有的 analyzer.py 和 monitor.py 都会自动放在正确的位置。
原子化测试：我让它在创建完代码后立即运行测试。如果 Windows 权限或编码有问题，Claude Code 会直接在终端看到报错并自我修复。
Shell32 兜底：如果在测试时你本地没有 .ico 文件，我提示它使用 C:\Windows\System32\shell32.dll,3（典型的文件夹图标），这样能立刻验证注入逻辑是否成功。

执行指令后，请留意终端是否显示了 engine.py 已创建，并观察 E:\Projects\SmartIcon\TestFolder 的图标有没有变样！

---
*从 Gemini 导出，2026-05*
