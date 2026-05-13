---
title: Prompted
source: gemini
date: 2026-05-02
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

这个报错是因为你正在使用的这个浏览器插件（或者是某个网页工具）想要把内容发送到 Obsidian，但它没有获得“通行证”。
要解决这个问题，你需要回到 Obsidian 软件内，安装并配置一个桥接插件。通常这类工具使用的是 Local REST API 插件。
以下是具体的解决步骤：
第一步：在 Obsidian 中安装“桥接”插件

打开 Obsidian 的 设置 (Settings) -> 社区插件 (Community plugins)。
点击 浏览 (Browse)，搜索并安装 Local REST API。
安装完成后，点击 启用 (Enable)。

第二步：获取 API Key（通行证）

在 Obsidian 设置菜单的左侧找到刚装好的 Local REST API 选项。
在右侧面板中，你会看到一个 API Key 栏（通常是一串随机的字符）。

如果它是空的，点击旁边的按钮生成一个。


点击 Copy（复制）这个 API Key。

第三步：填入扩展程序的设置中

回到显示报错的那个浏览器页面。
点击该扩展程序的图标，进入其 Settings（设置）页面。
找到标注为 Obsidian API Key 或 API Key 的输入框。
将你刚才复制的字符粘贴进去，并保存。


⚠️ 注意事项

软件必须运行： 使用此类同步功能时，你的 Obsidian 桌面端必须是开启状态，否则插件无法连接。
HTTPS 报错： 有些插件要求开启 HTTPS。在 Local REST API 插件设置里，确保相关开关是打开的（如果你的浏览器插件有此要求）。

如果你不确定这是哪个插件触发的：
看这个“Sync to Obsidian”按钮的样式，很像是 Readwise、Omnivore 或者是某个 AI 剪藏工具。如果你能告诉我这个工具的名字，我可以给你更具体的配置建议。
你是想把网页上的资料（比如短视频规则相关的文章）直接剪藏进 Obsidian 吗？

---
*从 Gemini 导出，2026-05*
