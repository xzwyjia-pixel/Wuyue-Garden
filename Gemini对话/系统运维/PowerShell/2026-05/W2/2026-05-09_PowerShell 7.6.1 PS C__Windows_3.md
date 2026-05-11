---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 项目管理
tags: [gemini, 系统运维, PowerShell]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> assoc .folder=Folder
assoc: The term 'assoc' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> assoc .directory=Directory
assoc: The term 'assoc' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32>

这是一个非常典型的误区：assoc 是 Windows 旧版 命令提示符 (CMD) 的内置命令，而你目前运行的是 PowerShell 7.6.1。PowerShell 并不直接识别这个命令。
既然你正在使用较新版本的 PowerShell，我们可以直接用 PowerShell 的原生命令（或者通过它调用 CMD）来解决。请尝试以下方案：
方案一：在 PowerShell 中调用 CMD 执行（最快）
你不需要切换窗口，直接在当前的 PowerShell 提示符下输入以下带有 cmd /c 前缀的命令：

修复文件夹关联：
cmd /c "assoc .folder=Folder"


修复目录关联：

    cmd /c "assoc .directory=Directory"
    ```

---

### 方案二：使用 PowerShell 原生命令修改注册表
如果你想用更“PowerShell”的方式从底层修复，可以执行以下命令，这会直接修改注册表中负责文件关联的部分：

```powershell
# 修复 .folder 关联
if (!(Test-Path "Registry::HKEY_CLASSES_ROOT\.folder")) {
    New-Item -Path "Registry::HKEY_CLASSES_ROOT\.folder" -Force
}
Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\.folder" -Name "(Default)" -Value "Folder"

# 修复 .directory 关联
if (!(Test-Path "Registry::HKEY_CLASSES_ROOT\.directory")) {
    New-Item -Path "Registry::HKEY_CLASSES_ROOT\.directory" -Force
}
Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\.directory" -Name "(Default)" -Value "Directory"


方案三：针对 ThinkPad 环境的“终极修复”
考虑到你日常处理大量的工业自动化和 AI 代理开发工作，系统环境可能比较复杂。如果上述关联修复后依然弹出 image_aeb9db.png 中的错误，这通常意味着 Folder 或 Directory 下方的 Open 命令路径 被破坏了。
请在 PowerShell 中执行以下命令，将文件夹的默认打开动作强制指向系统的资源管理器：
# 强制设定文件夹通过 Explorer.exe 打开
$regPath = "Registry::HKEY_CLASSES_ROOT\Folder\shell\open\command"
if (!(Test-Path $regPath)) {
    New-Item -Path $regPath -Force
}
Set-ItemProperty -Path $regPath -Name "(Default)" -Value 'C:\Windows\explorer.exe "%1"'

操作建议：

执行完上述任一方案后，请务必重启电脑或在任务管理器中重启 explorer.exe 进程。
鉴于你正在进行 Semantic Folder Icon Visualization 的开发，请检查该项目的脚本是否在尝试注册自定义图标处理程序时，意外覆盖了 HKEY_CLASSES_ROOT\Folder 的默认键值。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
