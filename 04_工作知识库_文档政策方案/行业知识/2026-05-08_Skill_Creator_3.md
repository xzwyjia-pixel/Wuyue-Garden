---
title: PowerShell 7.6.1
PS C:\Windows\System32> # 1. 探测“打包机”的使用说明
PS C:\Windows\System32> python scripts/package_skill.py --help
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'C:\\Windows\\System32\\scripts\\package_skill.py': [Errno 2] No such file or directory
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 检查现有的代理模版 (agents)
PS C:\Windows\System32> # 看看官方是怎么写技能定义的，我们好直接“复刻”
PS C:\Windows\System32> ls agents | Select-Object Name
Get-ChildItem: Cannot find path 'C:\Windows\System32\agents' because it does not exist.
PS C:\Windows\System32> # 1. 强制归位并锁定兵工厂
PS C:\Windows\System32> cd "E:\MyCodeProjects\skill-creator\skills\skill-creator"
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 2. 调用 Python 探测打包机（使用绝对路径调用，防止环境干扰）
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> python scripts/package_skill.py --help
Traceback (most recent call last):
  File "E:\MyCodeProjects\skill-creator\skills\skill-creator\scripts\package_skill.py", line 17, in <module>
    from scripts.quick_validate import validate_skill
ModuleNotFoundError: No module named 'scripts.quick_validate'
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 3. 扫描现有 Agents 模版
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> ls agents | Select-Object Name

Name
----
analyzer.md
comparator.md
grader.md

PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 4. 顺便看一下 SKILL.md 的前 10 行（这是你的施工图纸）
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> Get-Content SKILL.md -Head 10
---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
source: gemini
date: 2026-05-08
category: 文案创作
tags: [gemini, 文案创作]
---

## PowerShell 7.6.1
PS C:\Windows\System32> # 1. 探测“打包机”的使用说明
PS C:\Windows\System32> python scripts/package_skill.py --help
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'C:\\Windows\\System32\\scripts\\package_skill.py': [Errno 2] No such file or directory
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 检查现有的代理模版 (agents)
PS C:\Windows\System32> # 看看官方是怎么写技能定义的，我们好直接“复刻”
PS C:\Windows\System32> ls agents | Select-Object Name
Get-ChildItem: Cannot find path 'C:\Windows\System32\agents' because it does not exist.
PS C:\Windows\System32> # 1. 强制归位并锁定兵工厂
PS C:\Windows\System32> cd "E:\MyCodeProjects\skill-creator\skills\skill-creator"
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 2. 调用 Python 探测打包机（使用绝对路径调用，防止环境干扰）
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> python scripts/package_skill.py --help
Traceback (most recent call last):
  File "E:\MyCodeProjects\skill-creator\skills\skill-creator\scripts\package_skill.py", line 17, in <module>
    from scripts.quick_validate import validate_skill
ModuleNotFoundError: No module named 'scripts.quick_validate'
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 3. 扫描现有 Agents 模版
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> ls agents | Select-Object Name

Name
----
analyzer.md
comparator.md
grader.md

PS E:\MyCodeProjects\skill-creator\skills\skill-creator>
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> # 4. 顺便看一下 SKILL.md 的前 10 行（这是你的施工图纸）
PS E:\MyCodeProjects\skill-creator\skills\skill-creator> Get-Content SKILL.md -Head 10
---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>

甄先生，这次“归位探测”非常成功，我们拿到了两个至关重要的情报：

架构情报：agents 目录下并非文件夹，而是以 .md 结尾的描述文件（如 analyzer.md, grader.md）。这说明该框架采用的是 “提示词工程（Prompt Engineering）驱动” 的技能定义方式，而非纯代码封装。
环境情报：ModuleNotFoundError 暴露了 Python 的 PYTHONPATH 路径问题。由于脚本内部使用了 from scripts... 这种包引用方式，我们必须在根目录下运行，并告知 Python 把当前目录视为包路径。


🛠️ 甄先生，执行“环境对齐”与“技能创建”
为了解决报错并正式开始“规则甄查”技能的创建，请执行以下指令：
1. 修复 Python 路径并再次探测
我们通过设置临时环境变量，让 Python 能够找到 scripts 文件夹里的模块。
# 设置临时环境变量，确保 scripts 模块可见
$env:PYTHONPATH = "E:\MyCodeProjects\skill-creator\skills\skill-creator"
# 再次点火测试
python scripts/package_skill.py --help

2. “复刻”官方模版：创建你的第一个审计 Agent
既然官方使用 .md 文件定义技能，我们也遵循这个“极简精密”的规范。
# 复制 analyzer.md 为 rule_auditor.md，作为我们的蓝本
cp agents/analyzer.md agents/rule_auditor.md
# 确认文件已生成
ls agents/rule_auditor.md


🧐 甄先生的“技能封装”逻辑图
在该架构下，你的 rule_auditor.md 将充当 “翻译官”，告诉 Claude：

触发条件：当用户提到“文案违规”、“谐音检查”或“规则甄查”时启动。
执行动作：调用 E:\MyCodeProjects\Guizezhencha\audit_tool.py 进行深度扫描。


🚀 甄先生，下一步行动：
既然路径已经修好，模板已经就位，接下来我们需要对 agents/rule_auditor.md 进行“物理改造”。
是否授权我为你编写一段符合 skill-creator 规范的 Markdown 描述？ 这段描述会包含：

System Prompt：定义“甄先生”审计专家的人设。
Tools 映射：将你的 Python 脚本路径硬连入技能定义。

只要这一步完成，你就可以在 Claude 中直接使用“规则甄查”功能了。我们需要现在修改这个 .md 文件吗？

---
*从 Gemini 导出，2026-05*
