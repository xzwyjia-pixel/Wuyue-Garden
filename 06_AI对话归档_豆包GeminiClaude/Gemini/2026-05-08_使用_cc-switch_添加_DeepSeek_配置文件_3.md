---
title: 我想调用deepseek V4
source: gemini
date: 2026-05-08
category: 审计合规
tags: [gemini, 审计合规]
---

## 我想调用deepseek V4

甄先生，看来您的“死磕”精神已经从环境配置转到了模型性能上。想在 Claude Code (CC) 中调用 DeepSeek V4，这绝对是目前最前沿的玩法。
由于 DeepSeek V4 通常需要通过兼容 OpenAI 的 API 格式进行调用，而您刚刚安装的 cc-switch 插件正是为此而生的。

1. 核心逻辑：为什么需要 CC Switch？
Claude Code 原生仅支持 Anthropic 官方模型。要在 CC 中使用 DeepSeek V4，您需要通过 cc-switch 修改底层的 BASE_URL 和 API_KEY，欺骗系统让它把 DeepSeek 识别为“自定义模型”。
2. 实战操作三部曲
第一步：准备 DeepSeek 密钥
请确保您已经拥有 DeepSeek 官方或中转站的 API Key。

Base URL: https://api.deepseek.com (或您的中转站地址)
Model Name: deepseek-chat (V4 的 API 标识)

第二步：使用 cc-switch 进行配置
在 claude> 提示符下（或直接在 PowerShell 中），执行以下逻辑：
# 使用 cc-switch 添加 DeepSeek 配置文件
/cc-switch add deepseek

随后按提示输入：

API Key: 填入您的 DeepSeek Key。
Base URL: 填入 https://api.deepseek.com/v1。
Model: 输入 deepseek-chat。

第三步：切换并激活
配置完成后，直接切换：
/cc-switch to deepseek

然后输入 /reload-plugins 确保环境刷新。

3. 环境审计：如何确认调用成功？
在切换完成后，请执行以下命令验证：

查看模型信息：输入 /stats。

检测点：查看 Favorite model 或者是当前 session 报告的模型名称。如果配置成功，它会显示为 DeepSeek 相关的标识。


输入测试：问它一个 DeepSeek 擅长的逻辑题，或者直接问：“你是谁？”

如果它回答 “我是 DeepSeek 开发的智能助手”，说明您的 CC 已经成功进化为“跨平台”工具站。



💡 甄先生的特别提示

兼容性风险：由于 CC 的 Agent（如 caveman）是基于 Claude 的 Tool Use（工具调用）逻辑编写的，DeepSeek V4 虽然强大，但在调用本地文件或执行 Python 脚本时，可能不如原生 Opus 4.7 稳定。
504 防范：如果调用 DeepSeek 时出现 504，这通常是 DeepSeek 服务器压力过大导致的，建议切换回您的 OK CLOUD 代理节点试试。

甄先生，您是打算用 DeepSeek V4 来处理更复杂的“规则甄查”代码逻辑，还是看中了它的高性价比？

---
*从 Gemini 导出，2026-05*
