---
title: ╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: Claude/MCP
tags: [gemini, 系统运维, PowerShell]
---

## ╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮

## ╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│                                    │ Tips for getting started                                                        │
│            Welcome back!           │ Run /init to create a CLAUDE.md file with instructions for Claude               │
│                                    │ ─────────────────────────────────────────────────────────────────────────────── │
│               ▐▛███▜▌              │ What's new                                                                      │
│              ▝▜█████▛▘             │ Fixed OAuth authentication failing with a 401 retry loop when `CLAUDE_CODE_DIS… │
│                ▘▘ ▝▝               │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to select a Bedroc… │
│                                    │ Pasting a PR URL into the `/resume` search box now finds the session that crea… │
│   Sonnet 3.7 · API Usage Billing   │ /release-notes for more                                                         │
│         E:\MyCodeProjects          │                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

> /init
  ⎿  Retrying in 9s · attempt 6/10

* Flambéing… (25s)

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt

甄先生，看到 "Retrying... attempt 6/10"，这说明邮递员（Claude Code）手里拿着你要寄出的信，但地址单上写的是**“你的真实代理域名.com”**，由于找不到这个地方，他在原地打转。
目前的问题在于：你之前的 PowerShell 命令并没有把“占位符”替换成实际生效的英文地址。
请立即按 Esc 中断当前操作，并按照以下精密步骤进行最后一次物理层面的修复：
1. 确认你的“真实地址”
你需要从你的 API 供应商（中转商）那里获取两个关键信息：

Base URL：例如 https://api.gptsapi.net 或 https://api.openai-hk.com。
API Key：形如 sk-xxxx....。

2. 在 PowerShell 中注入真实数据
请先退出 Claude Code（输入 exit 或直接关掉黑窗口），在 PowerShell 蓝底窗口中逐行执行以下指令（请将引号内的中文替换为你的实际英文地址/Key）：
# 1. 设定真实的代理地址（注意：末尾不要带 /v1）
$myRealUrl = "https://这里填你代理商的域名.com"

# 2. 设定真实的 API 密钥
$myRealKey = "sk-这里填你真实的Key"

# 3. 强制覆盖系统变量（永久生效）
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $myRealUrl, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $myRealKey, "User")

# 4. 让当前窗口立即刷新
$env:ANTHROPIC_BASE_URL = $myRealUrl
$env:ANTHROPIC_API_KEY = $myRealKey

3. 清理缓存（关键！）
Claude Code 会缓存上一次错误的 https://你的真实代理域名.com。必须删掉缓存文件：
Remove-Item "$env:AppData\claude-code\config.json" -Force -ErrorAction SilentlyContinue

4. 重新起航
现在回到你的根目录启动，你会发现“重试”和“Flambéing”的卡顿感会瞬间消失：
cd "E:\MyCodeProjects"
claude --model claude-3-7-sonnet-20250219


甄先生，如何判断是否成功？
再次启动后，输入 /status。

失败状态：Anthropic base URL 后面还带着“你的真实代理域名...”字样。
成功状态：Anthropic base URL 显示的是你代理商的纯英文官方地址。

只要地址变成了真实的英文域名，/init 就能在 1 秒内响应。
甄先生，如果你不确定你的代理商地址具体是多少，可以把地址发给我（注意遮掩 Key 的中间部分），我来帮你拼写正确的 PowerShell 命令。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
