---
title: 上述命令在哪里输入？powershell?claudecode?
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## 上述命令在哪里输入？powershell?claudecode?

上述命令应该在你的 系统终端（System Terminal） 中输入，而不是在 Claude Code 的对话界面里。
对于你使用的 ThinkPad P15V 运行的环境，具体的选择如下：
1. 推荐：PowerShell (管理员权限)
这是最直接的方式。

按下 Win + X，选择 终端 (管理员) 或 Windows PowerShell (管理员)。
直接粘贴执行上面给出的 npm 或 bun 安装命令。
原因：这些工具需要通过包管理器安装到你的系统全局路径中，PowerShell 拥有执行脚本和写入全局目录的权限。

2. 不要直接在 Claude Code 对话框输入

如果你在 Claude Code 的对话窗口里输入安装命令，它可能会尝试用 AI 的逻辑去“解释”或者通过它内置的 shell 权限去运行。
最佳实践：先在 PowerShell 里装好，然后重启 Claude Code。这样 Claude Code 就能通过环境变量识别到这些新安装的工具（如 gsd、opsx 等）。


⚠️ Windows 用户特别注意（避坑指南）
由于你之前安装过 Superpowers，在 PowerShell 中执行新命令时，请注意以下两点：

执行策略限制：
如果报错“无法加载文件...因为在此系统上禁止运行脚本”，请先在 PowerShell 执行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
环境变量同步：
安装完成后，如果输入 gsd 或 ecc 提示“找不到命令”，请关闭并重新打开你的 PowerShell 窗口。

安装后的验证
安装成功后，你可以分别输入以下命令检查是否安装到位：

ecc --version
gsd --help
opsx --version

等这些命令在 PowerShell 里都能跑通了，你再打开 claude 进入交互模式，它们就能协同工作了。

---
*从 Gemini 导出，2026-05*
