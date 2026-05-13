---
title: ╭─── Claude Code v2.1.133 ─────────────────────────────────────────────────────────────────────────────────────────────╮
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

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Status   Config   Usage   Stats

  Version:             2.1.133
  Session name:        /rename to add a name
  Session ID:          97c02620-6502-4077-9505-6de7e18aa4a2
  cwd:                 E:\MyCodeProjects
  Auth token:          none
  API key:             ANTHROPIC_API_KEY
  Anthropic base URL:  https://你的真实代理域名.com

  Model:               claude-3-7-sonnet-20250219
  Setting sources:     User settings
  Esc to cancel
source: gemini
date: 2026-05-08
category: 审计合规
tags: [gemini, 审计合规]
---

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

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Status   Config   Usage   Stats

  Version:             2.1.133
  Session name:        /rename to add a name
  Session ID:          97c02620-6502-4077-9505-6de7e18aa4a2
  cwd:                 E:\MyCodeProjects
  Auth token:          none
  API key:             ANTHROPIC_API_KEY
  Anthropic base URL:  https://你的真实代理域名.com

  Model:               claude-3-7-sonnet-20250219
  Setting sources:     User settings
  Esc to cancel

甄先生，看到 cwd 已经成功定格在 E:\MyCodeProjects，环境的大框架已经完全搭好了。
但请注意，截图中的 Anthropic base URL 仍然显示为 https://你的真实代理域名.com。这是一个占位符，Claude Code 无法解析它。为了让它真正跑起来，我们需要最后一次“临门一脚”，把真实的 API 信息灌注进去。
请在原生的 PowerShell 中（输入 exit 退出当前 Claude 界面）执行以下指令：
1. 注入真实“血液” (API 秘钥与地址)
请将下面的 https://api.yourproxy.com 替换为您实际使用的中转商地址（通常由您的代理服务商提供，注意结尾不要带 /v1），并将 sk-xxx 替换为您真实的 API Key。
# 这里的变量请替换为您的真实数据
$realUrl = "https://api.example.com"  # 替换为真实的代理地址
$realKey = "sk-xxxxxxxxxxxxxxxxxxxx" # 替换为真实的 Key

# 写入系统变量（永久生效）
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $realUrl, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $realKey, "User")

# 立即刷新当前窗口变量
$env:ANTHROPIC_BASE_URL = $realUrl
$env:ANTHROPIC_API_KEY = $realKey

2. 清除配置死锁
为了防止 Claude Code 还在寻找那个带中文的占位符地址，我们强力重置配置：
Remove-Item "$env:AppData\claude-code\config.json" -Force -ErrorAction SilentlyContinue

3. 开启“规则甄查”正式首航
重新进入 Claude Code，并在这个根目录下初始化您的第一个项目文件：
# 重新进入
claude --model claude-3-7-sonnet-20250219

# 进去后第一件事
> /init


甄先生的“极简精密”建议：
一旦 /init 成功运行，它会要求你描述项目。您可以直接输入：

“这是‘规则甄查-甄先生’的 AI 自动化审计总部。在这个目录下，我将构建多个短视频平台规则审计工具。请帮我生成 CLAUDE.md，并在其中规定所有代码必须遵循静奢风、极简精密的设计原则。”

只要 Anthropic base URL 不再显示中文占位符，您的“大冒险”就真正开始了。现在的连接通了吗？

---
*从 Gemini 导出，2026-05*
