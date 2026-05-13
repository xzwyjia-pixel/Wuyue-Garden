---
title: 文件在E盘
source: gemini
date: 2026-05-05
category: 编程开发
tags: [gemini, 编程开发]
---

## 文件在E盘

既然文件在 E盘，你需要先在终端（PowerShell）中切换盘符，然后再运行。
请按照以下命令顺序操作：
1. 在终端切换到 E 盘
在 PowerShell 窗口中直接输入：
e:

2. 进入文件夹
假设你的文件放在 E:\code 目录下，输入：
cd code

(如果不记得具体文件夹名，可以输入 ls 查看当前盘符下的所有文件)
3. 运行 Python 脚本
确保你已经把代码保存为 test_baidu.py，然后执行：
python test_baidu.py


💡 为什么之前会失败？（技术要点）

环境隔离：你在 看到的报错是因为 PowerShell 是一个命令外壳，它负责管理文件和运行程序。它不认识 Python 的内部语法（如 page.goto），它只认识 .exe 或内置命令。
解释器模式：如果你想直接在终端输入代码并立即看到结果，你需要先输入 python 并回车，进入 Python 交互模式（看到 >>> 符号），那时你粘贴的代码才会被逐行执行。但对于 Playwright 这种需要 with 语句块的复杂脚本，保存为文件运行是最稳妥的做法。

验证成果
运行成功后：

你会看到一个 Chromium 浏览器自动打开并跳转到百度。
控制台会打印出 页面标题是: 百度一下，你就知道。
E 盘 对应的文件夹里会多出一张名为 baidu_success.png 的截图。

如果你在运行 python test_baidu.py 时提示“找不到模块”，请确保你在 E 盘下也执行过 pip install playwright。

---
*从 Gemini 导出，2026-05*
