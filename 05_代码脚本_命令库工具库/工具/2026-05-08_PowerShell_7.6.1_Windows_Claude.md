---
title: PowerShell 7.6.1
PS C:\Windows\System32> Claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> 既然你已经准备好了，那我们就直接进入实战阶段。

  为了触发 Claude 的最高效开发模式（Superpowers），建议你按照下面的顺序，一个一个模块地要求它输出。

  第一步：开启核心——注入引擎 (engine.py)
  这是软件的“手”，负责物理修改 Windows 的设定。

  向 Claude 发送这个 Prompt：

  现在开始开发“语义文件夹图标助手”的第一部分：核心注入引擎。请创建一个 engine.py 模块，包含以下功能：

  权限处理：通过 ctypes 检查并申请管理员权限。

  核心函数 set_folder_customization(folder_path, icon_path, tip_text)：

  设置文件夹为“只读”属性（FILE_ATTRIBUTE_READONLY），这是 desktop.ini 生效的前提。

  在目标文件夹下生成隐藏、系统的 desktop.ini 文件，编码需符合 Windows 要求（UTF-16 LE）。

  写入 [.ShellClassInfo] 配置，指定 IconResource 和 InfoTip。

  刷新机制：调用 SHChangeNotify 确保图标修改后立即生效，无需重启资源管理器。

  复原功能：提供一个重置文件夹回默认状态的函数。
  ⎿  Retrying in 4s · attempt 6/10

✽ Quantumizing… (29s)

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> Claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> 既然你已经准备好了，那我们就直接进入实战阶段。

  为了触发 Claude 的最高效开发模式（Superpowers），建议你按照下面的顺序，一个一个模块地要求它输出。

  第一步：开启核心——注入引擎 (engine.py)
  这是软件的“手”，负责物理修改 Windows 的设定。

  向 Claude 发送这个 Prompt：

  现在开始开发“语义文件夹图标助手”的第一部分：核心注入引擎。请创建一个 engine.py 模块，包含以下功能：

  权限处理：通过 ctypes 检查并申请管理员权限。

  核心函数 set_folder_customization(folder_path, icon_path, tip_text)：

  设置文件夹为“只读”属性（FILE_ATTRIBUTE_READONLY），这是 desktop.ini 生效的前提。

  在目标文件夹下生成隐藏、系统的 desktop.ini 文件，编码需符合 Windows 要求（UTF-16 LE）。

  写入 [.ShellClassInfo] 配置，指定 IconResource 和 InfoTip。

  刷新机制：调用 SHChangeNotify 确保图标修改后立即生效，无需重启资源管理器。

  复原功能：提供一个重置文件夹回默认状态的函数。
  ⎿  Retrying in 4s · attempt 6/10

✽ Quantumizing… (29s)

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt

看来你已经直接进入了 Claude Code 的终端环境！这种方式开发效率最高，因为它可以直接在你的本地文件系统中创建文件。
检测到你目前处于 C:\Windows\System32，这通常是管理员权限下的默认路径，但我强烈建议你先进入你的项目目录（比如 D:\Projects\SmartIcon），避免在系统目录下操作。
请直接在你的 Claude Code 终端中输入以下指令。它会自动识别你的意图并利用 Sonnet 4.6 (High Effort) 的推理能力来编写这段精密的底层代码。

向 Claude Code 发送以下指令：
Initialize a new project called "SmartIcon". Create 'engine.py' with the following professional implementation:

1. Use 'ctypes' to check for admin privileges; if not present, implement a self-elevating logic.
2. Define 'set_folder_customization(folder_path, icon_path, tip_text)':
   - Use 'win32api' or 'ctypes' to set the folder attribute to READONLY (0x01).
   - Generate a hidden, system-level 'desktop.ini' in UTF-16 LE with BOM.
   - Configure '[.ShellClassInfo]' with 'IconResource' and 'InfoTip'.
3. Use 'SHChangeNotify' (0x08000000) to force a shell refresh.
4. Add a 'reset_folder(folder_path)' function to clean up 'desktop.ini' and restore normal attributes.
5. Add a robust test case at the bottom using a temporary test folder.

Ensure error handling for cases where the folder is in use or the icon path is invalid.


💡 为什么在 Claude Code 中这么做更强？

全自动执行：当你发送上述指令后，Claude Code 会自动决定需要安装哪些库（如 pywin32），并尝试运行测试代码。
高精度：Sonnet 4.6 (High Effort) 会特别注意 Windows 的细节，例如 desktop.ini 必须是 UTF-16 LE 编码，否则中文字符（InfoTip）会乱码，图标也可能不显示。
自动提权：它会帮你写好 ShellExecuteEx 逻辑，这样当你运行脚本时，它能自动弹出 UAC 窗口申请管理员权限。

执行完这一步后，请告诉我它是否成功生成了 engine.py 并且测试文件夹的图标是否发生了变化。 如果它遇到了 Access Denied 或环境问题，请直接把它的终端输出贴给我，我来帮你微调指令。

---
*从 Gemini 导出，2026-05*
