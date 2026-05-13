---
title: %APPDATA%\Claude打不开
source: gemini
date: 2026-05-02
category: 系统运维
tags: [gemini, 系统运维]
---

## %APPDATA%\Claude打不开

甄先生，打不开通常是因为这个文件夹还没有被系统自动创建。别担心，我们可以换一种最直接的方式，让 Claude Code 终端自己告诉我们该改哪个文件。
请在您现在的那个黑色终端窗口（如 image_03ddf8.png 所示）中输入以下命令：
/config

输入后回车，它会显示一串配置项。请留意屏幕上是否有显示 Path 或者 Config file 字样的路径。
如果 /config 没给出路径，请尝试以下操作：


手动复制路径：
请按下键盘上的 Win + R 键，在弹出的运行框里输入：
explorer %APPDATA%
（注意这里先不加 \Claude），然后回车。


寻找文件夹：
在打开的窗口里，看看有没有一个叫 Claude 的文件夹？

如果有：点进去，找 config.json。
如果没有：请看看有没有一个叫 claude-code 的文件夹。



💡 另外一个更简单的办法：
您可以直接在那个黑色终端窗口里输入以下指令，让 Claude 帮您定位：

“Where is your MCP configuration file located on my Windows machine?”

它会直接给出完整的文件路径。
找到路径后，请告诉我，或者把路径贴出来，我带您完成最后一步的“代码粘贴”。

---
*从 Gemini 导出，2026-05*
