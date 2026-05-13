---
title: Local REST API这个找不到
source: gemini
date: 2026-05-05
category: 编程开发
tags: [gemini, 编程开发]
---

## Local REST API这个找不到

看到你提供的截图了，显示“无法加载社区插件”，这通常是因为网络环境无法直接访问 Obsidian 的插件市场。
既然你在开发 Python 和 MCP 工具，我们可以用更高效的方式来解决：
1. 解决“无法加载”的问题
由于网络限制，你可以通过以下两种方式安装插件：

手动安装（推荐）：

前往 GitHub 搜索 coddingtonbear/obsidian-local-rest-api。
下载最新的 main.js、manifest.json 和 styles.css 文件。
将它们放入你 Obsidian 库文件夹下的 .obsidian/plugins/obsidian-local-rest-api/ 目录中。
重启 Obsidian，在“已安装插件”列表中启用它。


使用代理/加速器：如果你有现成的网络工具，确保 Obsidian 的流量经过代理。


2. 检查替代方案：Obsidian Connect
如果你使用的是某些特定的剪藏插件（例如常用的 MarkDownload），它可能支持 Obsidian Connect（原名 Obsidian Clipper）。

在插件市场搜索 Obsidian Connect，它的配置逻辑与 REST API 类似，也是生成一个 Token 进行握手。


3. 开发者进阶方案 (MCP 相关)
考虑到你正在研究 Ollama 和 Python 开发，如果你想让你的本地 AI 直接与 Obsidian 交互，Local REST API 确实是最佳选择。

API 调试：安装成功后，你可以通过 curl 或 Python 的 requests 库来测试连接：
curl -X GET http://127.0.0.1:27123/active-file \
     -H "Authorization: Bearer YOUR_API_KEY"



建议： 先尝试手动从 GitHub 下载插件包，这是绕过“无法加载社区插件”最直接的办法。
你目前正在调试的 Python 敏感词检测工具，是否也计划集成到这个 Obsidian 工作流中？

---
*从 Gemini 导出，2026-05*
