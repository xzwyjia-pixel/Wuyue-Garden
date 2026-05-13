---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> # 修复资源管理器层级的 shell 执行命令
PS C:\Users\think> $regPath = "HKCU:\Software\Classes\CLSID\{52205393-4030-4313-915B-7C8303F50129}\shell\open\command"
PS C:\Users\think> if (Test-Path $regPath) {
>>     Remove-Item -Path "HKCU:\Software\Classes\CLSID\{52205393-4030-4313-915B-7C8303F50129}" -Recurse -Force
>> }
PS C:\Users\think>
PS C:\Users\think> # 重置关联路径
PS C:\Users\think> reg add "HKCR\Folder\shell\open\command" /ve /t REG_EXPAND_SZ /d "explorer.exe" /f
错误: 拒绝访问。
PS C:\Users\think>
PS C:\Users\think> # 立即重启资源管理器
PS C:\Users\think> Stop-Process -Name explorer -Force; Start-Process explorer
PS C:\Users\think> # 检查并列出所有被设置了“调试器”劫持的程序
PS C:\Users\think> Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\*" |
>> Where-Object { $_.Debugger -ne $null } |
>> Select-Object PSChildName, Debugger
PS C:\Users\think> # 检查系统层级的键盘映射
PS C:\Users\think> Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layout" -Name "Scancode Map" -ErrorAction SilentlyContinue
PS C:\Users\think>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> # 修复资源管理器层级的 shell 执行命令
PS C:\Users\think> $regPath = "HKCU:\Software\Classes\CLSID\{52205393-4030-4313-915B-7C8303F50129}\shell\open\command"
PS C:\Users\think> if (Test-Path $regPath) {
>>     Remove-Item -Path "HKCU:\Software\Classes\CLSID\{52205393-4030-4313-915B-7C8303F50129}" -Recurse -Force
>> }
PS C:\Users\think>
PS C:\Users\think> # 重置关联路径
PS C:\Users\think> reg add "HKCR\Folder\shell\open\command" /ve /t REG_EXPAND_SZ /d "explorer.exe" /f
错误: 拒绝访问。
PS C:\Users\think>
PS C:\Users\think> # 立即重启资源管理器
PS C:\Users\think> Stop-Process -Name explorer -Force; Start-Process explorer
PS C:\Users\think> # 检查并列出所有被设置了“调试器”劫持的程序
PS C:\Users\think> Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\*" |
>> Where-Object { $_.Debugger -ne $null } |
>> Select-Object PSChildName, Debugger
PS C:\Users\think> # 检查系统层级的键盘映射
PS C:\Users\think> Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layout" -Name "Scancode Map" -ErrorAction SilentlyContinue
PS C:\Users\think>

从你的 PowerShell 输出看，最重要的信息是 “错误：拒绝访问”。这说明你在尝试修改 HKCR（全局根类）下的关联路径时，由于没有使用管理员权限，操作被拦截了。
此外，由于你提供的最新截图标题显示 shell:::{52205fd8-5dfb-447d-801a-d0b52f2e83e1}，这说明劫持点是在 User Shell 扩展层级，而非普通的键盘映射。
请务必按以下步骤以管理员身份重新运行修复脚本：
1. 切换至“管理员”模式
请点击任务栏搜索框，输入 PowerShell，在右侧选择 “以管理员身份运行”。

2. 执行针对性的“深度清理”命令
请将以下代码块完整复制并粘贴到管理员权限的 PowerShell 中：
# 1. 强制修复被拒绝访问的全局关联项
# 这一步需要管理员权限
reg add "HKCR\Folder\shell\open\command" /ve /t REG_EXPAND_SZ /d "explorer.exe" /f

# 2. 移除 Listary 残留的最关键劫持 GUID
# 对应你报错窗口标题中的那串代码
$guid = "{52205fd8-5dfb-447d-801a-d0b52f2e83e1}"
$paths = @(
    "HKCU:\Software\Classes\CLSID\$guid",
    "HKLM:\SOFTWARE\Classes\CLSID\$guid",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\CLSID\$guid"
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "已清理劫持项: $p" -ForegroundColor Green
    }
}

# 3. 修复 Explorer 默认启动目标（重置为“此电脑”）
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LaunchTo" /t REG_DWORD /d 1 /f

# 4. 强制重启 Explorer 进程以应用注册表修改
Stop-Process -Name explorer -Force; Start-Process explorer


3. 为什么之前没成功？

权限不足：你之前的 reg add 命令返回了“拒绝访问”，这意味着核心的关联修复没有生效。
劫持位置：报错图 image_a19a99.png 指向的 shell:::{52205fd8...} 是 Listary 用来拦截 Windows 系统搜索界面的钩子。即便删除了软件，注册表里这个 GUID 的 open\command 依然指向了一个不存在的路径。

验证方法
执行完上述脚本后：

确认 PowerShell 窗口中没有出现红色的“拒绝访问”字样。
再次按下 Ctrl + E。

正常情况：如果是在浏览器或资源管理器里，它应该聚焦到搜索框；如果是在桌面，它可能不再触发任何报错（视具体的焦点而定）。



提示：考虑到你正在进行 AI 相关的技术开发并管理着 ThinkPad P15V 这样的工作站级设备，这类由于第三方工具（Listary）残留导致的注册表污染比较常见。如果重启后仍报错，建议检查是否还有残留的 Context Menu（右键菜单） 扩展在后台尝试调用 Listary。

---
*从 Gemini 导出，2026-05*
