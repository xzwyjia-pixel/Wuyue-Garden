---
title: PS C:\Windows\System32> get-shit-done-cc --version

   ██████╗ ███████╗██████╗
  ██╔════╝ ██╔════╝██╔══██╗
  ██║  ███╗███████╗██║  ██║
  ██║   ██║╚════██║██║  ██║
  ╚██████╔╝███████║██████╔╝
   ╚═════╝ ╚══════╝╚═════╝

  GSD Code-First v1.3.3
  Code-first development fork of GSD — build first, annotate,
  iterate. For Claude Code, OpenCode, Gemini, Codex, Copilot, Antigravity, Cursor, and Windsurf.

  Which runtime(s) would you like to install for?

  1) Claude Code  (~/.claude)
  2) OpenCode     (~/.config/opencode) - open source, free models
  3) Gemini       (~/.gemini)
  4) Codex        (~/.codex)
  5) Copilot      (~/.copilot)
  6) Antigravity  (~/.gemini/antigravity)
  7) Cursor       (~/.cursor)
  8) Windsurf     (~/.windsurf)
  9) All

  Select multiple: 1,4,6 or 1 4 6

  Choice [1]: 1
  Where would you like to install?

  1) Global (~\.claude) - available in all projects
  2) Local  (./.claude) - this project only

  Choice [1]: 1
  Installing for Claude Code to ~\.claude

  ✓ Installed commands/gsd
  ✓ Installed get-shit-done
  ✓ Installed agents
  ✓ Wrote VERSION (1.3.3)
  ✓ Wrote package.json (CommonJS mode)
  ✓ Installed hooks (bundled)
  ✓ Wrote file manifest (gsd-file-manifest.json)
  ✓ Configured update check hook
  ✓ Configured context window monitor hook
  ✓ Configured prompt injection guard hook

  ⚠ Existing statusline detected

  Your current statusline:
    command: powershell -ExecutionPolicy Bypass -File "C:\Users\think\.claude\plugins\cache\caveman\caveman\ef6050c5e184\hooks\caveman-statusline.ps1"

  GSD includes a statusline showing:
    • Model name
    • Current task (from todo list)
    • Context window usage (color-coded)

  1) Keep existing
  2) Replace with GSD statusline

  Choice [1]:
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## PS C:\Windows\System32> get-shit-done-cc --version

   ██████╗ ███████╗██████╗
  ██╔════╝ ██╔════╝██╔══██╗
  ██║  ███╗███████╗██║  ██║
  ██║   ██║╚════██║██║  ██║
  ╚██████╔╝███████║██████╔╝
   ╚═════╝ ╚══════╝╚═════╝

  GSD Code-First v1.3.3
  Code-first development fork of GSD — build first, annotate,
  iterate. For Claude Code, OpenCode, Gemini, Codex, Copilot, Antigravity, Cursor, and Windsurf.

  Which runtime(s) would you like to install for?

  1) Claude Code  (~/.claude)
  2) OpenCode     (~/.config/opencode) - open source, free models
  3) Gemini       (~/.gemini)
  4) Codex        (~/.codex)
  5) Copilot      (~/.copilot)
  6) Antigravity  (~/.gemini/antigravity)
  7) Cursor       (~/.cursor)
  8) Windsurf     (~/.windsurf)
  9) All

  Select multiple: 1,4,6 or 1 4 6

  Choice [1]: 1
  Where would you like to install?

  1) Global (~\.claude) - available in all projects
  2) Local  (./.claude) - this project only

  Choice [1]: 1
  Installing for Claude Code to ~\.claude

  ✓ Installed commands/gsd
  ✓ Installed get-shit-done
  ✓ Installed agents
  ✓ Wrote VERSION (1.3.3)
  ✓ Wrote package.json (CommonJS mode)
  ✓ Installed hooks (bundled)
  ✓ Wrote file manifest (gsd-file-manifest.json)
  ✓ Configured update check hook
  ✓ Configured context window monitor hook
  ✓ Configured prompt injection guard hook

  ⚠ Existing statusline detected

  Your current statusline:
    command: powershell -ExecutionPolicy Bypass -File "C:\Users\think\.claude\plugins\cache\caveman\caveman\ef6050c5e184\hooks\caveman-statusline.ps1"

  GSD includes a statusline showing:
    • Model name
    • Current task (from todo list)
    • Context window usage (color-coded)

  1) Keep existing
  2) Replace with GSD statusline

  Choice [1]:

这一步是你安装过程中最关键的**“界面集成”**决策。
作为一名拥有工业自动化背景的专业人士，你一定理解“仪表盘”的重要性。这里 GSD 提示检测到了你之前安装的 Superpowers（它使用了 caveman 插件）已经占用了状态栏（statusline）。
建议选择：2（Replace with GSD statusline）
理由如下：

信息密度更高： GSD 的状态栏不仅能显示模型名称，最重要的是它能实时监控上下文窗口（Context Window）使用量并以颜色预警。这对于防止 Claude “变傻”至关重要。
任务追踪： 它能直接显示你当前正在执行的待办事项（Todo list），让你在复杂的“语义文件夹”开发中始终保持目标清晰。
兼容性： 虽然你替换了显示界面，但 Superpowers 的核心逻辑（TDD 和规则约束）依然是在后台运行的，并不会因为状态栏变了就失效。


选择后的动作：

输入 2 并回车。
安装完成后，GSD 会完成最后的配置写入。
重启你的 Claude Code 终端。

接下来如何验证？
当你再次进入项目目录并启动 claude 时，你应该能在底部看到一个全新的、更现代的仪表盘。此时，你可以尝试输入：
gsd help
如果你能看到一连串以 gsd- 开头的指令，说明你的**“超强复合工具链”**已经完全合体。

⚠️ 给 45 岁项目管理者的特别提醒：
你现在已经把 Superpowers 的质量控制和 GSD 的流程监控强行揉合在了一起。这是一个非常强大的组合，但也可能产生“指令重叠”。
如果 Claude 运行异常，请记住这个“紧急救援”指令：
如果发现 CLAUDE.md 里的规则太多导致 Claude 混乱，你可以手动打开它，删除重复的指令，只保留：

Superpowers 的测试要求。
GSD 的阶段（Phases）管理逻辑。

现在请按下 2，完成这最后的“仪表盘”升级！

---
*从 Gemini 导出，2026-05*
