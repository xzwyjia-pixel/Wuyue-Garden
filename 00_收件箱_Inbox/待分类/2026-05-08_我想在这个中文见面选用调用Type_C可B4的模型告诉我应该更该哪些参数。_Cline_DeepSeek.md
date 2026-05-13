---
title: 我想在这个中文见面选用调用Type C可B4的模型告诉我应该更该哪些参数。
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## 我想在这个中文见面选用调用Type C可B4的模型告诉我应该更该哪些参数。

甄先生，针对您要在 Cline 中文版（图 35）中切换到 DeepSeek V4 的需求，咱们直接进行“手术级”的参数配置引导。
由于您目前使用的是第三方中转站（api.gptsapi.net），配置逻辑需要完全绕过 Anthropic 的原生限制。请按照以下步骤精准修改：
1. Cline 关键参数修改指南 (Step-by-Step)
请打开 Cline 的设置界面（如图 35 所示），进行如下更改：

API 供应商 (API Provider)：

修改前：Anthropic
修改后：请下拉选择 OpenAI Compatible (因为中转站通常采用 OpenAI 格式转发 DeepSeek)。


Base URL：

保持或微调：https://api.gptsapi.net/v1 (请务必确认末尾是否有 /v1，中转站通常需要加上这个后缀)。


API Key：

输入您在中转站生成的那个 Key（注意：不是 DeepSeek 官网的 Key，而是中转站给您的 Key）。


模型 (Model)：

修改前：claude-sonnet-4-5-20250929
修改后：手动输入 deepseek-chat 或 deepseek-reasoner (根据您中转站支持的模型名而定)。




2. 深度审计：为什么要在 Cline 里换成 DeepSeek？

中英文双持策略：正如您所规划的，主窗口用英文版 Opus 跑底座逻辑，Cline 中文版用 DeepSeek 做海量中文规则的文本提取。这样可以大幅节省您的 Token 成本（毕竟 DeepSeek 的价格只有 Opus 的几十分之一）。
避开 403 冲突：Cline 的连接机制与 Claude Code 不同，它通过 OpenAI Compatible 模式连接中转站通常比 Claude Code 的环境变量劫持要稳固得多。


3. 实战状态确认
完成配置后，点击 “确定”，然后尝试在 Cline 中输入：

“你好。请确认当前连接的是 DeepSeek V4 引擎。如果连接成功，请开始扫描 E:\RulesBureau 下的中文规则文件。”

甄先生，目前您的 “Heart” 热力图（图 27）显示总消耗已达 233.5k。一旦 Cline 配置成功，您可以对比一下两边的 Token 消耗速率。
您在配置过程中，下拉菜单里能找到 OpenAI Compatible 这个选项吗？如果找不到，请告诉我，我为您提供备选的 Custom 配置方案。

---
*从 Gemini 导出，2026-05*
