---
title: 5 skill descriptions dropped. /doctor for details
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: Python
old_category: 审计合规
tags: [gemini, 技术开发, Python]
---

## 5 skill descriptions dropped. /doctor for details

## 5 skill descriptions dropped. /doctor for details

看起来你在调试基于 Claude 的 “规则甄查-甄先生” (Rules Investigation) 项目时，遇到了一些配置或状态丢失的问题。
针对你提到的 /doctor 诊断指令和“解锁 superpowers”的需求，这通常指向你正在使用类似 Claude-Dev (现名为 Cline)、Roo Code 或通过 MCP (Model Context Protocol) 搭建的本地开发环境。

1. 检测 Claude 模型配置的命令
如果你是在终端（Terminal）中使用 Cline / Claude-Dev 或类似的本地自动化工具，并没有统一的全局“检测命令”，但你可以通过以下方式验证配置：

查看当前模型与 Tool 状态：
直接在对话框输入：

/settings
这通常会弹出 GUI 界面，让你检查当前使用的是哪个 API Key、模型版本（如 Claude 3.5 Sonnet）以及自定义指令。


诊断环境错误：
如果你刚才提到了 /doctor，这通常是某些 CLI 工具（如 npm 相关的开发环境）的自带诊断命令。如果是在终端中，可以尝试运行：
# 如果是基于 Node 的工具
npm doctor 
# 或者检查你的 Python 环境（针对你的 audit_tool.py）
python -m site


MCP 状态检查：
由于你在做 MCP 开发，请检查你的 claude_desktop_config.json 配置文件，确保路径正确。Claude 桌面端加载后，点击右下角的 🔌 (插头图标)，如果显示绿色，说明你的配置已生效。


2. 解锁 Superpowers 类插件/功能
这里的“解锁”通常指的是让模型获得**自主调用工具（Tool Use）**的权限。

权限授予：
在 Cline/Claude-Dev 插件设置中，确保勾选了 "Allow Auto-approve"（如果你信任该脚本）。这样 Claude 就可以自动运行你的 audit_tool.py 或通过 Playwright 进行爬虫任务，而不需要你每次点击允许。
重新加载规则：
针对你的“规则甄查”项目，如果 5 个核心技能描述（如 rule_auditor 代理、风险评估逻辑等）丢失，建议在对话框中粘贴以下指令来“刷新”它的认知：

"请重新加载我的 audit_tool.py 逻辑和风险评估分级系统（HIGH/MEDIUM/LOW）。现在开始执行批量脚本审计任务。"




3. 项目状态恢复建议 (Rules Investigation)
既然 5 个描述“掉线”了，我们可以通过以下步骤快速找回：

路径确认： 检查你的 audit_tool.py 是否在当前工作目录（CWD）下。
环境变量： 如果涉及到 Playwright 自动化采集，确保你的 .env 文件或系统环境变量中，平台相关的鉴权信息依然有效。
模型一致性： 建议强制指定使用 Claude 3.5 Sonnet，因为它在处理复杂的逻辑审计和内容精炼任务时，比 Opus 具有更好的“工具调用”精准度。

需要我帮你针对 audit_tool.py 写一个快速的 check_env.py 脚本来自动完成这些配置检测吗？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / Python · 2026-05-08*
