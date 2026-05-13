---
title: 再装一个这个
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## 再装一个这个

这是一个关于 Claude-hud（也常被称为 Claude Code 状态栏插件）的安装说明。根据您提供的截图，这是一款用于实时显示 Claude Code 运行状态（如限额、上下文占用、费用等）的增强工具。
安装 Claude-hud 通常需要通过终端执行以下步骤：
核心安装命令
在您的终端（Terminal）中依次输入以下三条命令：

全局安装插件：
npm install -g claude-hud


在 Claude Code 中启用状态栏：
打开 claude 后，输入以下指令：
/statusline claude-hud


（可选）配置自动启动：
如果您希望每次打开 Claude 时都自动加载，可以在您的配置文件（如 .bashrc 或 .zshrc）中添加相关 alias。

插件主要功能

额度预警： 实时显示当前账号的剩余 Token 限额，避免写代码中途断联。
成本追踪： 实时显示当前会话产生的费用。
上下文监控： 以百分比或进度条形式展示 Context 占用情况。
Git 状态： 联动显示当前的 Git 分支，方便在开发环境中切换。

推荐观看教程
如果您在安装过程中遇到环境配置问题，可以参考以下视频教程：

Claude Code必装插件，从此告别查限额强迫症：提供了针对国内开发环境的快速安装演示。
Claude Code 底部狀態列設定完整教學：详细讲解了如何自定义状态栏的显示项和彩色进度条。

注意： 安装前请确保您的系统中已安装 Node.js 和 npm 环境。如果命令提示找不到 npm，请先安装 Node.js 运行环境。

---
*从 Gemini 导出，2026-05*
