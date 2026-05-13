---
title: ✻ Brewed for 2s

> /model claude-3-5-sonnet-20241022
  ⎿  Model 'claude-3-5-sonnet-20241022' not found
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## ✻ Brewed for 2s

> /model claude-3-5-sonnet-20241022
  ⎿  Model 'claude-3-5-sonnet-20241022' not found

甄先生，看来咱们的通讯协议遇到了最典型的“翻译官”问题。在中转 API 环境下，服务端往往对模型名称进行了微调。
既然 claude-3-5-sonnet-20241022 无法直接识别，咱们用最原始、最精密的方法来锁定它。请在 > 提示符后执行：
1. 模型拨号审计
直接输入这个命令，看看您的中转供应商到底给这个模型起了什么名字：
/model

甄先生，请告诉我弹出的列表里有哪些选项？ (通常会是 claude-3-5-sonnet 或者简单的 sonnet-3.5)

2. 备选方案：强制握手
如果 /model 列表里没有，您可以尝试强制切换到中转商最通用的 ID：
/model claude-3-5-sonnet


3. 为什么会出现这种情况？
由于您设置了 ANTHROPIC_BASE_URL，Claude Code 现在实际上是在和您的代理服务器对话。有些代理服务器不支持最新的长 ID，只接受简短别名。
只要模型选对，咱们那几个“后备箱”里的技能（Caveman, Superpowers）就能立刻被激活。
甄先生，请告诉我 /model 列表里的内容，我为您挑选最精准的那个。

---
*从 Gemini 导出，2026-05*
