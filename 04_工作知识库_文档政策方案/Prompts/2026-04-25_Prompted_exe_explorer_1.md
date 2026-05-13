---
title: Prompted
source: gemini
date: 2026-04-25
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

看来注册表关联修复后，系统中仍有某些深层设置或第三方拦截导致资源管理器（explorer.exe）本身被禁止执行。
这个错误窗口标题直接显示为 explorer.exe，说明问题已经从“快捷方式打不开”变成了“资源管理器程序本身无法调用”。我们需要尝试更底层的方法来解除这种“关联丢失”。

方法一：修复 .exe 可执行文件关联
有时候不仅仅是快捷方式（.lnk），连可执行文件（.exe）的系统关联也会被篡改。请再次打开管理员身份的命令提示符（CMD），输入以下命令并回车：
ftype exefile="%1" %*

方法二：利用系统自带的 sfc 修复损坏文件
如果关联没问题，可能是 explorer.exe 的核心文件损坏了。在管理员 CMD 窗口中输入：
sfc /scannow


注意： 这个过程可能需要 5-10 分钟。它会扫描并自动修复所有损坏的 Windows 系统文件。


方法三：检查注册表中的“映像劫持”（关键）
有些软件或病毒会通过注册表强行拦截 explorer.exe。我们可以检查并清理它：

按 Win + R，输入 regedit 并回车（如果弹窗报错，请尝试按 Ctrl + Shift + Esc 打开任务管理器，点击“运行新任务”，输入 regedit 并勾选“以管理权限创建”）。
导航到以下路径：
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options
在左侧文件夹列表里找有没有叫 explorer.exe 的子项。
如果有，右键删除它。
同样检查这个路径下有没有：
HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options
如果有 explorer.exe，也将其删除。


方法四：终极方案——重置“默认应用”设置
如果上述方法都无效，说明系统的默认协议关联彻底乱了：

按 Win + I 打开 设置。
点击 应用 -> 默认应用。
滚动到页面最底部，找到 “重置所有默认应用”，点击 重置。


如果执行上述操作时依然反复跳出该错误弹窗：
这通常意味着系统当前的用户配置文件（User Profile）已损坏。最快的“断后”办法是：

创建一个新的本地管理员账户，登录新账户看是否正常。如果新账户正常，直接把资料迁移过去即可。

目前执行完方法一或方法三后，情况有改善吗？

---
*从 Gemini 导出，2026-04*
