---
title: C:\Windows\System32>reg delete "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell" /f
source: gemini
date: 2026-04-25
category: 系统运维
subcategory: 部署同步
old_category: 项目管理
tags: [gemini, 系统运维, 部署同步]
---

## C:\Windows\System32>reg delete "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell" /f

## C:\Windows\System32>reg delete "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell" /f
操作成功完成。

C:\Windows\System32>reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.lnk\UserChoice" /f
错误: 系统找不到指定的注册表项或值。

看来我们离真相已经非常近了：UserChoice 找不到是好事，说明没有错误的第三方强制关联；而第一个命令执行成功，说明我们已经重置了当前用户的 Shell 视图。
既然 Win + E 还是没动静，但命令能开，这说明 Windows 热键监听服务（Shell Hotkey Handler） 已经把 Win + E 过滤掉或者“忘记”了它的存在。
请尝试最后两个“非注册表”层面的绝招，这通常能解决 99% 的热键顽疾：
1. 强制重置资源管理器“打开位置”缓存
有些时候 Win + E 并不是没生效，而是它尝试去打开一个已经不存在的“快速访问”链接导致卡死。

按下 Win + R，输入以下路径并回车：
shell:::{0628D980-5021-101E-9865-062403557467}
如果能打开“选项”窗口，点击 “清除” 历史记录。
将“打开文件资源管理器以”改为 “此电脑”。
点击确定。

2. 通过任务管理器“新建”一个无缓存的环境
这是一个非常有效的技巧：

按下 Ctrl + Shift + Esc。
找到 Windows 资源管理器，右键点击 “结束任务”（此时屏幕变黑是正常的）。
点击 “运行新任务”。
关键点： 输入 explorer.exe，但不要急着点确定，先勾选下面的 “以管理权限创建此任务”，然后再点确定。
等桌面加载出来后，再次测试 Win + E。


3. 如果依然无效，极大概率是“第三方输入法”劫持
作为常年使用 ThinkPad 处理工业项目的专业用户，你的电脑里是否有以下软件？

输入法： 检查搜狗、QQ输入法、或是某些翻译软件。它们非常喜欢占用 Win + E。
测试方法： 点击右下角的输入法图标，切换到 “英语（美国）” 或 “微软拼音”。在保持英文输入状态下，按 Win + E。


最终备选方案（如果还是没反应）：
如果连切换输入法都没用，这说明系统的 explorerframe.dll 出现了逻辑断裂。
你可以尝试一个“手动路由”法：

在桌面新建一个快捷方式。
对象位置输入：explorer.exe /e,::{20D04FE0-3AEA-1069-A2D8-08002B30309D}
命名为“此电脑”。
在这个快捷方式上右键 -> 属性 -> 快捷键。
尝试给它指定一个你习惯的其他键（比如 Ctrl + Alt + E），作为 Win + E 的临时替代品。

现在切换到纯英文输入法状态下按 Win + E，有反应吗？

---
*从 Gemini 导出，2026-04*

---
*Gemini · 系统运维 / 部署同步 · 2026-04-25*
