---
title: Prompted
source: gemini
date: 2026-05-07
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

恭喜，这一步操作非常精准！你已经成功安装了 Superpowers for Copilot Chat。
从你提供的截图来看，这款插件已经在你的 VS Code 中生效了。它将原本复杂的 Agent 工作流 变成了可以直接调用的“指令集”。
接下来如何操作？（保姆级指令）
要实现你第一张图中显示的“开发流程”，你需要通过 GitHub Copilot Chat 窗口来召唤它。请按照以下步骤尝试：
1. 呼叫 Superpowers
在 VS Code 界面点击左侧的“气泡”图标（Copilot Chat 窗口），或者按快捷键 Ctrl + Shift + I。在输入框中输入：
@superpowers
你会发现输入框上方会出现它支持的专属技能。
2. 开始第 ① 阶段：需求确认
根据你第一张图的流程，你可以先输入：

@superpowers /brainstorm 我想开发一个用于自动化审计短视频违规词的 Python 脚本

效果： 它不会直接给你写代码，而是会像一个专业的产品经理一样，先跟你讨论需求、目标用户和核心功能。
3. 推进到第 ③ 阶段：文档与计划
当你聊清楚需求后，输入：

@superpowers /plan

效果： 它会生成一份详细的执行计划文档（对应的就是你图中第 3 阶段），明确告诉你要用什么技术选型，分几步走。

💡 核心进阶操作：Custom Skills（自定义技能）
注意到你截图中的 "Custom Skills" 部分了吗？这才是它最精髓的地方。
由于你目前正在运营“规则甄查-甄先生”账号，涉及大量的平台规则审计逻辑。你可以把这些规则写成 .md 文件放在它指定的目录下（通常是项目根目录下的 .copilot/skills/superpowers/）：

创建规则库： 新建一个 audit_rules.md。
调用它： 在聊天框输入 @superpowers custom audit_rules。

这样，AI 在写代码或分析问题时，就会严格遵守你定义的“甄先生规则体系”。

⚠️ 一个小提醒
如果你输入 @superpowers 没有任何反应，请确保：

你已经登录了 GitHub 账号 并且拥有 GitHub Copilot 的订阅权限。
你的 VS Code 版本在 1.90.0 以上（截图显示基本没问题）。

如果你想让它像图片里那样全自动执行，可以再尝试安装侧边栏那个 Superpowers Copilot Agents，那个版本更倾向于“自动驾驶”模式。
现在，要不要试着运行一下 /brainstorm 指令看看它的反应？

---
*从 Gemini 导出，2026-05*
