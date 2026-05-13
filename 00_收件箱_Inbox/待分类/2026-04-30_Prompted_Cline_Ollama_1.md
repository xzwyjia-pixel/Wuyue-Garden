---
title: Prompted
source: gemini
date: 2026-04-30
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

从您提供的截图看，目前左侧 Cline 的设置界面被一个 “Introducing Cline Kanban” 的弹窗挡住了。要配置 Ollama，请按照以下步骤操作：
1. 移开遮挡物

点击左侧那个黑色浮窗右上角的 “X” 将其关闭。
或者点击底部的 “Done” 按钮。

2. 找到 API Provider
一旦遮挡物消失，您会看到 Cline 的核心配置界面：

找到 “API Provider” 下拉菜单。
在列表中向下滑动，选择 “Ollama”。
Model ID：点击旁边的刷新图标，或者直接输入 qwen2.5-coder:7b。
Ollama Base URL：确保是 http://localhost:11434。


3. 下一步：验证您的本地环境
现在您的软件链路已经打通：

后台：ollama serve 正在运行。
显卡：Quadro P620 已就绪。
前端：VS Code 中的 Cline 插件。

4. 针对“规则甄查”项目的首个任务建议
既然一切都已就绪，您可以直接在 Cline 的对话框里输入以下指令，开始构建您的 “规则情报局” 助手：

指令：
“帮我创建一个名为 rules_intelligence.py 的脚本。逻辑是：读取我电脑上的 blacklist.txt（违规词库），并对比我输入的社交媒体文案。请使用 MCP 协议编写，以便你可以通过调用这个工具来帮我审核内容。”

核心优势确认

100% 免费：只要 Provider 选的是 Ollama，您的所有操作都在本地显卡运行，不产生任何 API 费用。
数据安全：您的合规规则和文案草稿永远不会离开您的电脑，这完美符合您对项目隐私的要求。

如果您关闭弹窗后仍找不到选项，请再发一张左侧配置栏完整展示的截图给我。

---
*从 Gemini 导出，2026-04*
