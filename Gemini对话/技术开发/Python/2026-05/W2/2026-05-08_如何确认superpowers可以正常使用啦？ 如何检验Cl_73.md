---
title: 如何确认superpowers可以正常使用啦？
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: Python
old_category: 编程开发
tags: [gemini, 技术开发, Python]
---

## 如何确认superpowers可以正常使用啦？

## 如何确认superpowers可以正常使用啦？
如何检验Claude-hud已经开启了？

甄先生，要确认这套“精密终端”是否调校完成，不需要复杂的代码，只需通过以下两个直观的“视觉”和“反馈”信号即可验证：
1. 验证 Claude-HUD 是否开启
HUD（抬头显示）一旦开启，你的终端界面会发生明显的物理变化：


视觉标志：观察终端窗口的顶部或底部。你应该能看到一排动态更新的参数，通常包括：

Model: 显示 Sonnet 4.6。
Tokens: 实时显示当前对话消耗的 Input/Output Token 数。
Cost: 实时计算当前 Session 的消费金额（以美金计）。



交互验证：如果你没看到这排数据，直接在 > 后输入：

/config

查看 gui.hud 是否标记为 on。如果还是没有，尝试按下 Ctrl + H（部分版本的快捷键）手动切换显示状态。



2. 检验 Superpowers 是否已全功能解锁
由于之前存在“5 descriptions dropped”的问题，我们需要确认那几个高阶技能（尤其是验证和执行类）是否已经完整加载。
执行这个“压力测试”指令：

> superpowers:writing-plans, 为我的 audit_tool.py 设计一个防死循环的逻辑。

如何判断正常：

通过（成功）：Claude 立即进入“思考”状态，并输出一个带有 [Plan] 标签的结构化列表。这证明它读到了 writing-plans 的完整定义。
失败（截断）：如果它只是像普通对话一样给你写了几行 Python 代码，或者回复“我不明白如何编写 plan”，说明技能描述依然在 Truncated 状态。


3. 终极自检（利用你最爱的 Caveman）
输入这个组合命令，让系统自己汇报健康状况：

> caveman-stats, 确认 HUD 状态和 superpowers 加载情况。

理想的极简反馈应该是：

● HUD: Active (Visible)
● Budget: 5% (No truncated skills)
● Ready: Rules Investigation context loaded.


💡 甄先生的特别提醒：
如果你发现 HUD 开启了但数据不跳动，或者 Superpowers 还是提示丢失，请检查你是否还在 C:\Windows\System32。
一定要切换到你的项目目录！ 因为很多 Superpowers 是依赖项目根目录下的 .claude 文件夹或 CLAUDE.md 才能激活的。
现在看一眼你的屏幕顶部，那排精密的 Token 计数器跳出来了吗？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / Python · 2026-05-08*
