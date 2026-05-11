---
title: PS C:\Windows\System32> /update-config skillListingBudgetFraction 0.05 && /init
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## PS C:\Windows\System32> /update-config skillListingBudgetFraction 0.05 && /init

## PS C:\Windows\System32> /update-config skillListingBudgetFraction 0.05 && /init
/update-config: The term '/update-config' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32>

甄先生，抱歉！这是我的疏忽。刚才我提供的命令是 Claude Code 内部指令，你应该在 Claude 的 对话输入框（即出现 > 符号的地方）输入，而不是直接在 Windows 的 PowerShell (PS) 终端里运行。
在 PowerShell 层面，系统并不认识 / 开头的斜杠命令。
请按照以下步骤操作：
1. 首先，在你的 PowerShell 中启动 Claude：
（如果你已经处于对话状态，请忽略这一步）
claude

2. 进入 Claude 的对话界面后，在 > 提示符下输入：
直接复制粘贴下面这一行：

/update-config

3. 在弹出的交互式配置中进行修改：

Claude 会弹出一个 JSON 编辑器或配置列表。
找到 "skillListingBudgetFraction": 0.01。
将其手动修改为 0.05。
按下 Ctrl + S 保存，然后按 Enter 确认（根据终端提示操作）。


如果你想让它“自己执行”逻辑
在 Claude 的对话框 > 之后，直接对它说一句话即可：

“请帮我修改配置，将 skillListingBudgetFraction 设置为 0.05，然后运行 /init 重新加载我的 CLAUDE.md。”

⚠️ 甄先生，还有一个关键细节：
你现在的路径是 C:\Windows\System32，这非常危险且不利于项目管理。
建议你先进入你的项目文件夹：
cd D:\你的项目路径\Rules_Investigation  # 替换成你实际的代码存放地
claude

这样 Claude 才能通过 CLAUDE.md 识别出你是“甄先生”，并自动加载你那套极简精密的技能配置。需要我帮你写一个快速切换目录并启动的批处理脚本吗？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
