---
title:   Skills
  24 skills · Space to cycle, Enter to save, / to search, t to sort, Esc to cancel

  ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
  │ ⌕ Search skills…                                                                                                 │
  ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  > 🔒 on         superpowers:brainstorming · plugin · ~56 tok · locked by plugin
    🔒 on         caveman:cavecrew · plugin · ~142 tok · locked by plugin
    🔒 on         caveman:caveman · plugin · ~102 tok · locked by plugin
    🔒 on         caveman:caveman-commit · plugin · ~92 tok · locked by plugin
    🔒 on         caveman:caveman-help · plugin · ~54 tok · locked by plugin
    🔒 on         caveman:caveman-review · plugin · ~83 tok · locked by plugin
    🔒 on         caveman:caveman-stats · plugin · ~70 tok · locked by plugin
    🔒 on         caveman:compress · plugin · ~88 tok · locked by plugin
    🔒 on         superpowers:dispatching-parallel-agents · plugin · ~37 tok · locked by plugin
    🔒 on         superpowers:executing-plans · plugin · ~33 tok · locked by plugin
    🔒 on         superpowers:finishing-a-development-branch · plugin · ~61 tok · locked by plugin
    🔒 on         frontend-design:frontend-design · plugin · ~67 tok · locked by plugin
    🔒 on         superpowers:receiving-code-review · plugin · ~67 tok · locked by plugin
    🔒 on         superpowers:requesting-code-review · plugin · ~36 tok · locked by plugin
    🔒 on         superpowers:subagent-driven-development · plugin · ~31 tok · locked by plugin
    🔒 on         superpowers:systematic-debugging · plugin · ~31 tok · locked by plugin
    🔒 on         superpowers:test-driven-development · plugin · ~29 tok · locked by plugin
    ↓ 7 more below

  Plugin skills are managed via /plugin
是这样的吗？
source: gemini
date: 2026-05-08
category: 审计合规
tags: [gemini, 审计合规]
---

##   Skills
  24 skills · Space to cycle, Enter to save, / to search, t to sort, Esc to cancel

  ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
  │ ⌕ Search skills…                                                                                                 │
  ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  > 🔒 on         superpowers:brainstorming · plugin · ~56 tok · locked by plugin
    🔒 on         caveman:cavecrew · plugin · ~142 tok · locked by plugin
    🔒 on         caveman:caveman · plugin · ~102 tok · locked by plugin
    🔒 on         caveman:caveman-commit · plugin · ~92 tok · locked by plugin
    🔒 on         caveman:caveman-help · plugin · ~54 tok · locked by plugin
    🔒 on         caveman:caveman-review · plugin · ~83 tok · locked by plugin
    🔒 on         caveman:caveman-stats · plugin · ~70 tok · locked by plugin
    🔒 on         caveman:compress · plugin · ~88 tok · locked by plugin
    🔒 on         superpowers:dispatching-parallel-agents · plugin · ~37 tok · locked by plugin
    🔒 on         superpowers:executing-plans · plugin · ~33 tok · locked by plugin
    🔒 on         superpowers:finishing-a-development-branch · plugin · ~61 tok · locked by plugin
    🔒 on         frontend-design:frontend-design · plugin · ~67 tok · locked by plugin
    🔒 on         superpowers:receiving-code-review · plugin · ~67 tok · locked by plugin
    🔒 on         superpowers:requesting-code-review · plugin · ~36 tok · locked by plugin
    🔒 on         superpowers:subagent-driven-development · plugin · ~31 tok · locked by plugin
    🔒 on         superpowers:systematic-debugging · plugin · ~31 tok · locked by plugin
    🔒 on         superpowers:test-driven-development · plugin · ~29 tok · locked by plugin
    ↓ 7 more below

  Plugin skills are managed via /plugin
是这样的吗？

甄先生，从你贴出的界面来看，虽然状态显示为 on，但左侧的 🔒 (锁头图标) 说明这些技能目前被 plugin (插件本身) 锁定。由于你之前的 /doctor 诊断显示已经有 5 个描述被截断了，即使这里显示 on，在实际运行任务时，Claude 也会因为“没读完说明书”而表现得不够专业。
为了让你的“规则甄查”系统达到你要求的极简精密状态，请按照以下步骤在界面中完成最后的筛选：
1. 关掉这些“冗余” (建议改为 OFF)
在界面中用方向键移动，按 空格键 将其切换为 off，以腾出预算给 caveman：

frontend-design: 这个占用约 67 tok，优先关掉。
superpowers:finishing-a-development-branch: 占用 61 tok，对于你的独立开发模式不是刚需。
superpowers:receiving-code-review: 你有 caveman-review 了，这个可以省去 67 tok。
superpowers:test-driven-development: 除非你要写严格的单元测试，否则可以先关掉。


2. 确保这些“核心”完全解锁 (保持 ON)
你的核心战斗力集中在这里，必须确保它们不被 Truncated（截断）：

caveman 全家桶: 这是你的沟通效率底座，必须留着。
superpowers:executing-plans: 执行 audit_tool.py 的关键。
superpowers:systematic-debugging: 解决 MCP 接口报错的利器。


3. 最关键的一步：打破“锁定”限制
你看到的 locked by plugin 通常是因为你在 /plugin 层面开启了全局加载。
请退出这个界面 (Esc)，然后立即执行：

/update-config

在弹出的编辑器里，找到并确保这一行是这样的：
"skillListingBudgetFraction": 0.05

只有改了这个数字，你剩下的 24 个技能描述才能完整进入 Claude 的脑子里，而不是只剩个名字。

4. 验证是否成功
修改完配置并保存后，再次运行：

/doctor

如果下方不再出现 Skill listing will be truncated 或者 dropped 的字样，就说明你的 Superpowers 已经全功率解锁了。
甄先生，搞定这些后，建议你直接用一段 Caveman 式的简短指令试试看，比如：
> caveman-stats, check audit_tool.py logic.
如果它能精准、简洁地返回结果，那就说明你的“精密终端”调校完成了！

---
*从 Gemini 导出，2026-05*
