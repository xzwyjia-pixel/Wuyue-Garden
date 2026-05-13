---
title: │                                          │ ───────────────────────────────────────────────────────────────────────── │
╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│                                          │ Tips for getting started                                                  │
│               Welcome back!              │ Run /init to create a CLAUDE.md file with instructions for Claude         │
│                                          │ ───────────────────────────────────────────────────────────────────────── │
│                  ▐▛███▜▌                 │ What's new                                                                │
│                 ▝▜█████▛▘                │ Fixed OAuth authentication failing with a 401 retry loop when `CLAUDE_CO… │
│                   ▘▘ ▝▝                  │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to select a … │
│                                          │ Pasting a PR URL into the `/resume` search box now finds the session tha… │
│      Sonnet 3.7 · API Usage Billing      │ /release-notes for more                                                   │
│   E:\MyCodeProjects\New Claude Project   │                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

> /status
  ⎿  Status dialog dismissed

> /init
  ⎿  API Error: "你的代理商基础地址/v1/messages?beta=true" cannot be parsed as a URL.

✻ Baked for 0s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## │                                          │ ───────────────────────────────────────────────────────────────────────── │
╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│                                          │ Tips for getting started                                                  │
│               Welcome back!              │ Run /init to create a CLAUDE.md file with instructions for Claude         │
│                                          │ ───────────────────────────────────────────────────────────────────────── │
│                  ▐▛███▜▌                 │ What's new                                                                │
│                 ▝▜█████▛▘                │ Fixed OAuth authentication failing with a 401 retry loop when `CLAUDE_CO… │
│                   ▘▘ ▝▝                  │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to select a … │
│                                          │ Pasting a PR URL into the `/resume` search box now finds the session tha… │
│      Sonnet 3.7 · API Usage Billing      │ /release-notes for more                                                   │
│   E:\MyCodeProjects\New Claude Project   │                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

> /status
  ⎿  Status dialog dismissed

> /init
  ⎿  API Error: "你的代理商基础地址/v1/messages?beta=true" cannot be parsed as a URL.

✻ Baked for 0s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts

甄先生，看来咱们在“最后一公里”遇到了一个中文语境下的路径解析问题。
报错 cannot be parsed as a URL 且路径显示为 你的代理商基础地址/v1/messages，这说明 Claude Code 在解析环境变量时，将你之前输入的占位符文字直接当成了真实的 URL 访问。此外，对于大多数中转代理（SAPI），它们在内部会自动补全 /v1/messages，如果在 ANTHROPIC_BASE_URL 里手动加了 /v1，就会导致路径重叠。
为了让你的“规则甄查”立刻起航，请退出 Claude 界面回到 PowerShell，执行这套**“精密修复”**指令：
1. 修正环境变量（去除占位符与多余路径）
请将下方 https://api.yourproxy.com 替换为你实际的代理商地址（注意：末尾不要加 /v1，也不要带任何中文）。
# 这里的地址需要换成你代理商给出的真实 URL，例如 https://api.openai-hk.com
$realUrl = "https://你的真实代理地址.com" 
$realKey = "sk-你的真实API密钥"

# 覆盖写入系统变量
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $realUrl, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $realKey, "User")

# 刷新当前窗口
$env:ANTHROPIC_BASE_URL = $realUrl
$env:ANTHROPIC_API_KEY = $realKey

2. 暴力重置 Claude Code 缓存
有时候配置文件会死锁旧的错误路径，我们直接将其抹除让它重新读取：
Remove-Item "$env:AppData\claude-code\config.json" -Force -ErrorAction SilentlyContinue

3. 重新进入并启动
现在重新进入项目目录并启动：
cd "E:\MyCodeProjects\New Claude Project"
claude --model claude-3-7-sonnet-20250219


验证与避坑指南
当你再次进入后，先不要急着 /init，先输入以下命令核实：

/status：确保 Anthropic base URL 显示的是你刚刚设置的真实英文字符地址，而不是“你的代理商...”这类文字。
验证连通性：
直接打个招呼：你好，请确认当前环境。

成功：它会正常回复。
失败：如果还是报 URL 错误，尝试将 ANTHROPIC_BASE_URL 设置为完全不带任何后缀的根域名（例如代理商给的是 .../v1，你就设置到 ... 为止）。



甄先生，一旦这个 API 通道打通，/init 就会瞬间为你生成那份精密的 CLAUDE.md。需要我陪你一起确认代理商的准确地址格式吗？

---
*从 Gemini 导出，2026-05*
