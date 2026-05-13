---
title: PowerShell 7.6.1
PS C:\Windows\System32> Claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> 既然你已经准备好了，那我们就直接进入实战阶段。

  为了触发 Claude 的最高效开发模式（Superpowers），建议你按照下面的顺序，一个一个模块地要求它输出。

 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Press Ctrl-C again to exit

Resume this session with:
claude --resume 7d5f16b1-9360-41c1-bf6e-59adc24f320a
PS C:\Windows\System32> :\Projects\SmartIcon
:\Projects\SmartIcon: The term ':\Projects\SmartIcon' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> E:\Projects\SmartIcon
E:\Projects\SmartIcon: The term 'E:\Projects\SmartIcon' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> Claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> cd E:\Projects\SmartIcon
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
  Create a folder named 'TestFolder', set a custom icon (if you can find a .ico on system or just use shell32.dll
  index), and verify it works.
  ⎿  Please run /login · API Error: 401 Authentication Fails, Your api key: ****706e is invalid

✻ Baked for 3m 7s

> /login

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Login

  Browser didn't open? Use the url below to sign in (c to copy)

  tps://platform.claude.com/oauth/authorize?code=true&client_id=9d1c250a-e61b-44d9-88ed-5944d1962f5e&response_type=cod
  direct_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback&scope=org%3Acreate_api_key+user%3Aprofile+use
  inference+user%3Asessions%3Aclaude_code+user%3Amcp_servers+user%3Afile_upload&code_challenge=Qmsw66wceoP9Axsltiil_MI
  1fbf-tguCP3pgoQs&code_challenge_method=S256&state=0s4MJCyL1uOWa62FGiHu3Ydp8KyOa9BCUpw3Xg1VyPE


  Paste code here if prompted >

  Press Ctrl-C again to exit

Resume this session with:
claude --resume 56660655-139f-43fc-ba54-83ae75093982
PS C:\Windows\System32> ^C
PS C:\Windows\System32> ^C
PS C:\Windows\System32> ^C
PS C:\Windows\System32> ^C
PS C:\Windows\System32> $env:ANTHROPIC_API_KEY = "sk-c8cf2fa5efc44b29b84f4ef6a7b9706e"
PS C:\Windows\System32> # 1. 确保目录存在
PS C:\Windows\System32> mkdir -p E:\Projects\SmartIcon

    Directory: E:\Projects

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    22:03                SmartIcon

PS C:\Windows\System32> cd E:\Projects\SmartIcon
PS E:\Projects\SmartIcon>
PS E:\Projects\SmartIcon> # 2. 带着 Key 启动
PS E:\Projects\SmartIcon> claude
╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                    │ Tips for getting started                                        │
│                    Welcome back!                   │ Ask Claude to create a new app or clone a repository            │
│                                                    │ ─────────────────────────────────────────────────────────────── │
│                       ▐▛███▜▌                      │ What's new                                                      │
│                      ▝▜█████▛▘                     │ Fixed OAuth authentication failing with a 401 retry loop when … │
│                        ▘▘ ▝▝                       │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to… │
│                                                    │ Pasting a PR URL into the `/resume` search box now finds the s… │
│   Sonnet 4.6 with high effort · API Usage Billing  │ /release-notes for more                                         │
│                E:\Projects\SmartIcon               │                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

> "Status: Authenticated. I'm in E:\Projects\SmartIcon. Please create 'engine.py'. Requirement: Write 'desktop.ini' in
  UTF-16 LE with BOM, set folder as ReadOnly, and use SHChangeNotify to refresh. Test it with 'TestFolder' using
  shell32.dll,3."
  ⎿  Please run /login · API Error: 401 Authentication Fails, Your api key: ****706e is invalid

✻ Baked for 3m 2s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts
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

 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Press Ctrl-C again to exit

