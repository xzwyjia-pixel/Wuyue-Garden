---
title: 我现在需要确认一下我原来的中转帐的路径是否正常，再有就是我要用cloudcode去更改你所说的第一项内容修改。 将最后一行原来的那个替换为新的这个内容。
source: gemini
date: 2026-05-09
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## 我现在需要确认一下我原来的中转帐的路径是否正常，再有就是我要用cloudcode去更改你所说的第一项内容修改。 将最后一行原来的那个替换为新的这个内容。

既然我们要确认中转脚本的健康状况，并同步修改直连脚本以打通 DeepSeek 高性能模式，我们可以按照以下精确的工程步骤操作。
这不仅能保住你已有的 Super Power 和 “规则甄查”资料，还能彻底解决路径报错问题。
1. 确认中转脚本 (脚本一) 路径
请在 VS Code 中打开 start-claude-proxy.ps1，确保它的末行不要使用硬编码的长路径。
为了兼容你目前的 npm 报错情况，建议将中转脚本的末行也统一改为最稳妥的调用方式：
# 建议修改为：
npx @anthropic-ai/claude-code


检查重点：确保脚本顶部的环境变量（API Key 和 Base URL）指向的是你的 GPTSAPI 中转站。
优势：使用 npx 会自动跳过你本地损坏的 claude.cmd 软链接，直接启动程序。


2. 执行修改：打通直连脚本 (脚本二)
这是你最关心的任务。请打开 start-claude-direct.ps1，按照以下“处方”修改：

删除旧行：cmd.exe /c "claude"（这行会导致路径解析错误）。
替换为新行：

npx @anthropic-ai/claude-code


为什么不用绝对路径？
既然你重装后依然报错，说明 C:\Users\think\AppData\Roaming\npm 下的索引文件仍然存在双斜杠污染。使用 npx 是目前在 ThinkPad P15V 上最优雅的绕行方案，它不消耗额外 Token，且能完美继承你的 E 盘项目资料。


3. 如何使用 Cloud Code 修改？
你可以直接利用现有的 claude 界面（如果还能进去）或者手动在 VS Code 编辑器中完成。如果你想让 AI 帮你操作：

在对话框中输入：

“请帮我修改 E:\MyCodeProjects\start-claude-direct.ps1，将最后一行改为 npx @anthropic-ai/claude-code。”


当它请求 Write 权限时，点击 “批准”。

4. 验证与资产匹配

资料匹配：修改完成后运行 .\start-claude-direct.ps1。由于你已经在 E:\MyCodeProjects 目录下，AI 会自动加载该目录下的所有规则资料。
中转帐确认：如果直连脚本能顺利启动且不报错，说明程序本体没问题。此时你可以放心对比直连模式下的 Token 消耗优势。

建议操作：
现在请先手动或让 AI 修改 start-claude-direct.ps1 的末行为 npx @anthropic-ai/claude-code，然后再次尝试运行。如果这次成功进入，你的 DeepSeek 高性能直连 就正式宣告打通了！

---
*从 Gemini 导出，2026-05*
