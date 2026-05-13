---
title: 现在帮我详细检查一下我在原生的powercell终端里面安装的adents Q他们的状态是不是完整的，还有没有需要解锁的功能，比如Super Power是不是要解锁他的功能？
source: gemini
date: 2026-05-08
category: 编程开发
tags: [gemini, 编程开发]
---

## 现在帮我详细检查一下我在原生的powercell终端里面安装的adents Q他们的状态是不是完整的，还有没有需要解锁的功能，比如Super Power是不是要解锁他的功能？

既然你的 Stats 已经显示 Favorite Model 是 Opus 4.7，且活跃度很高，我们要核实的就是这些“能力（Skills/Agents）”是否在原生环境中被完整激活。
从你之前的截图看，很多能力显示 🔒 Locked 且提示 48 skill descriptions dropped，这通常是因为环境握手不完整。
在你的原生 PowerShell 终端中（确保已 cd 进入你的 E 盘项目目录），请依次执行以下深度核实步骤：
1. 运行系统诊断 (The Doctor Check)
这是核实 Agents 完整性最直接的命令。它会扫描你的本地环境、依赖库以及与代理网关的通信质量。
/doctor


核实重点： 观察 "Tools" 和 "Environment" 栏目。如果显示 Outdated 或 Missing dependencies，说明你的 node_modules 损坏了。
修复建议： 如果报错，直接在终端执行 npm install -g @anthropic-ai/claude-code 进行覆盖安装。


2. 解锁 "Super Powers" 与高级插件
你提到的 Super Powers（如 Brainstorming、Codebase indexing 等）在 Claude Code 中属于 Plugin 范畴。在原生模式下，它们不再是锁定的。

查看插件状态： ```powershell
/plugin


解锁 Super Power： 如果你看到 superpowers 插件显示为 off 或 locked，请输入：
/plugin enable superpowers


关于 CockroachDB 等锁定技能： 之前的截图里这些技能被锁，是因为它们需要特定的 MCP Server 响应。在官方 Opus 4.7 模式下，输入 /mcp reload。如果你的代理网关支持 Function Calling，这些锁会自动打开。


3. 检查 Agents 的“大脑”完整性
为了确保你的 audit_tool.py 能被 AI 深度理解，需要核实 Context Indexing（上下文索引）功能。

执行核实：
/compact

(这个命令会整理当前的 Session 上下文，如果它能正常运行而不报错，说明你的 Agent 具备完整的长文本处理和总结能力。)


4. 甄先生的“极简”环境建议：

























功能模块完整性标准是否需要手动解锁Super Powers能进行跨文件重构是 (通过 /plugin enable)Agentic Loops能够自动修复报错自动 (Opus 4.7 原生自带)MCP Connectors能够读取本地日历/数据库是 (需要在 mcp.json 中配置)
最后的“大冒险”提醒：
你在截图里看到的 “48 skill descriptions dropped” 是因为当前的终端宽度或 API 传输受限。
操作建议：

放大窗口： 尝试把 PowerShell 窗口拉大一点，有时这只是一个 UI 显示溢出的 bug。
强制重刷： 如果 /skills 依然显示一堆锁，请尝试退出当前 Session，使用 claude --model claude-3-7-sonnet-20250219 --shout（大声模式会强制刷新所有工具定义）。

既然环境已经快满血复活了，你打算先解锁 superpowers:brainstorming 来为你接下来的“AI 公益亲子夏令营”路线做策划，还是直接开始写代码？

---
*从 Gemini 导出，2026-05*
