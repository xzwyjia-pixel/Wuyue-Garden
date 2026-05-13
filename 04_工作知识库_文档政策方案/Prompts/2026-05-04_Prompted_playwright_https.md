---
title: Prompted
source: gemini
date: 2026-05-04
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

看来安装虽然成功了，但在运行初始测试时遇到了网络连接超时的问题。
报错原因分析
截图中的错误信息 Test timeout of 30000ms exceeded 以及 page.goto: ... waiting until "load" 表明：Playwright 尝试访问其官方示例网站 [https://playwright.dev/](https://playwright.dev/)，但在默认的 30 秒内没有加载成功。
这通常是因为：

网络环境限制：在国内直接访问国外服务器（playwright.dev）有时会非常慢或不稳定。
代理未配置：如果你的终端没有配置科学上网环境，浏览器内核无法建立连接。


解决方案
方法一：测试本地网站（验证工具是否正常）
为了确认 Playwright 本身没问题，你可以修改 tests/example.spec.ts 文件，将第 11 行的网址改为国内可以快速访问的地址（例如 [https://www.baidu.com](https://www.baidu.com)），然后重新运行：
npx playwright test

方法二：增加超时时间
如果只是网络慢，可以在 playwright.config.ts 中调大 timeout，或者在代码中临时修改：
await page.goto('https://playwright.dev/', { timeout: 60000 }); // 改为 60 秒

方法三：配置终端代理
如果你有代理工具，请确保在执行测试前，终端已经开启了代理：
# 以 PowerShell 为例
$env:HTTP_PROXY="http://127.0.0.1:你的端口"
$env:HTTPS_PROXY="http://127.0.0.1:你的端口"
npx playwright test

接下来建议
你现在可以按终端提示的 Ctrl+C 退出报告查看，然后尝试方法一。只要能成功打开一个国内网站，就说明你的 Playwright 环境已经彻底搭建好了。

---
*从 Gemini 导出，2026-05*
