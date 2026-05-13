---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> ollama list
NAME          ID              SIZE      MODIFIED
qwen2:1.5b    f6daf2b25194    934 MB    16 minutes ago
PS C:\Users\think>
source: gemini
date: 2026-05-07
category: 系统运维
tags: [gemini, 系统运维]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> ollama list
NAME          ID              SIZE      MODIFIED
qwen2:1.5b    f6daf2b25194    934 MB    16 minutes ago
PS C:\Users\think>

找到了！问题就在这里：你的 Ollama 列表里只有 qwen2:1.5b，而你在 Cline 里的设置是 qwen2.5-coder:7b。这就像是你有奔驰的钥匙，但车库里停的是一辆五菱宏光，系统自然“点火”失败。
要让 Plan Mode 顺利跑通，你有两个选择：
方案 A：直接使用现有的模型（最快，适合立刻测试）
不需要下载新东西，直接修改 Cline 的配置：

点击 Cline 的 齿轮图标 (Settings)。
在 Model ID 处，把原来的名字删掉，改成：qwen2:1.5b。
点击 Retry 或者重新发送指令。


注意： 1.5b 模型比较小，它的“智商”在处理复杂逻辑时可能会偶尔“断片”，但用来测试 Plan Mode 的流程通不通是没问题的。

方案 B：下载更强的“程序员”模型（推荐，逻辑更稳）
如果你希望本地 AI 能更精准地审计代码和写计划，建议下载 Qwen2.5 的编程专用版。

在你的 PowerShell 中输入：
ollama pull qwen2.5-coder:7b


等待下载进度条完成（约 4.7GB）。
下载完成后，Cline 里的 qwen2.5-coder:7b 设置就生效了。


💡 为什么我推荐方案 B？

逻辑精度： 1.5b 模型太小，可能看不出 analyze_folder.py 里的深层 Bug。
Plan Mode 的本质： 计划模式非常依赖模型的“常识”和“因果推断”，7b 及以上规模的模型在这一块的通过性有质的飞跃。

建议： 你可以先按 方案 A 改成 qwen2:1.5b 看看 Cline 动不动；如果动了，说明链路全通，然后再去后台静默执行 ollama pull 升级装备。
等配置改好后，再跑一次刚才的测试指令，看看它能不能说出 resolve_icon 怎么改！

---
*从 Gemini 导出，2026-05*
