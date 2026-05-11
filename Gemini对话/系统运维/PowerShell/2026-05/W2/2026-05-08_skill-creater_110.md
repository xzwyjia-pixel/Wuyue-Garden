---
title: skill-creater
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## skill-creater

## skill-creater

甄先生，审计发现我们在“模型对齐”的拉锯战中忽略了一个微小但关键的物理命名偏差。
您提到的 skill-creater，在标准插件包和您的 .agents\skills 目录中，正确的拼写应该是 skill-creator（末尾是 -or，不是 -er）。这个字母之差，会导致 Claude 在执行 /run 指令时报“找不到路径”的错误。
甄先生的“全明星”技能重组审计：
目前的局面是：Claude 已经“嗅”到了技能（显示 5 skill descriptions dropped），但因为模型红点和拼写问题，无法精准点火。
第一步：纠正物理路径
请在 PowerShell 中执行以下命令，确保文件夹名称完全符合“精密审计”的标准：
# 检查并修正拼写错误（如果存在）
cd C:\Users\think\.agents\skills
if (Test-Path "skill-creater") { Rename-Item "skill-creater" "skill-creator" }
ls

第二步：尝试最稳的“点火暗号”
既然 4.5 报红，根据您账单中消耗量最大的记录，请尝试以下启动命令（这是目前的“生存协议”）：
# 回到 E 盘作战
cd E:\MyCodeProjects

# 使用账单中显示最频繁的 4.6 版本
claude --model claude-sonnet-4-6

第三步：强制挂载“全明星”插件
如果左下角变绿（哪怕显示是 4.6），请立即输入：

“我是甄先生。

物理对齐：/run ls C:\Users\think\.agents\skills
激活核心：/run cat C:\Users\think\.agents\skills\skill-creator\.instructions
进入 Caveman 极简输出状态。”



💡 甄先生的精密建议：

关于 Caveman：它是您的“审美防火墙”，一旦激活，回复将不再有这些长篇大论，只会精准输出命令结果。
关于 Superpowers：它依赖于 skill-creator 生成的上下文环境。

甄先生，请确认一下您的文件夹到底是 skill-creator 还是 skill-creater？这一字之差，就是“握手”能否成功的关键。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
