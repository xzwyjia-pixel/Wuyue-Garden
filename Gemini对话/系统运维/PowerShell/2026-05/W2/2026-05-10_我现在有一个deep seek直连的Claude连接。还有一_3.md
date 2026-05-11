---
title: 我现在有一个deep seek直连的Claude连接。还有一个gptsapi的中转Claude登录链接。我想把他们的登录信息植入到我的powershell里面，这样就不用每次都输入url和api了。我该怎么操作？
source: gemini
date: 2026-05-10
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## 我现在有一个deep seek直连的Claude连接。还有一个gptsapi的中转Claude登录链接。我想把他们的登录信息植入到我的powershell里面，这样就不用每次都输入url和api了。我该怎么操作？

## 我现在有一个deep seek直连的Claude连接。还有一个gptsapi的中转Claude登录链接。我想把他们的登录信息植入到我的powershell里面，这样就不用每次都输入url和api了。我该怎么操作？

为了实现“一键直达”且无需重复输入 API Key 和 URL，最稳妥且高效的方法是将这些信息配置为 PowerShell 环境变量 或 别名（Aliases）。
由于你使用的是 Claude Code (命令行版)，它通常会读取系统的环境变量。我们可以通过修改 PowerShell 的 Profile（配置文件） 来永久保存这些信息。

🛠️ 第一步：打开你的 PowerShell 配置文件
在 PowerShell 中输入以下命令，这会用记事本打开你的永久启动脚本：
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
notepad $PROFILE


第二步：植入登录信息
在打开的记事本末尾，根据你的两个来源（DeepSeek 直连和 GPTSAPI 中转），粘贴以下配置代码：
# ==========================================
# Claude 登录信息配置 (甄查工作站专用)
# ==========================================

# 1. 设置 DeepSeek 直连环境的快捷函数
function claude-deep {
    $env:CLAUDE_API_KEY = "你的_DeepSeek_Claude_API_Key"
    $env:CLAUDE_BASE_URL = "https://api.deepseek.com/v1" # 请确认为直连的具体 URL
    claude
}

# 2. 设置 GPTSAPI 中转环境的快捷函数
function claude-api {
    $env:CLAUDE_API_KEY = "你的_GPTSAPI_Key"
    $env:CLAUDE_BASE_URL = "https://你的中转地址.com/v1" 
    claude
}

# 可选：设置默认使用的 API (例如默认使用 GPTSAPI)
$env:CLAUDE_API_KEY = "你的_GPTSAPI_Key"
$env:CLAUDE_BASE_URL = "https://你的中转地址.com/v1"


⚠️ 注意：请将上面的 你的_API_Key 和 URL 替换为你手头真实的字符串。


第三步：生效与使用

保存并关闭记事本。
在 PowerShell 中输入以下命令重载配置：
. $PROFILE



🚀 现在你可以这样一键登录：

如果你想用 DeepSeek 直连：直接输入 claude-deep
如果你想用 GPTSAPI 中转：直接输入 claude-api
如果你想用 默认配置：直接输入 claude


💡 为什么这样做更安全、更专业？

解耦管理：你把两个不同的“油箱”（API 来源）分开了，切换起来只需要一个命令，不需要去改代码。
避免硬编码：你的 start_audit.py 脚本不需要再写 API 信息，它会自动从环境变量里“闻”到登录态。
持久化：即便重启电脑，这些信息依然保留在 PowerShell 进程中。


🔍 最后一步自检：验证是否成功
输入以下命令检查环境变量是否已经挂载：
$env:CLAUDE_API_KEY
$env:CLAUDE_BASE_URL

如果输出了你刚才填写的 Key 和 URL，说明你的“甄查工作站”现在已经具备了自动拨号上网的能力。
Michael，现在登录问题解决了。刚才那个报错的 start_audit.py 脚本，在有了这些环境变量后，我们可以直接通过 claude-api 启动它并让 Claude 协助你进行 82% 遮挡率的深度分析了吗？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-10*
