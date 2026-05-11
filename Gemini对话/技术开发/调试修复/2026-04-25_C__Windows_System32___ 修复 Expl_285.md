---
title: C:\Windows\System32>:: 修复 Explorer 命令的核心路径
source: gemini
date: 2026-04-25
category: 技术开发
subcategory: 调试修复
old_category: 系统运维
tags: [gemini, 技术开发, 调试修复]
---

## C:\Windows\System32>:: 修复 Explorer 命令的核心路径

## C:\Windows\System32>:: 修复 Explorer 命令的核心路径
C:\Windows\System32>reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\explorer.exe" /ve /t REG_SZ /d "C:\Windows\explorer.exe" /f
操作成功完成。

C:\Windows\System32>
C:\Windows\System32>:: 修复 Explorer 默认关联
C:\Windows\System32>reg add "HKCR\Folder\shell\open\command" /ve /t REG_EXPAND_SZ /d "%%SystemRoot%%\Explorer.exe" /f
操作成功完成。

C:\Windows\System32>
C:\Windows\System32>:: 彻底删除当前用户的 Explorer 损坏配置
C:\Windows\System32>reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Modules" /f
操作成功完成。

C:\Windows\System32>

既然这三条关键命令都显示“操作成功完成”，说明注册表的核心路径和权限已经重置，困扰你的 Win + E 关联问题在代码层面理论上已经扫清了障碍。
然而，由于 Windows 的快捷键映射（Hotkey Mapping）是由进程驻留内存管理的，你现在感觉“没反应”很可能是因为旧的错误配置还在内存中运行。请按以下最后两步操作：
1. 彻底刷新 Explorer 进程
不要只是重启电脑，先执行一次物理层面的“进程重启”：

按下 Ctrl + Shift + Esc 打开任务管理器。
找到 “Windows 资源管理器”（如果没有，点击“详细信息”）。
右键点击它，选择 “结束任务”。此时任务栏和桌面图标会消失，这是正常的。
点击任务管理器左上角的 “运行新任务”（或“文件”->“运行新任务”）。
输入 explorer.exe，点击确定。
桌面恢复后，立刻按下 Win + E 测试。


2. 如果依然无效，极大概率是“默认应用”协议丢失
如果按键没反应，可能是 Folder 协议在 UI 层被挂起了。请尝试以下手动补救：

按下 Win + I 打开“设置”。
进入 应用 -> 默认应用。
滚动到页面底部，点击 “按文件类型指定默认值”。
找到 .lnk（快捷方式），确保它是“资源管理器”。
返回，点击 “按协议指定默认值”。
找到 FOLDER 协议，确保它关联的是 “文件资源管理器”。


终极排查建议
如果执行完上述所有操作，Win + E 还是没动静，而你双击文件夹却能打开：

这说明问题不在于“打不开”，而在于“信号被拦截”。

作为专业用户，请检查你是否安装了以下可能会劫持全局热键的软件：

ThinkPad 热键驱动 / 联想管家： 检查是否有“Fn 锁定”或“游戏模式”禁用了 Win 键组合。
输入法设置： 某些输入法的“快捷搜索”或“符号热键”经常会占用 Win + E。
PowerToys： 如果你安装了微软的 PowerToys，检查其“键盘管理器”是否重映射了该按键。

现在请尝试重启一次电脑。 如果重启后 Win + E 依然弹窗报错，请把最新的报错截图发给我，看看报错的窗口标题和路径是否发生了变化。

---
*从 Gemini 导出，2026-04*

---
*Gemini · 技术开发 / 调试修复 · 2026-04-25*
