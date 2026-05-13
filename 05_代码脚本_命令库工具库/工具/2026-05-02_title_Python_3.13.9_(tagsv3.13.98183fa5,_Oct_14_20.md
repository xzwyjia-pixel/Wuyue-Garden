---
title: Python 3.13.9 (tags/v3.13.9:8183fa5, Oct 14 2025, 14:09:13) [MSC v.1944 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import subprocess
>>> import sys
>>> import os
>>>
>>> def check_command(command, args=["--version"]):
...         try:
...                         result = subprocess.run([command] + args, capture_output=True, text=True, timeout=5)
...                                 if result.returncode == 0:
...                                                     return result.stdout.strip().split('\n')[0]
...                                                             return None
...                                                                 except Exception:
...                                                                                 return None
...
  File "<python-input-4>", line 4
    if result.returncode == 0:
IndentationError: unexpected indent
>>> def detect_environment():
...             print(" 正在检测电脑 AI 开发环境...\n" + "-"*40)
...
>>>     checks = {
  File "<python-input-6>", line 1
    checks = {
IndentationError: unexpected indent
>>>         "Python 版本": ("python", ["--version"]),
  File "<python-input-7>", line 1
    "Python 版本": ("python", ["--version"]),
IndentationError: unexpected indent
>>>         "Node.js 版本": ("node", ["--version"]),
  File "<python-input-8>", line 1
    "Node.js 版本": ("node", ["--version"]),
IndentationError: unexpected indent
>>>         "Ollama 运行状态": ("ollama", ["list"]),
  File "<python-input-9>", line 1
    "Ollama 运行状态": ("ollama", ["list"]),
IndentationError: unexpected indent
>>>         "Git 安装状态": ("git", ["--version"]),
  File "<python-input-10>", line 1
    "Git 安装状态": ("git", ["--version"]),
IndentationError: unexpected indent
>>>     }
  File "<python-input-11>", line 1
    }
IndentationError: unexpected indent
>>>
>>>     results = {}
  File "<python-input-13>", line 1
    results = {}
IndentationError: unexpected indent
>>>     for name, (cmd, args) in checks.items():
  File "<python-input-14>", line 1
    for name, (cmd, args) in checks.items():
IndentationError: unexpected indent
>>>         version = check_command(cmd, args)
  File "<python-input-15>", line 1
    version = check_command(cmd, args)
IndentationError: unexpected indent
>>>         results[name] = version if version else " 未找到 (Not Found)"
  File "<python-input-16>", line 1
    results[name] = version if version else " 未找到 (Not Found)"
IndentationError: unexpected indent
>>>         print(f"{name}: {results[name]}")
  File "<python-input-17>", line 1
    print(f"{name}: {results[name]}")
IndentationError: unexpected indent
>>>
>>>     # 检测 MCP 配置文件是否存在 (默认路径)
>>>     mcp_path = os.path.expanduser("~/.config/claude-desktop/config.json")
  File "<python-input-20>", line 1
    mcp_path = os.path.expanduser("~/.config/claude-desktop/config.json")
IndentationError: unexpected indent
>>>     if not os.path.exists(mcp_path):
  File "<python-input-21>", line 1
    if not os.path.exists(mcp_path):
IndentationError: unexpected indent
>>>         mcp_path = os.path.expanduser("~/AppData/Roaming/Claude/config.json") # Windows 路径
  File "<python-input-22>", line 1
    mcp_path = os.path.expanduser("~/AppData/Roaming/Claude/config.json") # Windows 路径
IndentationError: unexpected indent
>>>
>>>     print(f"MCP 配置文件状态: {' 已找到' if os.path.exists(mcp_path) else ' 未找到 (通常在初次配置时创建)'}")
  File "<python-input-24>", line 1
    print(f"MCP 配置文件状态: {' 已找到' if os.path.exists(mcp_path) else ' 未找到 (通常在初次配置时创建)'}")
IndentationError: unexpected indent
>>>     print("-"*40)
  File "<python-input-25>", line 1
    print("-"*40)
IndentationError: unexpected indent
>>>     return results
  File "<python-input-26>", line 1
    return results
IndentationError: unexpected indent
>>>
>>> if __name__ == "__main__":
...                 detect_environment()
source: gemini
date: 2026-05-02
category: 系统运维
tags: [gemini, 系统运维]
---

## Python 3.13.9 (tags/v3.13.9:8183fa5, Oct 14 2025, 14:09:13) [MSC v.1944 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import subprocess
>>> import sys
>>> import os
>>>
>>> def check_command(command, args=["--version"]):
...         try:
...                         result = subprocess.run([command] + args, capture_output=True, text=True, timeout=5)
...                                 if result.returncode == 0:
...                                                     return result.stdout.strip().split('\n')[0]
...                                                             return None
...                                                                 except Exception:
...                                                                                 return None
...
  File "<python-input-4>", line 4
    if result.returncode == 0:
IndentationError: unexpected indent
>>> def detect_environment():
...             print(" 正在检测电脑 AI 开发环境...\n" + "-"*40)
...
>>>     checks = {
  File "<python-input-6>", line 1
    checks = {
IndentationError: unexpected indent
>>>         "Python 版本": ("python", ["--version"]),
  File "<python-input-7>", line 1
    "Python 版本": ("python", ["--version"]),
IndentationError: unexpected indent
>>>         "Node.js 版本": ("node", ["--version"]),
  File "<python-input-8>", line 1
    "Node.js 版本": ("node", ["--version"]),
IndentationError: unexpected indent
>>>         "Ollama 运行状态": ("ollama", ["list"]),
  File "<python-input-9>", line 1
    "Ollama 运行状态": ("ollama", ["list"]),
IndentationError: unexpected indent
>>>         "Git 安装状态": ("git", ["--version"]),
  File "<python-input-10>", line 1
    "Git 安装状态": ("git", ["--version"]),
IndentationError: unexpected indent
>>>     }
  File "<python-input-11>", line 1
    }
IndentationError: unexpected indent
>>>
>>>     results = {}
  File "<python-input-13>", line 1
    results = {}
IndentationError: unexpected indent
>>>     for name, (cmd, args) in checks.items():
  File "<python-input-14>", line 1
    for name, (cmd, args) in checks.items():
IndentationError: unexpected indent
>>>         version = check_command(cmd, args)
  File "<python-input-15>", line 1
    version = check_command(cmd, args)
IndentationError: unexpected indent
>>>         results[name] = version if version else " 未找到 (Not Found)"
  File "<python-input-16>", line 1
    results[name] = version if version else " 未找到 (Not Found)"
IndentationError: unexpected indent
>>>         print(f"{name}: {results[name]}")
  File "<python-input-17>", line 1
    print(f"{name}: {results[name]}")
IndentationError: unexpected indent
>>>
>>>     # 检测 MCP 配置文件是否存在 (默认路径)
>>>     mcp_path = os.path.expanduser("~/.config/claude-desktop/config.json")
  File "<python-input-20>", line 1
    mcp_path = os.path.expanduser("~/.config/claude-desktop/config.json")
IndentationError: unexpected indent
>>>     if not os.path.exists(mcp_path):
  File "<python-input-21>", line 1
    if not os.path.exists(mcp_path):
IndentationError: unexpected indent
>>>         mcp_path = os.path.expanduser("~/AppData/Roaming/Claude/config.json") # Windows 路径
  File "<python-input-22>", line 1
    mcp_path = os.path.expanduser("~/AppData/Roaming/Claude/config.json") # Windows 路径
IndentationError: unexpected indent
>>>
>>>     print(f"MCP 配置文件状态: {' 已找到' if os.path.exists(mcp_path) else ' 未找到 (通常在初次配置时创建)'}")
  File "<python-input-24>", line 1
    print(f"MCP 配置文件状态: {' 已找到' if os.path.exists(mcp_path) else ' 未找到 (通常在初次配置时创建)'}")
IndentationError: unexpected indent
>>>     print("-"*40)
  File "<python-input-25>", line 1
    print("-"*40)
IndentationError: unexpected indent
>>>     return results
  File "<python-input-26>", line 1
    return results
IndentationError: unexpected indent
>>>
>>> if __name__ == "__main__":
...                 detect_environment()

看来在 Python 交互式命令行（REPL）中直接粘贴代码遇到了缩进错误（IndentationError）。这是因为 Python 对空格非常敏感，直接粘贴多行代码时，命令行往往无法正确处理。
为了解决这个问题，我们换一种更简单、更专业的方法。
第一步：创建并运行检测脚本
不要在命令行里一行行输入，请按以下步骤操作：

在你的电脑桌面或任何文件夹里，新建一个文本文档。
将文本文档重命名为 check_env.py（确保后缀名是 .py 而不是 .txt）。
将下面的代码全部复制并粘贴到这个文件中，然后保存。

import subprocess
import os
import platform

def check_command(command, args=["--version"]):
    try:
        # 使用 shell=True 兼容 Windows 环境
        result = subprocess.run([command] + args, capture_output=True, text=True, timeout=5, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
        return None
    except Exception:
        return None

def detect_environment():
    print(f"🚀 正在检测电脑 AI 开发环境... (系统: {platform.system()})")
    print("-" * 50)
    
    # 核心环境检测
    checks = {
        "Python 版本": ("python", ["--version"]),
        "Node.js 版本": ("node", ["--version"]),
        "Git 工具状态": ("git", ["--version"]),
        "Ollama (本地LLM)": ("ollama", ["--version"]),
    }

    for name, (cmd, args) in checks.items():
        version = check_command(cmd, args)
        status = f"✅ {version}" if version else "❌ 未找到 (请安装)"
        print(f"{name:15}: {status}")

    # MCP 配置文件检测 (Windows 专用路径)
    appdata = os.environ.get('APPDATA')
    mcp_paths = [
        os.path.join(appdata, "Claude", "config.json"),
        os.path.join(appdata, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json")
    ]
    
    print("\nMCP 配置文件检测:")
    for path in mcp_paths:
        exists = "✅ 已找到" if os.path.exists(path) else "❌ 未找到"
        print(f"  路径: ...{path[-50:]} -> {exists}")

    print("-" * 50)
    print("检测完成！")

if __name__ == "__main__":
    detect_environment()


运行它：

在文件夹空白处按住 Shift 键并右击鼠标，选择“在此处打开 PowerShell 窗口”或“在终端中打开”。
输入命令：python check_env.py 并回车。




第二步：根据结果找到还需要安装的软件
运行完上面的脚本后，请观察输出：

如果 Git 是 ❌：你需要安装 Git for Windows。这是下载 scholar-skill 源码的基础。
如果 Node.js 是 ❌：虽然你主要用 Python，但很多 MCP 核心组件依赖 Node.js 运行环境，建议去 Node.js 官网 安装 LTS 版本。
如果 MCP 配置文件全是 ❌：说明你虽然安装了 VS Code，但还没正式开启过 Cline 或 Claude Dev 的 MCP 功能。

第三步：现在你应该做什么？
既然你已经准备好了 Python 3.13 环境，你现在的首要任务是：

安装 Git：因为 scholar-skill 这种技能通常托管在 GitHub 上，没有 Git 你很难将其同步到本地并保持更新。
在 VS Code 中安装 Cline 插件：如果你还没装，这是连接 scholar-skill 和你本地 Ollama 模型的“桥梁”。
准备 Skill 存放目录：在你的 D 盘或用户目录下新建一个文件夹，例如 C:\AI_Skills，这将是你以后存放所有 MCP 技能（包括这次的 scholar-skill）的基地。

你可以先运行脚本，把输出的结果告诉我，我再帮你针对性地写下一步的配置代码。

---
*从 Gemini 导出，2026-05*