Resume this session with:
claude --resume 7d5f16b1-9360-41c1-bf6e-59adc24f320a
PS C:\Windows\System32> :\Projects\SmartIcon
:\Projects\SmartIcon: The term ':\Projects\SmartIcon' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> E:\Projects\SmartIcon
E:\Projects\SmartIcon: The term 'E:\Projects\SmartIcon' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> Claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> cd E:\Projects\SmartIcon
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
  Create a folder named 'TestFolder', set a custom icon (if you can find a .ico on system or just use shell32.dll
  index), and verify it works.
  ⎿  Please run /login · API Error: 401 Authentication Fails, Your api key: ****706e is invalid

✻ Baked for 3m 7s

> /login

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Login

  Browser didn't open? Use the url below to sign in (c to copy)

  tps://platform.claude.com/oauth/authorize?code=true&client_id=9d1c250a-e61b-44d9-88ed-5944d1962f5e&response_type=cod
  direct_uri=https%3A%2F%2Fplatform.claude.com%2Foauth%2Fcode%2Fcallback&scope=org%3Acreate_api_key+user%3Aprofile+use
  inference+user%3Asessions%3Aclaude_code+user%3Amcp_servers+user%3Afile_upload&code_challenge=Qmsw66wceoP9Axsltiil_MI
  1fbf-tguCP3pgoQs&code_challenge_method=S256&state=0s4MJCyL1uOWa62FGiHu3Ydp8KyOa9BCUpw3Xg1VyPE


  Paste code here if prompted >

  Press Ctrl-C again to exit

Resume this session with:
claude --resume 56660655-139f-43fc-ba54-83ae75093982
PS C:\Windows\System32> ^C
PS C:\Windows\System32> ^C
PS C:\Windows\System32> ^C
PS C:\Windows\System32> ^C
PS C:\Windows\System32> $env:ANTHROPIC_API_KEY = "sk-c8cf2fa5efc44b29b84f4ef6a7b9706e"
PS C:\Windows\System32> # 1. 确保目录存在
PS C:\Windows\System32> mkdir -p E:\Projects\SmartIcon

    Directory: E:\Projects

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    22:03                SmartIcon

PS C:\Windows\System32> cd E:\Projects\SmartIcon
PS E:\Projects\SmartIcon>
PS E:\Projects\SmartIcon> # 2. 带着 Key 启动
PS E:\Projects\SmartIcon> claude
╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                    │ Tips for getting started                                        │
│                    Welcome back!                   │ Ask Claude to create a new app or clone a repository            │
│                                                    │ ─────────────────────────────────────────────────────────────── │
│                       ▐▛███▜▌                      │ What's new                                                      │
│                      ▝▜█████▛▘                     │ Fixed OAuth authentication failing with a 401 retry loop when … │
│                        ▘▘ ▝▝                       │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to… │
│                                                    │ Pasting a PR URL into the `/resume` search box now finds the s… │
│   Sonnet 4.6 with high effort · API Usage Billing  │ /release-notes for more                                         │
│                E:\Projects\SmartIcon               │                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

> "Status: Authenticated. I'm in E:\Projects\SmartIcon. Please create 'engine.py'. Requirement: Write 'desktop.ini' in
  UTF-16 LE with BOM, set folder as ReadOnly, and use SHChangeNotify to refresh. Test it with 'TestFolder' using
  shell32.dll,3."
  ⎿  Please run /login · API Error: 401 Authentication Fails, Your api key: ****706e is invalid

✻ Baked for 3m 2s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts

看来在配置 Claude Code 的过程中遇到了一些小麻烦。虽然你已经在 PowerShell 中设置了 ANTHROPIC_API_KEY 环境变量，但工具似乎在身份验证上依然卡在了 OAuth 流程或旧的 Key 上。
既然你现在处于 E:\Projects\SmartIcon 目录，且急需完成这个 engine.py 的核心逻辑，我直接为你编写这个“高功耗（High-effort）”版本的代码。你可以先手动创建文件并运行，等 Claude Code 的环境稳定后再进行后续的 AI 自动化。
engine.py 实现代码
import os
import ctypes
import struct
from pathlib import Path

# Windows 常量定义
FILE_ATTRIBUTE_READONLY = 0x01
FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04
SHCNE_ASSOCCHANGED = 0x08000000
SHCNF_IDLIST = 0

