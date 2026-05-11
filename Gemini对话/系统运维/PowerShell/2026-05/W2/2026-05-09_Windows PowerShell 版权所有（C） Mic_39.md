---
title: Windows PowerShell
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## Windows PowerShell

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> npm i -g @anthropic-ai/claude-code
\(node:19696) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
npm warn cleanup Failed to remove some directories [
npm warn cleanup   [
npm warn cleanup     'E:\\ClaudeEnvironment\\npm_global\\node_modules\\@anthropic-ai\\.claude-code-TcZR59kL',
npm warn cleanup     [Error: EPERM: operation not permitted, unlink 'E:\ClaudeEnvironment\npm_global\node_modules\@anthropic-ai\.claude-code-TcZR59kL\node_modules\@anthropic-ai\claude-code-win32-x64\claude.exe'] {
npm warn cleanup       errno: -4048,
npm warn cleanup       code: 'EPERM',
npm warn cleanup       syscall: 'unlink',
npm warn cleanup       path: 'E:\\ClaudeEnvironment\\npm_global\\node_modules\\@anthropic-ai\\.claude-code-TcZR59kL\\node_modules\\@anthropic-ai\\claude-code-win32-x64\\claude.exe'
npm warn cleanup     }
npm warn cleanup   ]
npm warn cleanup ]

changed 2 packages in 3s
PS C:\Users\think>

从你提供的日志来看，更新失败的核心原因是 EPERM: operation not permitted。
简单来说：Claude 的程序正在运行中，或者被 Windows 系统锁定了，导致 npm 无法删除旧文件并替换新文件。
特别是这一行：
unlink 'E:\...\claude.exe' —— 这说明 claude.exe 进程可能还在后台挂着，或者你的终端窗口正在占用它。
解决方法
请按顺序尝试以下步骤：

1. 彻底关闭相关进程
在执行安装命令前，确保没有任何 Claude 相关的程序在运行：

关闭所有正在运行 claude 命令的终端/命令行窗口。
打开任务管理器 (Ctrl + Shift + Esc)，查找是否有 claude.exe 或 node.exe 进程，如果有，请手动结束任务。
以 管理员身份 重新打开 PowerShell。

2. 清理 npm 缓存并强制安装
有时候残留的临时文件（如你日志里的 .claude-code-TcZR59kL）会干扰安装。请执行：
# 强制覆盖安装
npm install -g @anthropic-ai/claude-code --force

3. 处理环境变量警告 (安全提示)
你的日志开头有一行警告：Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0'。

这意味着什么： 你（或某些脚本）为了跳过网络证书检查，关闭了 Node.js 的安全验证。这在公司内网或使用特殊代理时常见，但存在安全风险。
建议： 如果更新依然报错，尝试在执行安装前恢复安全设置（临时）：
$env:NODE_TLS_REJECT_UNAUTHORIZED = "1"
npm i -g @anthropic-ai/claude-code



4. 手动删除顽固目录（终极手段）
如果上述方法都不行，说明文件夹权限彻底锁死：

手动前往路径：E:\ClaudeEnvironment\npm_global\node_modules\@anthropic-ai\
删除其中所有带 .claude-code-xxx 后缀的文件夹。
再次运行 npm i -g @anthropic-ai/claude-code。


验证是否成功
操作完成后，输入：
claude --version

如果没有报错并且显示了版本号，就说明问题已经解决了！

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
