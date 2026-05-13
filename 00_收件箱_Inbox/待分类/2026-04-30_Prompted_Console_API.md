---
title: Prompted
source: gemini
date: 2026-04-30
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

这是因为在认证过程中，网页需要从 Anthropic 的服务器加载授权信息。由于网络环境或缓存原因，有时会卡在“加载中……”界面。

1. 为什么会卡在这里？

网络连接问题：认证页面需要连接 platform.claude.ai，如果您的网络环境不稳定或没有开启合适的网络加速工具，可能会导致资源加载失败。
浏览器缓存/脚本冲突：旧的缓存数据或某些浏览器扩展（如广告拦截器）可能会阻止授权页面的脚本运行。

2. 解决方法建议
您可以尝试以下操作来跳过这个“黑屏”：

手动输入授权码：

回到您的 VS Code 界面（参照 image_f1f5d4.png）。
在左侧的对话框中，有一个 "paste your authorization code manually" 的输入框。
如果浏览器授权成功，通常会给你一串 5-6 位的代码。如果浏览器一直卡住，请尝试刷新浏览器页面或更换浏览器（如从 Chrome 换到 Edge）再次点击登录按钮。


检查 Console 额度（免费确认点）：

直接访问 https://console.anthropic.com/settings/billing。
如果能进入这个页面，说明您的网络没问题。请查看是否有 $5.00 的 Initial Credits。
如果有额度：您可以在 Console 页面手动创建一个 API Key，然后在 VS Code 中根据提示填入，而不需要非得通过这个自动授权页面。



3. 操作总结

目前的软件状态：您的电脑已经装好了所有开发 Agent 和 Skill 所需的软件（Node, Git, Python, MCP SDK）。
第一步核心：完成 API Key 的绑定。
免费性确认：只要您的 Console 账户里有那 5 美元赠送额度，您接下来学习和开发 Agent 及 Skill 的全过程就是完全免费的。

如果手动刷新浏览器还是不行，我们可以尝试通过命令行方式直接绑定 API Key。您想试试命令行操作吗？

---
*从 Gemini 导出，2026-04*
