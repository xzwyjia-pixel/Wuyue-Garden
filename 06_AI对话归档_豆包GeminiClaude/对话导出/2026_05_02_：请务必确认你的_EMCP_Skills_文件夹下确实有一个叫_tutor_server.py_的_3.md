---
title: ：请务必确认你的 E:\MCP-Skills\ 文件夹下确实有一个叫 tutor_server.py 的文件。
这点应该怎么做
source: gemini
date: 2026-05-02
category: 编程开发
tags: [gemini, 编程开发]
---

## ：请务必确认你的 E:\MCP-Skills\ 文件夹下确实有一个叫 tutor_server.py 的文件。
这点应该怎么做

要确认这个文件是否存在，最直观的方法是通过文件资源管理器或者直接在 VS Code 内部查看。由于你正在搭建 AI 开发环境，确保路径和文件名完全匹配是成功运行 MCP Server 的关键。
以下是两种最简单的确认方法：
方法一：使用 VS Code 侧边栏（推荐）
既然你已经打开了 VS Code，可以直接在这里查看：

点击 VS Code 左侧菜单栏最上方的文件图标（Explorer）。
点击 "Open Folder"（打开文件夹）。
导航到 E:\MCP-Skills\ 路径并打开它。
检查右侧列表中是否显示了一个名为 tutor_server.py 的文件。

注意：请检查文件名是否有拼写错误，或者是否多了一个 .txt 后缀（比如变成了 tutor_server.py.txt）。



方法二：使用终端（最快速）
由于你之前已经在 VS Code 中打开过终端，你可以直接输入命令检查：

在 VS Code 下方的终端窗口中输入以下命令并回车：
ls E:\MCP-Skills\tutor_server.py


结果判断：

如果显示了文件名、权限和日期，说明文件已经存在。
如果提示 Cannot find path...（找不到路径），说明文件不存在或路径写错了。




如果文件夹里是空的，或者没有这个文件怎么办？
如果你发现文件夹里没有 tutor_server.py，你需要根据你获取这个 Skill 的来源进行操作：

如果是从网上下载的：请将下载好的 .py 脚本移动到 E:\MCP-Skills\ 目录下。
如果是需要自己编写的：在 VS Code 中点击“新建文件”，命名为 tutor_server.py，并将该 Skill 的源代码粘贴进去保存。

检查完后的下一步
一旦确认文件存在，别忘了点击 image_053a9c.png 顶部提示的 "Manage" -> "Trust"，这样 VS Code 才有权调用 Python 去执行这个脚本。
你现在看一眼 E:\MCP-Skills\ 文件夹，里面有东西吗？

---
*从 Gemini 导出，2026-05*
