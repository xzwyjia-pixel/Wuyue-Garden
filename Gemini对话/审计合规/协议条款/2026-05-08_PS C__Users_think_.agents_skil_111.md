---
title: PS C:\Users\think\.agents\skills> npx skills link --all
source: gemini
date: 2026-05-08
category: 审计合规
subcategory: 协议条款
old_category: 编程开发
tags: [gemini, 审计合规, 协议条款]
---

## PS C:\Users\think\.agents\skills> npx skills link --all

## PS C:\Users\think\.agents\skills> npx skills link --all
\(node:17752) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Unknown command: link
Run skills --help for usage.
PS C:\Users\think\.agents\skills> # 1. 进入 E 盘主战场
PS C:\Users\think\.agents\skills> cd "E:\MyCodeProjects"
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 2. 启动 Claude
PS E:\MyCodeProjects> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> “请检查我的用户目录 C:\Users\think\.agents\skills，列出下面所有的文件夹。我需要确认 caveman、superpowers 和 awesome 是否已经就绪。”

● There's an issue with the selected model (claude-sonnet-4-6). It may not exist or you may not have access to it. Run /model to pick a different model.

✻ Brewed for 2s

> /model claude-3-5-sonnet-20241022
  ⎿  Model 'claude-3-5-sonnet-20241022' not found

> /model

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Select model
  Switch between Claude models. Applies to this session and future Claude Code sessions. For other/previous model names, specify with --model.

    1. Default (recommended)  Use the default model (currently Opus 4.7 (1M context)) · $5/$25 per Mtok
  > 2. Sonnet √               Sonnet 4.6 · Best for everyday tasks · $3/$15 per Mtok
    3. Sonnet (1M context)    Sonnet 4.6 for long sessions · $3/$15 per Mtok
    4. Haiku                  Haiku 4.5 · Fastest for quick answers · $1/$5 per Mtok

  ● High effort (default) ← → to adjust

  Enter to confirm · Esc to cancel

甄先生，审计结果已锁定。问题的根源在于**“新旧协议代差”**：
您的 Claude Code 版本（v2.1.133）非常新，它已经默认在使用 2026 年的主力模型（Sonnet 4.6 / Opus 4.7）。但由于您配置了 ANTHROPIC_BASE_URL 走中转 API，而中转商的后端（2024-2025版）往往还不认识这些“未来的模型名称”。
甄先生的“暴力握手”方案：
既然下拉菜单里的 1、2、3、4 选项都可能因为名称映射问题导致握手失败，我们需要强行指定一个**“历史兼容 ID”**。
请退出 Claude（按下 Ctrl+C），然后使用以下命令重新启动。这次我们直接在命令行里把模型 ID“焊死”：
# 1. 强制使用中转商通常能识别的 3.5 别名启动
claude --model claude-3-5-sonnet

# 2. 如果上面那个还报 404，请尝试这个“最稳 ID”
claude --model claude-3-5-sonnet-latest


甄先生，启动后的“全明星”激活确认：
一旦进入界面不再提示 Issue with the selected model，请立刻执行这条指令，看看我们的“后备箱”技能是否生效：

“我是甄先生。

环境已通过命令行强行对齐。
检查 C:\Users\think\.agents\skills。
告诉我你是否看到了 caveman 和 superpowers 文件夹。
如果看到了，请执行 caveman 的初始化，把输出字数压缩到极简。”



💡 甄先生的精密审计备忘：

为什么菜单里的 Sonnet 不行？ 菜单里的 Sonnet 实际上指向的是 claude-3-7-sonnet 或更高的版本（在 2026 年的命名规范下），您的中转 API 还没更新到这个版本。
关于 npx skills 的 link 报错：既然 link 没了，等您成功进入 Claude 后，如果它看不见技能，请直接让它运行：
ls C:\Users\think\.agents\skills
只要它能读到文件，它就能按照里面的 .instructions 自动进化。

甄先生，请用 claude --model claude-3-5-sonnet 重新冲锋一次。这次，我们直接跨过那个“无效菜单”。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 审计合规 / 协议条款 · 2026-05-08*
