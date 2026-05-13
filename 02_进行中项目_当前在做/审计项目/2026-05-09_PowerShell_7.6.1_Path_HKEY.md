---
title: PowerShell 7.6.1
PS C:\Windows\System32> assoc .folder=Folder
assoc: The term 'assoc' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> assoc .directory=Directory
assoc: The term 'assoc' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> cmd /c "assoc .folder=Folder"
.folder=Folder
PS C:\Windows\System32> cmd /c "assoc .directory=Directory"
>>     ```
>>
>> ---
>>
>> ### 方案二：使用 PowerShell 原生命令修改注册表
>> 如果你想用更“PowerShell”的方式从底层修复，可以执行以下命令，这会直接修改注册表中负责文件关联的部分：
>>
>> ```powershell
>> # 修复 .folder 关联
>> if (!(Test-Path "Registry::HKEY_CLASSES_ROOT\.folder")) {
>>     New-Item -Path "Registry::HKEY_CLASSES_ROOT\.folder" -Force
>> }
>> Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\.folder" -Name "(Default)" -Value "Folder"
>>
>> # 修复 .directory 关联
>> if (!(Test-Path "Registry::HKEY_CLASSES_ROOT\.directory")) {
>>     New-Item -Path "Registry::HKEY_CLASSES_ROOT\.directory" -Force
>> }
>> Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\.directory" -Name "(Default)" -Value "Directory"
ParserError:
Line |
   4 |  ---
     |     ~
     | Missing expression after unary operator '-'.
PS C:\Windows\System32> # 强制设定文件夹通过 Explorer.exe 打开
>> $regPath = "Registry::HKEY_CLASSES_ROOT\Folder\shell\open\command"
>> if (!(Test-Path $regPath)) {
>>     New-Item -Path $regPath -Force
>> }
>> Set-ItemProperty -Path $regPath -Name "(Default)" -Value 'C:\Windows\explorer.exe "%1"'

    Hive: HKEY_CLASSES_ROOT\Folder\shell\open

Name                           Property
----                           --------
command

PS C:\Windows\System32>
source: gemini
date: 2026-05-09
category: 项目管理
tags: [gemini, 项目管理]
---

## PowerShell 7.6.1
PS C:\Windows\System32> assoc .folder=Folder
assoc: The term 'assoc' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> assoc .directory=Directory
assoc: The term 'assoc' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> cmd /c "assoc .folder=Folder"
.folder=Folder
PS C:\Windows\System32> cmd /c "assoc .directory=Directory"
>>     ```
>>
>> ---
>>
>> ### 方案二：使用 PowerShell 原生命令修改注册表
>> 如果你想用更“PowerShell”的方式从底层修复，可以执行以下命令，这会直接修改注册表中负责文件关联的部分：
>>
>> ```powershell
>> # 修复 .folder 关联
>> if (!(Test-Path "Registry::HKEY_CLASSES_ROOT\.folder")) {
>>     New-Item -Path "Registry::HKEY_CLASSES_ROOT\.folder" -Force
>> }
>> Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\.folder" -Name "(Default)" -Value "Folder"
>>
>> # 修复 .directory 关联
>> if (!(Test-Path "Registry::HKEY_CLASSES_ROOT\.directory")) {
>>     New-Item -Path "Registry::HKEY_CLASSES_ROOT\.directory" -Force
>> }
>> Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\.directory" -Name "(Default)" -Value "Directory"
ParserError:
Line |
   4 |  ---
     |     ~
     | Missing expression after unary operator '-'.
PS C:\Windows\System32> # 强制设定文件夹通过 Explorer.exe 打开
>> $regPath = "Registry::HKEY_CLASSES_ROOT\Folder\shell\open\command"
>> if (!(Test-Path $regPath)) {
>>     New-Item -Path $regPath -Force
>> }
>> Set-ItemProperty -Path $regPath -Name "(Default)" -Value 'C:\Windows\explorer.exe "%1"'

    Hive: HKEY_CLASSES_ROOT\Folder\shell\open

Name                           Property
----                           --------
command

PS C:\Windows\System32>

看来你已经成功执行了最关键的修复命令！虽然中间因为复制了多余的说明文字导致了 ParserError 报错，但最后的方案三（强制设定 Explorer.exe 路径）已经显示成功创建并修改了注册表项。
既然命令已经运行成功，请按以下步骤验证并完成修复：
1. 刷新系统环境
注册表的修改有时不会立即生效。请执行以下操作之一：

最推荐： 直接重启电脑。
快速尝试： 在刚才的 PowerShell 窗口中输入 taskkill /f /im explorer.exe; start explorer.exe 并回车，这会强制重启资源管理器进程。

2. 检查结果
重启后，尝试双击桌面上的文件夹。如果依然弹出 image_aeb9db.png 中的关联错误，请运行下面最后一行“补漏”命令，因为有些系统不仅识别 Folder，还会识别 Directory 类的打开动作：
# 修复 Directory 类的默认打开动作
$dirPath = "Registry::HKEY_CLASSES_ROOT\Directory\shell\open\command"
if (!(Test-Path $dirPath)) { New-Item -Path $dirPath -Force }
Set-ItemProperty -Path $dirPath -Name "(Default)" -Value 'C:\Windows\explorer.exe "%1"'


3. 深度排查：为什么会发生这种情况？
由于你正在开发 “Semantic Folder Icon Visualization” 项目，这个工具在自动化修改文件夹图标或视觉展示时，极有可能涉及对 HKEY_CLASSES_ROOT\Folder 或 HKEY_CLASSES_ROOT\Directory 下 ShellEx（壳层扩展）的修改。
建议：

检查你的 Python 审计工具或 AI Agent 脚本中，是否有对 shell\open\command 键值的写入操作。
如果你使用了 ThinkPad P15V 上的某些第三方系统优化软件，请确认它们没有开启“禁止资源管理器多窗口”或类似的精简功能，这些功能经常会破坏注册表关联。

目前看你的操作已经修复了核心键值，重启后应该就能恢复正常了！如果还是不行，那可能需要检查具体的 UserChoice 覆盖项，我会再帮你分析。

---
*从 Gemini 导出，2026-05*
