---
title: 我指的是在Claude code上装superpower
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## 我指的是在Claude code上装superpower

在 Claude Code 中安装 Superpowers（通常指的是由 obra 开发的 Superpowers 框架），并不是安装一个传统的浏览器插件，而是通过命令将其注入到 Claude Code 的工作流中。
这个框架能为 Claude Code 提供 14 种结构化技能（如 TDD 测试驱动开发、自动代码审查、系统化 Debug 等）。
安装方法
根据 2026 年最新的官方指南，你可以通过以下两种方式安装：
1. 一键快捷安装（推荐）
在你的终端（Terminal）中直接运行以下命令：
/plugin install superpowers@claude-plugins-official

注意：这需要在 Claude Code 的交互界面内执行。
2. 通过 GitHub 源码手动安装
如果你需要更灵活的配置，或者想要尝试开发者版本：

克隆仓库：
git clone https://github.com/obra/superpowers.git ~/.claude/plugins/superpowers


在 Claude Code 中注册：
打开 Claude Code 后，告知它加载该插件路径，或者在项目的 CLAUDE.md 文件中引用该框架。


安装后的核心变化
安装成功后，你不需要手动去“开启”它，它会自动拦截你的指令并进入 “Agentic 模式”：

头脑风暴阶段： 在写代码前，它会强制进行需求对齐，生成设计文档。
任务拆解： 它会将复杂的任务拆成 2-5 分钟就能完成的小模块。
铁律 (The Iron Law)： 强制要求“先写失败的测试，再写实现代码”，确保代码质量。
双重审查： 自动调用子代理（Sub-agents）进行规格一致性检查和代码质量检查。

💡 进阶提示：Superpowers Chrome 扩展
如果你还需要 Claude Code 能够 直接控制浏览器（例如自动测试网页 UI、爬取数据），你可能还需要安装它的配套工具：
npx superpowers-chrome start

这会启动一个基于 MCP（Model Context Protocol）的服务，让 Claude Code 获得操作 Chrome 的“超能力”。
你是准备在某个具体项目中使用它的 TDD 模式，还是主要想用它的自动 Debug 功能？

---
*从 Gemini 导出，2026-05*
