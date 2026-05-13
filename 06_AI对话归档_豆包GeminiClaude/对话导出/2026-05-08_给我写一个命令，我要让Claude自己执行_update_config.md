---
title: 给我写一个命令，我要让Claude自己执行
source: gemini
date: 2026-05-08
category: 其他
tags: [gemini, 其他]
---

## 给我写一个命令，我要让Claude自己执行

既然我们要让 Claude Code 自动完成上述的所有优化，你只需要在终端（Terminal）粘贴并执行这一条指令。它会利用 update-config 技能直接修改底层预算，并让 Claude 立即重构环境：
/update-config skillListingBudgetFraction 0.05 && /init


这条命令执行了什么？

/update-config skillListingBudgetFraction 0.05:
这是最关键的一步。它直接把技能描述的 Token 预算从 1% 提升到 5%。这会立刻找回你之前丢失的那 5 个 superpowers 详细描述。
&& /init:
在修改完预算后，立即触发初始化。它会扫描你刚才建立的 CLAUDE.md，并将 Caveman 模式和 Rules Investigation 的项目上下文深度挂载到当前会话中。


执行后的下一步：
执行完这条命令后，直接给它一个 Caveman 式的指令来验证是否“调教”成功：

caveman-stats, check skill status.

如果它给出的回复极简、没有废话，且没有提示 "dropped skills"，说明你的极简精密终端已经完全解锁。

---
*从 Gemini 导出，2026-05*
