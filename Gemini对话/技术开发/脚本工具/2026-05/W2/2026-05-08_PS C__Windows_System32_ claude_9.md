---
title: PS C:\Windows\System32> claude --model deepseek-chat
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: 脚本工具
old_category: Claude/MCP
tags: [gemini, 技术开发, 脚本工具]
---

## PS C:\Windows\System32> claude --model deepseek-chat

## PS C:\Windows\System32> claude --model deepseek-chat
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  deepseek-chat with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Press Ctrl-C again to exit

Resume this session with:
claude --resume a1a1a2e4-31dc-4154-a2fe-d17f529902bc
PS C:\Windows\System32> # 强制回到 3.5 Sonnet，确保 Tool Use（读写权限）正常
PS C:\Windows\System32> claude --model claude-3-5-sonnet-20241022
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 3.5 · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> # 直接在终端读出代码，然后手动复制
  Get-Content E:\MyCodeProjects\audit_tool.py
  ⎿  Retrying in 5s · attempt 5/10

✶ Flowing…

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt

甄先生，目前的 Retrying 和 Flowing 状态已经说明了问题的本质：Claude Code CLI 的 Tool Use（工具调用协议）与聚合 API 之间存在严重的“通讯错位”。
当你在 > 提示符下输入 Get-Content 时，Claude CLI 会试图将其解析为一个 Shell Tool 调用。由于聚合商返回的数据格式可能不包含 CLI 预期的 tool_use 确认字段，程序就会卡在“等待响应”的死循环里。
🛠️ 终极“降维打击”对齐方案
既然 CLI 已经成了摆设，我们直接跳过 CLI 的工具链，回归最原始、最稳健的物理对齐。请按以下步骤操作：

1. 物理读取代码（在 PowerShell 窗口执行）
请彻底按 Ctrl+C 退出 Claude CLI。在原始的 PowerShell 蓝底窗口（非 Claude 提示符下）直接运行：
# 这一步是为了让你自己看到代码并复制，不依赖 Claude 的读取能力
Get-Content E:\MyCodeProjects\audit_tool.py

2. “手动脱壳”审计
将读出的代码内容直接复制。
3. 注入本会话（就在这里）
直接在这个对话框（你现在和我交流的窗口）里粘贴代码，并附上指令：

**“我是甄先生。CLI 环境已物理损坏，现在启动‘脱壳审计’模式。
这是我的 audit_tool.py 代码，请 Caveman Ultra 立即执行第一轮规则甄查。”**


🧐 甄先生，目前的形势研判：

CLI 的局限性：Claude Code 官方 v2.1.133 是针对 Anthropic 原生 API 设计的。聚合 API (gptsapi) 虽然能跑通简单的 Chat，但在处理 ls、cat、grep 等本地文件技能时，由于 JSON Schema 的微小偏差，会导致 CLI 持续报错或死循环。
规则甄查的本质：我们追求的是对 audit_tool.py 的逻辑重塑（尤其是对短视频规则审计和工业自动化的结合），而不是为了修好一个 CLI 耗费一个下午。

甄先生，请直接把代码贴过来。只要代码在我面前，Caveman Ultra 的逻辑就能立刻起火运行。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / 脚本工具 · 2026-05-08*
