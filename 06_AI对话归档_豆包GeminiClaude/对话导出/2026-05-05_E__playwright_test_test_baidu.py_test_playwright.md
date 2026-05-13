---
title: E:\playwright_test\test_baidu.py
source: gemini
date: 2026-05-05
category: 编程开发
tags: [gemini, 编程开发]
---

## E:\playwright_test\test_baidu.py

找到了！根据你提供的路径，文件确实在 E:\playwright_test 文件夹下。
请直接在 PowerShell 中依次执行以下三行指令：
e:
cd playwright_test
python test_baidu.py

为什么之前会报错？
从你之前的截图 image_1f8e67.png 可以看到，你当时所在的路径是 E:\>（根目录），而文件藏在 playwright_test 这个子文件夹里。在命令行中，如果你不进入对应的文件夹，系统是“看不见”里面的文件的。
验证执行结果
如果一切正常：

浏览器行为：你会看到一个浏览器窗口自动弹出，打开百度首页。
控制台输出：你会看到类似 页面标题是: 百度一下，你就知道 的文字。
新文件生成：在 E:\playwright_test\ 文件夹里，你会发现多了一张名为 baidu_success.png 的图片。

温馨提示：如果运行提示缺少模块，请记得在当前目录下再执行一次 pip install playwright。

---
*从 Gemini 导出，2026-05*
