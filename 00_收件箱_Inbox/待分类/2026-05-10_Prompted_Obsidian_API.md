---
title: Prompted
source: gemini
date: 2026-05-10
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

这就简单了，你现在已经处于 Obsidian AI Exporter 的配置界面。
请按照以下三个步骤操作，即可完成“握手”：
1. 展开高级设置
点击界面中部的 ▶ ADVANCED SETTINGS（高级设置）。点击后它会向下展开隐藏的输入框。
2. 填写 API Key 和端口
在展开的内容中，你会看到两个核心选项：

API Key: 把你刚才用 Python 脚本提取到的那一长串密钥粘贴进去。
Server URL (或 Port): 确保它是 http://127.0.0.1:27124（这是该插件默认的端口，如果脚本提示是 27123，请以脚本为准）。

3. 验证并保存

点击左下角的 🔌 Test Connection（测试连接）。
如果显示 "Success" 或绿色对勾，说明连接成功。
关键一步： 必须点击右下角的紫色按钮 💾 Save Settings（保存设置）。


💡 贴心提示：

确保 Obsidian 没关：测试连接时，Obsidian 软件必须在后台运行，且 Local REST API 插件处于启用状态。
打开开关：保存后，记得把界面最上方的 Obsidian (API) 后面的开关拨到“开启”状态（变色），这样以后点击同步时才会默认发送到 Obsidian。

完成这些，你图片里那个黄色的警告文字就会彻底消失了。试试看？

---
*从 Gemini 导出，2026-05*
