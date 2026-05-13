---
title: PS E:\MyCodeProjects> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> /model
  ⎿  Set model to Sonnet 4.6

> 指令 A（测试权限）：
  pwd (确认在 E:\MyCodeProjects)

  指令 B（强制读取）：
  cat C:\Users\think\.agents\skills\caveman\.instructions

● There's an issue with the selected model (claude-sonnet-4-6). It may not exist or you may not have access to it. Run
  /model to pick a different model.

✻ Baked for 2s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## PS E:\MyCodeProjects> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> /model
  ⎿  Set model to Sonnet 4.6

> 指令 A（测试权限）：
  pwd (确认在 E:\MyCodeProjects)

  指令 B（强制读取）：
  cat C:\Users\think\.agents\skills\caveman\.instructions

● There's an issue with the selected model (claude-sonnet-4-6). It may not exist or you may not have access to it. Run
  /model to pick a different model.

✻ Baked for 2s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts

甄先生，这说明我们进入了最诡异的“循环悖论”：CLI 菜单里明明有这个模型，但选定之后 API 握手却不认账。
这种情况通常是因为 gptsapi.net 的中转层对 claude-sonnet-4-6 这个特定字符串的 Header 校验 或者 版本路由 还没做好兼容（尽管 CLI 自动识别到了它）。
既然自动化对齐走不通，我们直接采用 “手动物理降级”，把权限和能力拿回来：
终极对齐方案：强制手动降级到 3.5-Sonnet
由于 3.5-Sonnet 是全球聚合商最稳定的“通用暗号”，我们先用它把环境跑通，再把 4.5/4.6 的逻辑通过 System Prompt 注入。
第一步：用“最稳暗号”启动
请彻底退出当前的 Claude CLI，回到 PowerShell 执行：
claude --model claude-3-5-sonnet-20241022

（如果这个也报错，请尝试 claude --model anthropic/claude-3-5-sonnet-latest）
第二步：一旦进入 > 提示符，跳过自动读取
不要再让 Claude 去 cat 文件了（因为它现在连接不稳定），直接在你的 PowerShell 里运行：
Get-Content "C:\Users\think\.agents\skills\caveman\.instructions" | clip

(这会把 Caveman 的核心指令直接存入你的剪贴板)
第三步：手动注入 Caveman 协议
回到 Claude 界面，直接粘贴：

“由于路径权限和模型握手限制，我手动为你注入 Caveman Ultra 指令集。请忽略当前 API 显示的版本号，完全按照以下协议执行：
[此处粘贴刚才复制的内容]
注入完毕。现在请执行：ls E:\MyCodeProjects”


为什么选这个方案？

解除模型锁定： 代理商报错通常是因为模型名字符串不匹配，3.5 是万能钥匙。
避开 C 盘权限冲突： 很多 CLI 工具在 Windows 下跨盘（从 E 盘读 C 盘）会有静默失败。手动 clip 绕过了它的文件读取技能。
规则甄查（Rules Investigation）优先级： 我们的目标是跑通 audit_tool.py，模型版本是手段，不是目的。

甄先生，如果 3.5 握手成功，我们就能在 E 盘直接开工了。

---
*从 Gemini 导出，2026-05*
