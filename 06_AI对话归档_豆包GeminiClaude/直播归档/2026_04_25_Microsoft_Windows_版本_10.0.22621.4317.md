---
title: Microsoft Windows [版本 10.0.22621.4317]
(c) Microsoft Corporation。保留所有权利。

C:\Windows\System32>reg add "HKCU\Software\Classes\CLSID\{52205fd8-5dfb-4472-8046-3306e0f391a2}\shell\opennewwindow\command" /ve /t REG_EXPAND_SZ /d "%%SystemRoot%%\Explorer.exe" /f
操作成功完成。

C:\Windows\System32>
C:\Windows\System32>reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LaunchTo" /t REG_DWORD /d 1 /f
操作成功完成。

C:\Windows\System32>reg add "HKCU\Software\Classes\CLSID\{52205fd8-5dfb-4472-8046-3306e0f391a2}\shell\opennewwindow\command" /ve /t REG_EXPAND_SZ /d "%%SystemRoot%%\Explorer.exe" /f
操作成功完成。

C:\Windows\System32>
C:\Windows\System32>reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LaunchTo" /t REG_DWORD /d 1 /f
操作成功完成。

C:\Windows\System32>
source: gemini
date: 2026-04-25
category: 文案创作
tags: [gemini, 文案创作]
---

## Microsoft Windows [版本 10.0.22621.4317]
(c) Microsoft Corporation。保留所有权利。

C:\Windows\System32>reg add "HKCU\Software\Classes\CLSID\{52205fd8-5dfb-4472-8046-3306e0f391a2}\shell\opennewwindow\command" /ve /t REG_EXPAND_SZ /d "%%SystemRoot%%\Explorer.exe" /f
操作成功完成。

C:\Windows\System32>
C:\Windows\System32>reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LaunchTo" /t REG_DWORD /d 1 /f
操作成功完成。

C:\Windows\System32>reg add "HKCU\Software\Classes\CLSID\{52205fd8-5dfb-4472-8046-3306e0f391a2}\shell\opennewwindow\command" /ve /t REG_EXPAND_SZ /d "%%SystemRoot%%\Explorer.exe" /f
操作成功完成。

C:\Windows\System32>
C:\Windows\System32>reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LaunchTo" /t REG_DWORD /d 1 /f
操作成功完成。

C:\Windows\System32>

既然这两条关键命令都已经“操作成功完成”，说明 Win + E 快捷键调用的底层类 ID（CLSID）和默认打开位置（此电脑）已经在当前用户下重新绑定了。
如果此时按下 Win + E 依然没有反应，这说明系统仍然在读取内存中那个错误的快捷键映射表，或者是权限锁死导致新设置无法即时生效。

第一步：物理刷新“热键表”
不要通过右键重启，请执行这个彻底的刷新动作：

按下 Ctrl + Shift + Esc 打开任务管理器。
找到 “Windows 资源管理器”，右键点击选择 “结束任务”。
此时桌面会变黑，点击任务管理器顶部的 “运行新任务”。
在输入框中输入 cmd /c taskkill /f /im explorer.exe & start explorer.exe 并回车。
等桌面重载后，立刻按下 Win + E。

第二步：检查“拒绝访问”留下的隐患
你在之前的脚本运行中遇到了大量“拒绝访问”，这说明 HKEY_LOCAL_MACHINE (HKLM) 区域的关联被锁死了。虽然我们刚才成功写入了 HKEY_CURRENT_USER (HKCU)，但系统有时会优先读取 HKLM 中的错误信息。
请尝试手动赋予权限：

按 Win + R 输入 regedit。
定位到：HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Folder\shell\opennewwindow。
右键点击该项 -> 权限 -> 高级。
检查“所有者”是否为 SYSTEM 或 Administrators。
如果还是无法修改，请在 安全模式 下重新运行之前的修复脚本，这是绕过“拒绝访问”最彻底的方法。


终极判断：确认是否为“物理拦截”
如果执行完这些操作，点击任务栏图标能打开“此电脑”，但 Win + E 组合键依然弹窗报错：

结论： 报错弹窗是由 explorer.exe 进程直接弹出的（如你之前截图中窗口标题所示），这意味着 快捷键信号已经传达给了资源管理器，但资源管理器在启动瞬间找不到对应的“外壳协议”。

建议： 由于你系统中出现了 .lit 和 .lmp4 等异常后缀，这通常意味着系统遭受过恶意修改。如果安全模式脚本修复后依然无效，建议使用 Windows 设置 -> 系统 -> 恢复 -> 重置此电脑（保留个人文件）。这会重写所有的系统关联协议，同时保留你的文档和数据。
现在按下 Win + E 时，那个“该文件没有与之关联的应用”报错还会弹出来吗？

---
*从 Gemini 导出，2026-04*
