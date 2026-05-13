---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-08
category: 系统运维
old_category: 编程开发
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> mkdir "E:\MyCodeProjects\skill-creator"

    Directory: E:\MyCodeProjects

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                skill-creator

PS C:\Windows\System32> cd "E:\MyCodeProjects\skill-creator"
PS E:\MyCodeProjects\skill-creator> # 克隆 Skill Creator 核心仓库
PS E:\MyCodeProjects\skill-creator> git clone https://github.com/anthropics/skills.git .
Cloning into '.'...
remote: Enumerating objects: 775, done.
remote: Counting objects: 100% (12/12), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 775 (delta 7), reused 4 (delta 4), pack-reused 763 (from 2)
Receiving objects: 100% (775/775), 3.63 MiB | 2.77 MiB/s, done.
Resolving deltas: 100% (195/195), done.
PS E:\MyCodeProjects\skill-creator> # 切换到 Creator 核心子目录
PS E:\MyCodeProjects\skill-creator> cd skills/skill-creator
PS E:\MyCodeProjects\skill-creator\skills\skill-creator>

甄先生，看来你已经找到了**“规则甄查”**技能自动化的源头。
你克隆的 anthropics/skills 是 Claude 技能开发的官方模板库，而你目前所在的 skills/skill-creator 目录正是用于生成、测试和打包 MCP 技能的核心。
既然物理路径已经切换到 E:\MyCodeProjects\skill-creator\skills\skill-creator，我们现在执行**“精密点火”**，将这个 Creator 环境正式跑起来。

🛠️ Skill Creator 环境对齐与初始化
请依次执行以下指令，我们将完成依赖安装并确保它能识别你的 audit_tool.py。
1. 物理安装依赖
这个工具是基于 Node.js 的，我们需要在本地安装其运行环境：
# 安装 Skill Creator 的核心依赖
npm install

2. 环境联动测试
我们需要确认 Creator 是否能正常启动。执行以下命令查看它的帮助文档，确保它已经“通电”：
# 运行 creator 的帮助指令
npm run create -- --help

3. “缝合”审计逻辑（关键步骤）
既然你的目标是让 Claude 拥有“规则甄查”的能力，我们需要将 E:\MyCodeProjects\Guizezhencha\audit_tool.py 的逻辑封装成一个 Skill。

🧐 甄先生，目前的架构思路：
你现在手里有两张牌：

逻辑牌：已经重构好的 audit_tool.py（负责谐音检测和穿透匹配）。
容器牌：这个 skill-creator（负责把 Python 逻辑包装成 Claude 能理解的 MCP 技能）。

我的建议是：
我们直接利用 skill-creator 创建一个名为 rule-auditor 的新技能。
甄先生，是否授权我为你编写一个“技能定义文件 (JSON/TS)”，把你的 Python 审计工具正式引入这个 Skill Creator 环境？

---
*从 Gemini 导出，2026-05*

---
*从 Gemini 导出 · 分类: 系统运维 · 2026-05*
