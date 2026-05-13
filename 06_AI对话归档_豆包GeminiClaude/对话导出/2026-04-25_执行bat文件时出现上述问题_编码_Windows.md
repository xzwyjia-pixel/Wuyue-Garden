---
title: 执行bat文件时出现上述问题
source: gemini
date: 2026-04-25
category: 项目管理
tags: [gemini, 项目管理]
---

## 执行bat文件时出现上述问题

出现这种满屏乱码（并且提示“不是内部或外部命令”）的原因是文件保存的编码格式不对。
Windows 系统的记事本现在默认会将文件保存为 UTF-8 编码，但是 Windows 的命令行窗口（CMD）在运行中文批处理文件时，默认识别的是 ANSI 编码。编码冲突导致系统把原本正常的命令读成了乱码，因此无法执行。
要解决这个问题非常简单，只需要重新保存一下文件的编码即可：
修复方法：更改为 ANSI 编码

重新打开文件： 在你刚才创建的 修复快捷方式.bat 文件上点击右键，选择 编辑（或者用记事本打开它）。
另存为： 在记事本左上角点击 文件 -> 另存为。
修改编码： 在弹出的保存窗口的最下方，找到 编码(E) 的下拉菜单。将默认的“UTF-8”更改为 ANSI。
保存并覆盖： 确保文件名依然是 修复快捷方式.bat，点击保存，并确认替换原有文件。
再次运行： 回到桌面，右键点击修改好编码的 .bat 文件，重新选择 以管理员身份运行 即可。


备用方案：直接在命令提示符中运行
如果修改编码后依然有报错，或者你不想折腾文件编码，你可以直接手动粘贴并执行核心的修复命令，跳过批处理文件：

按键盘上的 Win 键，搜索 cmd。
在搜索结果中找到 命令提示符，点击右侧的 以管理员身份运行。
在弹出的黑框中，将下面这 4 行核心修复命令一次性全部复制，然后右键点击黑框内部进行粘贴（粘贴后按一下回车键执行）：

assoc .lnk=lnkfile
reg add "HKCR\.lnk" /ve /d "lnkfile" /f
reg add "HKCR\lnkfile" /ve /d "Shortcut" /f
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.lnk\UserChoice" /f


执行完毕后，再输入以下两行命令（粘贴后按回车）重启资源管理器即可恢复：

taskkill /f /im explorer.exe
start explorer.exe

---
*从 Gemini 导出，2026-04*
