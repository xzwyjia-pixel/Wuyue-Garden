---
title: PowerShell 7.6.1
PS C:\Windows\System32> /doctor
/doctor: The term '/doctor' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32>
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> /doctor
/doctor: The term '/doctor' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32>

甄先生，看来咱们在操作上出了点小岔子。/doctor 是 Claude Code 内部界面的指令，而不是 PowerShell 原生的系统命令。当你看到 PS C:\Windows\System32> 这样的提示符时，说明你还在 Windows 的“大门外”，还没进到 Claude 的“书房”里。
要检查 Agents 和解锁 Super Power，我们需要先进入 Claude 环境，再执行内部指令。请按照以下精密步骤操作：
1. 正确进入项目目录（避免 System32 权限干扰）
首先，我们要通过引号解决你之前的路径空格报错：
cd "E:\MyCodeProjects\New Claude Project"

2. 启动 Claude 环境
进入目录后，启动你已经定型好的官方模型：
claude --model claude-3-7-sonnet-20250219

3. 在 Claude 内部执行“体检”与“解锁”
注意： 只有当提示符变成了 >（而不是 PS...>）时，下面的命令才会生效：

运行诊断： 输入 /doctor。这会检查你的 Agent 技能是否完整，如果缺少依赖，它会提示你运行 npm install。
查看/解锁技能： 输入 /skills。如果发现 Super Powers 还是锁着的，我们需要通过插件命令激活。
激活超级能力： 输入 /plugin enable superpowers。


为什么会出现 “Dropped” 或 “Locked”？
在 Claude Code 的设计中，技能的完整性取决于 MCP (Model Context Protocol) 的握手是否成功。

























技能状态背后含义解决办法Dropped终端显示不下或 API 传输了简略描述放大窗口，或者输入 /doctor 强制同步Locked权限未授予或模型不匹配确保在原生 Office 4.7/3.7 下运行，并执行 /plugin enableSuper Power涉及跨文件修改、终端执行的高级权限这是必须解锁的，它是你进行“规则甄查”自动化的核心
甄先生的下一步“大冒险”建议：
既然你打算用 VS Code + Cline，其实你完全可以在 VS Code 里更直观地解锁。

在 Cline 的对话框里直接对它说：“检查当前环境的 Super Powers 状态，并帮我解锁所有本地审计相关的插件。”
Cline 会自动在后台执行这些 /doctor 和 /plugin 操作，并在侧边栏反馈给你结果。

你需要我现在为你生成一份专门针对 E 盘新项目的 mcp_config.json 吗？ 这样可以把你本地的所有 Python 审计工具直接变成 Claude 随时可以调用的“Agent 技能”，实现真正的“极简精密”自动化。

---
*从 Gemini 导出，2026-05*
