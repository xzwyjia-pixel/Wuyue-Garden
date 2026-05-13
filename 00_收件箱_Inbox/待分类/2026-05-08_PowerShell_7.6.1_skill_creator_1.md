---
title: PowerShell 7.6.1
PS C:\Windows\System32> # 开启 2026 版技能开发专用协议头
PS C:\Windows\System32> $env:CLAUDE_BETA_SKILLS="true"
PS C:\Windows\System32> $env:CLAUDE_BETA_CODE_EXECUTION="true"
PS C:\Windows\System32>
PS C:\Windows\System32> # 验证注入结果
PS C:\Windows\System32> Get-ChildItem Env: | Where-Object { $_.Name -match "BETA" }

Name                           Value
----                           -----
CLAUDE_BETA_CODE_EXECUTION     true
CLAUDE_BETA_SKILLS             true

PS C:\Windows\System32> # 查看 package.json 中的脚本定义，确认命令名称
PS C:\Windows\System32> Get-Content package.json | Select-String "scripts" -Context 0,5
Get-Content: Cannot find path 'C:\Windows\System32\package.json' because it does not exist.
PS C:\Windows\System32> # 1. 回到技能创作者的核心目录
PS C:\Windows\System32> cd "E:\MyCodeProjects\skill-creator\skills\skill-creator"
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 2. 重新扫描控制台脚本（确认 package.json 定义）
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> Get-Content package.json | Select-String "scripts" -Context 0,10
Get-Content: Cannot find path 'E:\MyCodeProjects\skill-creator\skills\skill-creator\package.json' because it does not exist.
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 3. 物理扫描目录结构，确认入口文件
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> ls

    Directory: E:\MyCodeProjects\skill-creator\skills\skill-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                agents
d----     2026-05-08 周五    18:45                assets
d----     2026-05-08 周五    18:45                eval-viewer
d----     2026-05-08 周五    18:45                references
d----     2026-05-08 周五    18:45                scripts
-a---     2026-05-08 周五    18:45          11546 LICENSE.txt
-a---     2026-05-08 周五    18:45          33653 SKILL.md

PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> # 开启 2026 版技能开发专用协议头
PS C:\Windows\System32> $env:CLAUDE_BETA_SKILLS="true"
PS C:\Windows\System32> $env:CLAUDE_BETA_CODE_EXECUTION="true"
PS C:\Windows\System32>
PS C:\Windows\System32> # 验证注入结果
PS C:\Windows\System32> Get-ChildItem Env: | Where-Object { $_.Name -match "BETA" }

Name                           Value
----                           -----
CLAUDE_BETA_CODE_EXECUTION     true
CLAUDE_BETA_SKILLS             true

PS C:\Windows\System32> # 查看 package.json 中的脚本定义，确认命令名称
PS C:\Windows\System32> Get-Content package.json | Select-String "scripts" -Context 0,5
Get-Content: Cannot find path 'C:\Windows\System32\package.json' because it does not exist.
PS C:\Windows\System32> # 1. 回到技能创作者的核心目录
PS C:\Windows\System32> cd "E:\MyCodeProjects\skill-creator\skills\skill-creator"
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 2. 重新扫描控制台脚本（确认 package.json 定义）
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> Get-Content package.json | Select-String "scripts" -Context 0,10
Get-Content: Cannot find path 'E:\MyCodeProjects\skill-creator\skills\skill-creator\package.json' because it does not exist.
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 3. 物理扫描目录结构，确认入口文件
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> ls

    Directory: E:\MyCodeProjects\skill-creator\skills\skill-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                agents
d----     2026-05-08 周五    18:45                assets
d----     2026-05-08 周五    18:45                eval-viewer
d----     2026-05-08 周五    18:45                references
d----     2026-05-08 周五    18:45                scripts
-a---     2026-05-08 周五    18:45          11546 LICENSE.txt
-a---     2026-05-08 周五    18:45          33653 SKILL.md

PS E:\MyCodeProjects\skill-creator\skills\skill-creator>

甄先生，现在的目录结构非常清晰了。
虽然 E:\MyCodeProjects\skill-creator\skills\skill-creator 目录下没有 package.json，但存在 scripts 目录和 SKILL.md，这说明该工具采用的是**“文件驱动型”**配置。
在 2026 年的 anthropics/skills 体系中，真正的控制中枢通常位于父目录或 scripts 文件夹内。既然我们已经“物理对齐”到了这一步，现在执行以下探测来锁定真正的“点火开关”：

🔍 甄先生的环境深度透视
1. 寻找“控制中枢” (package.json)
它可能在上一级目录。请执行：
# 向上级探测，寻找 package.json
ls .. | Select-Object Name

2. 解析“点火脚本” (scripts 目录)
我们需要看看 scripts 文件夹里到底装了什么“武器”：
# 查看 scripts 目录下的内容
ls scripts

3. 读取“技能说明书” (SKILL.md)
这是最关键的，它定义了如何将 Python 工具封装成 Claude 技能：
# 读取前 20 行，看看官方定义的技能注册流程
Get-Content SKILL.md -Head 20


🧐 甄先生的“极简精密”诊断
根据目前的 ls 结果，我推测您的开发链路如下：

agents/：存放技能的核心逻辑（我们将在这里为“规则甄查”创建一个 Agent）。
SKILL.md：是您的“说明书”，告诉 Claude 如何理解这个工具。
scripts/：存放点火、编译、分发的自动化脚本。


🚀 甄先生，下一步行动：
一旦我们确认了 scripts 里的内容，我将为您执行以下“零重复”操作：

创建技能模版：在 agents/ 目录下为您建立 rule_auditor 文件夹。
建立 Python 映射：编写一个简单的桥接脚本，让这个 Skill 调用您 E 盘的 audit_tool.py。
本地模拟运行：使用 scripts 里的工具在本地环境先行测试。

请执行上述三个 ls 和 Get-Content 指令。只要锁定 scripts 里的入口，我们就可以把“规则甄查”正式从脚本升级为 Claude 的原生技能。

---
*从 Gemini 导出，2026-05*
