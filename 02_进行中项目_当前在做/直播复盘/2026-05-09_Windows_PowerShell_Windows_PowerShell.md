---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> # 列出所有正在运行且可能带有交互界面的非系统进程
PS C:\Users\think> Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object ProcessName, MainWindowTitle

ProcessName       MainWindowTitle
-----------       ---------------
chrome            修复Ctrl+E快捷键冲突问题 - Gemini - Google Chrome
Clash for Windows Clash for Windows
douyin            抖音
TextInputHost     Windows 输入体验
Weixin            微信
WindowsTerminal   Windows PowerShell


PS C:\Users\think>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> # 列出所有正在运行且可能带有交互界面的非系统进程
PS C:\Users\think> Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object ProcessName, MainWindowTitle

ProcessName       MainWindowTitle
-----------       ---------------
chrome            修复Ctrl+E快捷键冲突问题 - Gemini - Google Chrome
Clash for Windows Clash for Windows
douyin            抖音
TextInputHost     Windows 输入体验
Weixin            微信
WindowsTerminal   Windows PowerShell


PS C:\Users\think>

从你运行的进程列表来看，douyin（抖音桌面端） 是最可疑的元凶。很多短视频或直播类软件为了方便用户在录屏、截图或互动时快速操作，会默认占用一些全局快捷键。
既然你想用命令的方式解决，我们可以通过 PowerShell 强制结束可疑进程来验证，然后彻底禁用它的自启动或修改其配置。
1. 验证元凶：用命令结束可疑进程
请依次在 PowerShell 中执行以下命令，每执行一行后，按一次 Ctrl + E 看看是否还弹出报错：
# 1. 结束抖音进程（最显眼的嫌疑对象）
Stop-Process -Name "douyin" -Force

# 2. 如果还没好，尝试结束微信（微信偶尔会有全局快捷键冲突）
Stop-Process -Name "Weixin" -Force

观察结果：

如果在执行 Stop-Process -Name "douyin" 后快捷键恢复正常，那么问题就在抖音桌面端的设置里。
报错信息“无法访问指定设备”说明该快捷键原本绑定的文件已被删除或移动，但软件仍尝试去调用它。


2. 彻底修复：禁用该软件的快捷键映射
如果确认是抖音或其他软件引起的，你可以通过以下命令将其从开机启动项中移除，防止它下次继续占用：
# 查看所有自启动项目，找到对应的软件名
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location

# 建议手动操作：
# 打开抖音设置 -> 快捷键设置 -> 找到 Ctrl + E 并修改或关闭它。


3. 如果命令杀掉进程后仍未解决（注册表劫持）
如果所有第三方软件都关闭了，按 Ctrl + E 依然报错，说明快捷键在注册表级别被劫持到了一个不存在的路径。我们可以用命令将资源管理器的默认热键关联强制修复：
执行以下命令重置资源管理器（Explorer）的键盘处理关联：
# 修复资源管理器打开位置的注册表键值
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
Set-ItemProperty -Path $regPath -Name "LaunchTo" -Value 1 

# 重启资源管理器生效
Stop-Process -Name explorer -Force; Start-Process explorer


总结建议
考虑到你经常使用抖音进行“规则研究”和内容发布，该客户端极有可能是为了“快速上传”或“快速打开编辑器”而占用了 Ctrl + E。

直接方案： 进入抖音桌面端的“设置” -> “快捷键”，把 Ctrl + E 这一项删除。
替代方案： 养成使用 Win + E 的习惯，这是 Windows 系统底层最稳固的“打开此电脑”快捷键，几乎不会被第三方软件劫持。

如果上述操作后仍有问题，请告诉我你在杀掉哪个进程后快捷键不再报错，我再为你针对性关闭该软件的劫持。

---
*从 Gemini 导出，2026-05*
