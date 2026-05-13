---
title: 
● There's an issue with the selected model (claude-sonnet-4-6). It may not exist or you may not have access to it. Run /model to pick a different model.

✻ Cogitated for 3s

> /model claude-3-7-sonnet-latest
  ⎿  Model 'claude-3-7-sonnet-latest' not found
> /model claude-3-5-sonnet-20241022
  ⎿  Model 'claude-3-5-sonnet-20241022' not found
source: gemini
date: 2026-05-08
category: 编程开发
tags: [gemini, 编程开发]
---

## 
● There's an issue with the selected model (claude-sonnet-4-6). It may not exist or you may not have access to it. Run /model to pick a different model.

✻ Cogitated for 3s

> /model claude-3-7-sonnet-latest
  ⎿  Model 'claude-3-7-sonnet-latest' not found
> /model claude-3-5-sonnet-20241022
  ⎿  Model 'claude-3-5-sonnet-20241022' not found

看来中转站的“模型 ID 映射”比官方的还要严格。根据你之前的仪表盘截图显示，你实际成功调用的模型名称是 claude-sonnet-4-5-20250929。
在这种第三方中转环境下，Claude Code 有时无法识别带有日期后缀的长 ID，我们必须尝试最通用的**“短别名”**，或者直接手动对齐你仪表盘上的那个型号。
1. 甄先生的“精密对齐”尝试
请按顺序尝试以下指令，直到其中一个生效（不再提示 not found）：

方案 A（最通用）：

/model claude-3-5-sonnet


方案 B（手动强制对齐你的仪表盘）：

/model claude-sonnet-4-5-20250929


方案 C（查看可用清单）：

/model
(只输入这个命令，看看它弹出的滚动列表里有哪些可选的 Sonnet 型号。)




2. 为什么之前的 ID 会失败？

API 代理层差异：你的中转站（gptsapi.net）在后端将 claude-sonnet-4-5 映射到了特定的实例，如果请求的 ID 多个字母或日期不匹配，代理层就会直接返回 404/Not Found。
Claude Code 的限制：v2.1.133 有时会自动补全官方前缀，如果补全后与中转站 ID 不一致也会报错。


3. 环境与品牌体检（对齐后动作）
一旦模型 ID 对齐，底部的 Cogitated 进度条会变绿。届时，请不要犹豫，直接把这份**“甄先生规则审计指令”**发给它：

指令：
`“甄先生”品牌规则库建立指令：

读取 @audit_tool.py 的逻辑。
新建 rules.json。
严格分级：HIGH (封号), MEDIUM (限流), LOW (优化)。
生成后使用 !python -m json.tool rules.json 验证。`



💡 甄先生的极简锦囊：
如果以上方案都提示 not found，请直接在你的**网页端仪表盘（API Keys 页面）**查看“可用模型”那一栏，把那个一模一样的字符串复制过来。
我们现在就差这临门一脚了。尝试一下 /model claude-3-5-sonnet 成功了吗？

---
*从 Gemini 导出，2026-05*