def is_admin():
    """检查是否拥有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def set_folder_custom_icon(folder_path, icon_path, icon_index=0, infotip="SmartIcon Customized"):
    """
    核心逻辑：
    1. 设置文件夹为只读属性（Windows 识别 desktop.ini 的前提）
    2. 创建 UTF-16 LE BOM 编码的 desktop.ini
    3. 设置 desktop.ini 为 隐藏+系统 属性
    4. 刷新系统 Shell
    """
    folder = Path(folder_path).resolve()
    if not folder.exists():
        folder.mkdir(parents=True)

    # 1. 设置文件夹属性为 ReadOnly
    ctypes.windll.kernel32.SetFileAttributesW(str(folder), FILE_ATTRIBUTE_READONLY)

    # 2. 准备 desktop.ini 内容
    ini_content = [
        '[.ShellClassInfo]',
        f'IconResource={icon_path},{icon_index}',
        f'InfoTip={infotip}',
        '[ViewState]',
        'Mode=',
        'Vid=',
        'FolderType=Generic'
    ]
    ini_text = '\r\n'.join(ini_content) + '\r\n'
    ini_path = folder / 'desktop.ini'

    # 3. 写入文件 (UTF-16 LE with BOM)
    with open(ini_path, 'wb') as f:
        f.write(struct.pack('<H', 0xFEFF))  # BOM
        f.write(ini_text.encode('utf-16-le'))

    # 4. 设置 desktop.ini 属性为 Hidden + System
    ctypes.windll.kernel32.SetFileAttributesW(str(ini_path), FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)

    # 5. 刷新 Shell
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    print(f"成功：文件夹 '{folder.name}' 已更新图标。")

def remove_customization(folder_path):
    """清理自定义设置"""
    folder = Path(folder_path).resolve()
    ini_path = folder / 'desktop.ini'
    
    if ini_path.exists():
        # 先去掉隐藏属性才能删除
        ctypes.windll.kernel32.SetFileAttributesW(str(ini_path), 128) # Normal
        os.remove(ini_path)
    
    # 去掉文件夹只读属性
    ctypes.windll.kernel32.SetFileAttributesW(str(folder), 128)
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    print(f"已恢复文件夹 '{folder.name}' 的默认外观。")

if __name__ == "__main__":
    if not is_admin():
        print("警告：部分系统环境下修改属性可能需要管理员权限。")

    test_dir = Path("E:/Projects/SmartIcon/TestFolder")
    # 使用系统自带的 shell32.dll 中的图标 (索引 3 通常是一个文件夹图标)
    system_icon_dll = "C:\\Windows\\System32\\shell32.dll"
    
    set_folder_custom_icon(test_dir, system_icon_dll, 3, "这是通过 SmartIcon 引擎生成的测试文件夹")


💡 为什么 Claude Code 报错 401？
你的 API Key 看起来是有效的（格式正确），但报错 401 Authentication Fails 通常有三个原因：

全局代理问题：Claude Code 在终端运行时，如果你的网络代理没有正确劫持 Node.js 的请求，会导致握手失败。
Key 的作用域：如果是新生成的 Key，可能需要几分钟激活，或者该 Key 属于一个没有额度的 Organization。
配置冲突：Claude Code 优先读取它自己的 OAuth 配置文件。

解决办法：尝试运行 claude config set ANTHROPIC_API_KEY sk-c8cf...9706e（如果该命令可用），或者直接清理配置：rm -rf ~/.claude-code (Linux/Mac) 或删除 %USERPROFILE%\.claude-code (Windows)。



下一步操作

手动运行 python engine.py 验证文件夹图标是否变化。
关于 Claude Code，建议检查一下你的 Anthropic Dashboard 确认 API 余额是否充足，因为 401 有时也代表账户受限。

如果需要我针对 Model Context Protocol (MCP) 接入这个脚本的控制逻辑，请随时告诉我！

---
*从 Gemini 导出，2026-05*
