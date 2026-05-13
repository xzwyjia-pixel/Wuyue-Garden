---
title:  尝试使用 CMD 强制运行
这个操作后完成了安装。
source: gemini
date: 2026-05-03
category: 系统运维
tags: [gemini, 系统运维]
---

##  尝试使用 CMD 强制运行
这个操作后完成了安装。

太好了！既然 CMD 强制运行成功了，说明你系统的 Windows Installer 引擎核心功能是正常的，只是前端的“文件关联”和“右键菜单”断开了。
从你发来的第二张截图看，系统找不到 .msi 对应的默认程序，甚至在推荐列表里出现的是 Word 或 抖音，这确实会导致双击无法安装。
为了以后不用每次都开 CMD，咱们把这最后一步“文件关联”彻底修好：
方法一：手动指定系统关联（最直接）
在你的第二张截图界面（设置 > 应用 > 按文件类型选择默认值）：

点击底部的 “在电脑上选择应用”。
在弹出的文件浏览器窗口中，定位到这个路径：
C:\Windows\System32\
在文件夹里找到 msiexec.exe，选中它并点击打开。
现在 .msi 应该就恢复成系统安装图标了，以后双击即可安装。


方法二：注册表一键修复（最彻底）
如果方法一找不到该程序，或者设置不生效，可以用这个“暴力”但有效的办法恢复右键菜单。

在桌面新建一个文本文档 (.txt)。
把下面这段代码全部复制进去：
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\.msi]
@="Msi.Package"

[HKEY_CLASSES_ROOT\Msi.Package\shell\Install]
@="安装(&I)"

[HKEY_CLASSES_ROOT\Msi.Package\shell\Install\command]
@="\"C:\\Windows\\System32\\msiexec.exe\" /i \"%1\" %*"


保存后，把这个文件的后缀名从 .txt 改为 .reg（例如：fix_msi.reg）。
双击运行这个 .reg 文件，点击“是”确认。
重启电脑或重启“资源管理器”，你的右键“安装”按钮就回来了。


为什么会出现这种情况？
由于你平时可能在研究 AI Agent 部署、MCP 协议或本地 LLM，在安装一些开发环境（如 VS Code 扩展或 Cline 依赖）时，某些底层配置或清理工具可能会误碰了系统的全局文件关联。既然现在已经能安装了，建议优先用方法二固化关联，省去以后的麻烦。
搞定关联后，你的那些工业私有云产品或 AI 自动化脚本的安装应该就顺畅了！

---
*从 Gemini 导出，2026-05*
