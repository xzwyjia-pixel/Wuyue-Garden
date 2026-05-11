---
title: Windows PowerShell
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 编程开发
tags: [gemini, 系统运维, PowerShell]
---

## Windows PowerShell

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> # 使用 npm 安装
PS C:\Users\think> npm install -g cc-switch
\(node:11356) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
npm error code E404
npm error 404 Not Found - GET https://registry.npmjs.org/cc-switch - Not found
npm error 404
npm error 404  'cc-switch@*' is not in this registry.
npm error 404
npm error 404 Note that you can also install from a
npm error 404 tarball, folder, http url, or git url.
npm error A complete log of this run can be found in: E:\ClaudeEnvironment\npm_cache\_logs\2026-05-09T09_38_43_254Z-debug-0.log
PS C:\Users\think>
PS C:\Users\think> # 或者使用 yarn 安装
PS C:\Users\think> yarn global add cc-switch
yarn : 无法将“yarn”项识别为 cmdlet、函数、脚本文件或可运行程序的名称。请检查名称的拼写，如果包括路径，请确保路径正确
，然后再试一次。
所在位置 行:1 字符: 1
+ yarn global add cc-switch
+ ~~~~
    + CategoryInfo          : ObjectNotFound: (yarn:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

PS C:\Users\think> Stop-Process -Name "Listary" -Force
Stop-Process : 由于以下错误而无法停止进程“Listary (7616)”: 拒绝访问。
所在位置 行:1 字符: 1
+ Stop-Process -Name "Listary" -Force
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : CloseError: (System.Diagnostics.Process (Listary):Process) [Stop-Process]，ProcessCommand
    Exception
    + FullyQualifiedErrorId : CouldNotStopProcess,Microsoft.PowerShell.Commands.StopProcessCommand

PS C:\Users\think> Stop-Process -Name "Listary" -Force
Stop-Process : 由于以下错误而无法停止进程“Listary (7616)”: 拒绝访问。
所在位置 行:1 字符: 1
+ Stop-Process -Name "Listary" -Force
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : CloseError: (System.Diagnostics.Process (Listary):Process) [Stop-Process]，ProcessCommand
    Exception
    + FullyQualifiedErrorId : CouldNotStopProcess,Microsoft.PowerShell.Commands.StopProcessCommand

PS C:\Users\think> # 使用 npm 安装
PS C:\Users\think> npm install -g cc-switch
\(node:18276) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
npm error code E404
npm error 404 Not Found - GET https://registry.npmjs.org/cc-switch - Not found
npm error 404
npm error 404  'cc-switch@*' is not in this registry.
npm error 404
npm error 404 Note that you can also install from a
npm error 404 tarball, folder, http url, or git url.
npm error A complete log of this run can be found in: E:\ClaudeEnvironment\npm_cache\_logs\2026-05-09T09_43_25_213Z-debug-0.log
PS C:\Users\think>
PS C:\Users\think> # 或者使用 yarn 安装
PS C:\Users\think> yarn global add cc-switch

看起来你在安装过程中遇到了几个典型的问题。报错 404 Not Found 说明 cc-switch 并不在 npm 的公共仓库里，这通常意味着它是一个本地开发的项目或者是通过 MCP (Model Context Protocol) 方式安装的工具。
结合你提到的 frontend-master 技能（Skill），这很可能是在配置你的 AI 环境（如 Claude 或其他支持 MCP 的客户端）。

1. 解决 cc-switch 的安装问题
既然 npm 找不到这个包，说明它应该是你本地 E:\ClaudeEnvironment 或类似目录下的一个项目。请尝试以下步骤：


切换到源码目录安装：
如果你本地有这个工具的代码文件夹，请先进入该文件夹，再进行本地链接：
cd E:\ClaudeEnvironment\cc-switch  # 请根据你实际的路径修改
npm install
npm link



关于权限拒绝 (Listary)：
你尝试停止 Listary 失败是因为没有管理员权限。请右键点击 PowerShell 图标，选择**“以管理员身份运行”**，然后再执行 Stop-Process 命令。



2. 补全 frontend-master 的功能
如果你是在配置 MCP 服务器，技能（Skill）通常对应代码中的 tools。如果你发现只有 1 个功能可用，通常是因为另外 3 个功能在配置文件中未启用，或者代码未编译。
操作步骤：
第一步：检查配置文件
找到你的 MCP 配置文件（通常是 claude_desktop_config.json），检查 frontend-master 的配置项。

确认 args 指向的文件路径是否正确。
确认是否漏掉了某些启动参数。

第二步：重新编译项目
如果 frontend-master 是你本地开发的 Python 或 TypeScript 项目，可能需要更新构建：
cd E:\ClaudeEnvironment\frontend-master
# 如果是 TS 项目：
npm install
npm run build
# 如果是 Python 项目：
pip install -e .

第三步：强制刷新 MCP 技能

彻底关闭你的 AI 客户端（如 Claude Desktop）。
在任务管理器中结束相关的 Node 进程。
重新启动客户端，它会重新读取 frontend-master 的入口文件，此时应该能识别到全部 4 个功能。


⚠️ 一个关键的安全提醒
你的日志中出现了：
Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0'
这意味着你当前关闭了 SSL 证书验证，这会带来安全风险。如果你之前是为了解决网络问题开启的，建议在安装完成后运行以下命令恢复默认设置：
$env:NODE_TLS_REJECT_UNAUTHORIZED="1"

建议： 如果你知道 cc-switch 所在的具体本地文件夹，请发给我，我可以给你写出更精准的路径跳转和安装命令。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
