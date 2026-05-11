---
title: ╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: 脚本工具
old_category: 系统运维
tags: [gemini, 技术开发, 脚本工具]
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

> /status
  ⎿  Status dialog dismissed

> /init
  ⎿  Retrying in 12s · attempt 6/10

· Schlepping… (31s)

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt

甄先生，看到 "Retrying... attempt 6/10" 和那长达 31 秒的 "Schlepping"，说明虽然“门牌号”（URL）写对了，但“快递员”可能因为找不到正确的信箱路径而迷路了。
在中转代理（gptsapi.net）的环境下，这通常是因为 Claude Code 自动补全的路径与代理商预期的不一致。
请立即按 Esc 键，退出 Claude 界面，回到 PowerShell 蓝底窗口，我们进行最后一次**“手术级”**的路径校准：
1. 强制校准路径（解决连接超时）
大多数中转代理（如 gptsapi）在处理 Claude 协议时，有时需要明确指定到 /v1。如果之前只填根目录不行，咱们换个精密打法：
# 1. 尝试加上 /v1 路径
$preciseUrl = "https://api.gptsapi.net/v1"

# 2. 确保 API Key 没有前后空格（请替换为您真实的 Key）
$preciseKey = "sk-xxxxxxxxxxxxxxxx" 

# 3. 写入环境变量
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $preciseUrl, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $preciseKey, "User")

# 4. 立即刷新当前窗口
$env:ANTHROPIC_BASE_URL = $preciseUrl
$env:ANTHROPIC_API_KEY = $preciseKey

2. 清除配置“记忆”
删除缓存文件，确保 Claude Code 不会带着旧的错误重试逻辑：
Remove-Item "$env:AppData\claude-code\config.json" -Force -ErrorAction SilentlyContinue

3. 启动并直接下达“极简”指令
重新进入后，跳过 /init 这种复杂的交互，直接输入一句简单的测试：
claude --model claude-3-7-sonnet-20250219

进入后输入：

“你好，我是甄先生。请确认你能否连接。如果成功，请告诉我当前的目录。”


甄先生，如果还是卡在 "Schlepping..."：
这通常意味着代理商的 api.gptsapi.net 在国内网络环境下需要“梯子”辅助，或者该代理商对 Claude 3.7 的特定 API 节点有特殊的地址要求（有的需要 https://api.gptsapi.net/v1/messages 这种全路径）。
我们可以做个对比实验：
如果命令行始终卡住，请打开 VS Code + Cline，并在 Cline 的设置里填入相同的 Base URL 和 Key。

如果 Cline 能跑通，说明是环境变量在命令行下的传递问题。
如果 Cline 也报错，说明是代理地址格式的问题。

咱们要不要试着在 VS Code 里配置一下？那里可以更直白地看到报错代码。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / 脚本工具 · 2026-05-08*
