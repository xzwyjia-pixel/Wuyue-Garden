---
title: API Provider，这个按键找不到
source: gemini
date: 2026-04-30
category: 审计合规
tags: [gemini, 审计合规]
---

## API Provider，这个按键找不到

从你的截图 image_f1105a.png 来看，Ollama 服务已经在后台完美运行。找不到 API Provider 通常是因为 Cline 的设置界面需要点击特定的图标才能展开。
请按照以下路径在 VS Code 中寻找：
1. 找到 Cline 的设置入口
在 VS Code 左侧边栏点击 Cline 图标（就是那个像小机器人的图标，见 image_f11b84.png），然后在 Cline 窗口的最上方，你会看到几个小图标：

点击那个齿轮形状的图标 (Settings)。
如果没看到齿轮，请点击右上角的 “...” (更多) 菜单，里面通常隐藏着设置选项。

2. 配置本地免费模型
进入设置页面后，你会看到一个名为 "Provider" 或 "API Provider" 的下拉菜单：

选择 Provider：在下拉列表中找到并选择 Ollama。
填写 Base URL：确保地址填的是 http://localhost:11434（这正对应你 image_f1105a.png 中显示的监听地址）。
选择 Model ID：点击刷新图标，或者手动输入你下载的模型名称，例如 qwen2.5-coder:7b。


3. 第一步实操：为“规则甄查”编写 Skill
配置好后，你可以直接在 Cline 对话框里输入指令。既然你关注 “规则情报局”，我们可以先做一个本地的“合规助手”：
你可以对 Cline 说：

“帮我写一个 Python 脚本 check_rules.py。它需要读取本地一个叫 blacklist.txt 的文件，并检查我发给你的文案是否包含里面的敏感词。请确保这个脚本符合 MCP 协议，以便你可以直接调用它。”

为什么这样做是“甄先生”的最佳选择？

100% 免费：你现在的 Quadro P620 显卡已经接管了计算，完全不走云端流量。
隐私安全：你的业务规则（Rules）和文案草稿只留在你的本地电脑上，不会上传给任何 AI 公司。
专业精准：使用 qwen2.5-coder 模型非常适合处理中文语境下的逻辑判断，符合你对“极简精确”的审美追求。

如果在设置中还是找不到，可以发一张 Cline 插件头部的截图给我，我帮你圈出来。

---
*从 Gemini 导出，2026-04*
