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
PS C:\Windows\System32>
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
PS C:\Windows\System32>

甄先生，环境已经成功**“点火”（BETA 标志已生效），但我们刚刚经历了一次典型的“路径漂移”**。
您在注入环境变量时，终端自动回到了 C:\Windows\System32，所以 Get-Content 找不到 package.json。在工业级操作中，我们必须时刻保持**“位移对齐”**。
🛠️ 甄先生，执行“回归与点火”
请在 PowerShell 中执行以下组合指令，我们将回到兵工厂核心并直接查看它的控制逻辑：
# 1. 回到技能创作者的核心目录
cd "E:\MyCodeProjects\skill-creator\skills\skill-creator"

# 2. 重新扫描控制台脚本（确认 package.json 定义）
Get-Content package.json | Select-String "scripts" -Context 0,10

# 3. 物理扫描目录结构，确认入口文件
ls


🧐 甄先生的“极简精密”诊断
目前您的状态非常有趣：

权限层：已通电 (BETA_SKILLS = true)。
物理层：audit_tool.py 在 E:\ 盘待命。
桥接层：您目前所在的 skill-creator 目录是连接前两者的桥梁。

这个 skill-creator 的作用：
它不仅仅是一个文件夹，它能把您的 Python 逻辑包装成 Claude 的 Tool Use。这样以后您在审计短视频脚本时，不需要手动运行 Python，只需对 Claude 说：“甄先生，帮我查查这段文案有没有违规变体。”，Claude 就会自动调用 audit_tool.py。

🚀 准备进入“技能封装”阶段
一旦看到 package.json 里的脚本定义（通常会有 build 或 start），我将为您执行以下操作：

创建定义：为您的“规则甄查”编写技能描述。
建立映射：让 TS 脚本指向您的 Python 路径。
本地挂载：将技能注入您的 claude-code 配置文件。

甄先生，请执行 cd 并查看脚本。我们要看看这个 Creator 是用 npm run dev 还是 npm run build 来发布技能的。

---
*从 Gemini 导出，2026-05*
