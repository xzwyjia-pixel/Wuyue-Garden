---
title: https://gptsapi.net/models网页打不开
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: API集成
old_category: Claude/MCP
tags: [gemini, 技术开发, API集成]
---

## https://gptsapi.net/models网页打不开

## https://gptsapi.net/models网页打不开

甄先生，网页打不开说明这个供应商的文档可能藏得比较深。既然“盲试” ID 总是报红，我们要用最硬核的 “审计日志法”，直接逼 Claude 把中转商要求的暗号吐出来。
请在 Claude Code 界面直接输入以下指令（不带 /run，因为现在权限被锁，我们只做逻辑探测）：

**“我是甄先生。握手失败，请自查并告诉我：

你当前尝试请求的 model 完整字符串是什么？
供应商返回的 404 或 400 错误信息里，是否提到了‘Model not found’或者‘Available models’？
请直接把报错原文发给我。”**



甄先生的精密“暗号”猜测
如果 claude-3-5-sonnet 不行，根据此类中转商的惯例，请您先退出 Claude，尝试这个最简化的**“暗号”**启动：
# 某些 API 聚合商会强制要求这个特定 ID
claude --model claude-3-5-sonnet-20240620


如果红点依然存在（Plan B）：
我们要去物理检查它的通信日志。请在资源管理器中打开这个路径：
%APPDATA%\claude-code\logs\
找一份最新的 .log 文件，搜索 404 或 model。

甄先生，日志里通常会写： The model 'xxx' is not available for this key. Available models: yyy, zzz...
找到那个 yyy，它就是我们要的真暗号。


💡 甄先生的审计提示：
只要红点在，我们的 Caveman 和 Superpowers 就无法“点火”。
甄先生，日志里有没有提到类似 claude-3-5-sonnet-v2-20241022 这种更长的名字？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / API集成 · 2026-05-08*
