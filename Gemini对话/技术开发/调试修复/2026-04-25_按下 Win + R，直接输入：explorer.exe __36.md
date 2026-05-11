---
title: 按下 Win + R，直接输入：explorer.exe /e,::{20D04FE0-3AEA-1069-A2D8-08002B30309D}
source: gemini
date: 2026-04-25
category: 技术开发
subcategory: 调试修复
old_category: 项目管理
tags: [gemini, 技术开发, 调试修复]
---

## 按下 Win + R，直接输入：explorer.exe /e,::{20D04FE0-3AEA-1069-A2D8-08002B30309D}

## 按下 Win + R，直接输入：explorer.exe /e,::{20D04FE0-3AEA-1069-A2D8-08002B30309D}
这步输入后，可以打开资源管理

既然这行命令能成功打开，说明 explorer.exe 的程序本身和核心组件都是健康的，只是 Win + E 这个快捷键在系统层面的“指向”断了。
在 Windows 11 中，Win + E 默认指向的是“主页”（Home）或者“快速访问”。如果这个特定位置的数据库坏了，快捷键就会失效，但通过命令直接打开“此电脑”却没问题。
我们做最后两步“精准手术”来打通这个快捷键：
1. 修改资源管理器的默认打开位置
有时候 Win + E 失效是因为它尝试打开“主页”，而主页缓存崩溃了。我们把它改成默认打开“此电脑”：

通过你刚才的方式打开资源管理器。
点击顶部的 三个点 (...) -> 选项。
在“常规”选项卡中，将第一项 “打开文件资源管理器以：” 从“主页”改为 “此电脑”。
点击确定，然后按下 Win + E 测试。


2. 清除资源管理器历史缓存 (最玄学的有效方案)
如果位置设置没错，那很可能是资源管理器的“快速访问”列表里有一个损坏的项目，导致 Win + E 初始化时直接闪退或无响应。

同样在刚才的 “文件资源管理器选项” 窗口。
在下方的“隐私”栏目里，点击 “清除” 按钮（清除文件资源管理器历史记录）。
同时取消勾选“在快速访问中显示最近使用的文件”和“显示常用文件夹”。
点击确定。


3. 强行修复 ShellExecute 钩子
如果上述依然不行，说明注册表中负责响应 Win + E 的一个特殊 UUID 挂钩掉了。请在管理员 CMD 窗口中运行这最后一段代码：
reg add "HKCU\Software\Classes\CLSID\{52205fd8-5dfb-4472-8046-3306e0f391a2}\shell\opennewwindow\command" /ve /t REG_EXPAND_SZ /d "%%SystemRoot%%\explorer.exe" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\DelegateFolders\{20D04FE0-3AEA-1069-A2D8-08002B30309D}" /ve /d "This PC" /f

运行完后，请务必在任务管理器里再次“重新启动”一次 Windows 资源管理器 进程。

最后的排查（如果还是不行）：
如果执行完这些 Win + E 还是没反应，请回想一下：你的电脑上是否安装了 ThinkPad 自带的键盘映射工具，或者是类似 PowerToys、AutoHotKey 这种改键软件？ 因为你用的是 ThinkPad 系列，有时候系统自带的“热键支持驱动”会覆盖掉 Windows 的默认快捷键。如果这几步走完还是没反应，通常就是这类外部驱动在搞鬼了。
现在按下 Win + E 有反应了吗？

---
*从 Gemini 导出，2026-04*

---
*Gemini · 技术开发 / 调试修复 · 2026-04-25*
