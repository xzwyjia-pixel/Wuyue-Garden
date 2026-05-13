---
title: Prompted
source: gemini
date: 2026-05-03
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

太棒了！从你的截图来看，npm install -g @openai/codex 已经成功执行（提示 changed 2 packages in 3s 说明包已经顺利安装到你的全局环境中了）。
既然已经安装完毕，接下来你可以按照以下步骤进行配置和使用：
1. 验证安装
在当前的 PowerShell 窗口中，直接输入以下命令来确认 Codex 已准备就绪：
codex --help

如果终端打印出了 Codex 的各种命令和帮助信息，说明安装完全没问题。
2. 登录与授权
在使用 Codex 帮你写代码之前，你需要先绑定你的账号。请输入：
codex login

按下回车后，系统通常会自动打开你的默认浏览器。请按照网页提示，登录你的 ChatGPT/OpenAI 账号并点击授权。授权成功后，你可以关掉浏览器页面回到 PowerShell。
3. 尝试你的第一个指令
完成登录后，你就可以直接在终端里用自然语言让它干活了。例如，试着让它帮你写一段 PowerShell 脚本：
codex "写一段 PowerShell 脚本，用来批量将当前目录下的所有 .txt 文件后缀改为 .md"


💡 常见问题排查：
如果你在输入 codex 时，PowerShell 报了一大段红字，提示**“无法将‘codex’项识别为 cmdlet、函数、脚本文件或可运行程序的名称”**，这说明 npm 的全局安装路径没有被添加到你电脑的“系统环境变量 (Path)”中。如果出现这种情况，请告诉我，我会教你如何配置环境变量。

---
*从 Gemini 导出，2026-05*
