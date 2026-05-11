---
title: Windows PowerShell
source: gemini
date: 2026-05-02
category: 系统运维
subcategory: PowerShell
old_category: 编程开发
tags: [gemini, 系统运维, PowerShell]
---

## Windows PowerShell

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> npm install -g webcrack
npm warn deprecated prebuild-install@7.1.3: No longer maintained. Please contact the author of the relevant native addon; alternatives are available.
npm warn cleanup Failed to remove some directories [
npm warn cleanup   [
npm warn cleanup     'C:\\Users\\think\\AppData\\Roaming\\npm\\node_modules\\webcrack\\node_modules\\@babel\\traverse',
npm warn cleanup     [Error: EPERM: operation not permitted, rmdir 'C:\Users\think\AppData\Roaming\npm\node_modules\webcrack\node_modules\@babel\traverse'] {
npm warn cleanup       errno: -4048,
npm warn cleanup       code: 'EPERM',
npm warn cleanup       syscall: 'rmdir',
npm warn cleanup       path: 'C:\\Users\\think\\AppData\\Roaming\\npm\\node_modules\\webcrack\\node_modules\\@babel\\traverse'
npm warn cleanup     }
npm warn cleanup   ],
npm warn cleanup   [
npm warn cleanup     'C:\\Users\\think\\AppData\\Roaming\\npm\\node_modules\\webcrack',
npm warn cleanup     [Error: EPERM: operation not permitted, rmdir 'C:\Users\think\AppData\Roaming\npm\node_modules\webcrack\node_modules\tar-fs\test'] {
npm warn cleanup       errno: -4048,
npm warn cleanup       code: 'EPERM',
npm warn cleanup       syscall: 'rmdir',
npm warn cleanup       path: 'C:\\Users\\think\\AppData\\Roaming\\npm\\node_modules\\webcrack\\node_modules\\tar-fs\\test'
npm warn cleanup     }
npm warn cleanup   ],
npm warn cleanup   [
npm warn cleanup     'C:\\Users\\think\\AppData\\Roaming\\npm\\node_modules\\webcrack\\node_modules\\tar-fs',
npm warn cleanup     [Error: EPERM: operation not permitted, rmdir 'C:\Users\think\AppData\Roaming\npm\node_modules\webcrack\node_modules\tar-fs\test'] {
npm warn cleanup       errno: -4048,
npm warn cleanup       code: 'EPERM',
npm warn cleanup       syscall: 'rmdir',
npm warn cleanup       path: 'C:\\Users\\think\\AppData\\Roaming\\npm\\node_modules\\webcrack\\node_modules\\tar-fs\\test'
npm warn cleanup     }
npm warn cleanup   ]
npm warn cleanup ]
npm error code 1
npm error path C:\Users\think\AppData\Roaming\npm\node_modules\webcrack\node_modules\isolated-vm
npm error command failed
npm error command C:\WINDOWS\system32\cmd.exe /d /s /c prebuild-install || (node-gyp rebuild --release -j max && node-gyp clean)
npm error prebuild-install warn install read ECONNRESET
npm error gyp info it worked if it ends with ok
npm error gyp info using node-gyp@10.1.0
npm error gyp info using node@20.18.0 | win32 | x64
npm error gyp info find Python using Python version 3.13.9 found at "C:\Users\think\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
npm error gyp http GET https://nodejs.org/download/release/v20.18.0/node-v20.18.0-headers.tar.gz
npm error gyp http 200 https://nodejs.org/download/release/v20.18.0/node-v20.18.0-headers.tar.gz
npm error gyp http GET https://nodejs.org/download/release/v20.18.0/SHASUMS256.txt
npm error gyp http GET https://nodejs.org/download/release/v20.18.0/win-x64/node.lib
npm error gyp http 200 https://nodejs.org/download/release/v20.18.0/SHASUMS256.txt
npm error gyp http 200 https://nodejs.org/download/release/v20.18.0/win-x64/node.lib
npm error gyp ERR! find VS
npm error gyp ERR! find VS msvs_version not set from command line or npm config
npm error gyp ERR! find VS VCINSTALLDIR not set, not running in VS Command Prompt
npm error gyp ERR! find VS could not use PowerShell to find Visual Studio 2017 or newer, try re-running with '--loglevel silly' for more details.
npm error gyp ERR! find VS
npm error gyp ERR! find VS Failure details: undefined
npm error gyp ERR! find VS could not use PowerShell to find Visual Studio 2017 or newer, try re-running with '--loglevel silly' for more details.
npm error gyp ERR! find VS
npm error gyp ERR! find VS Failure details: undefined
npm error gyp ERR! find VS could not use PowerShell to find Visual Studio 2017 or newer, try re-running with '--loglevel silly' for more details.
npm error gyp ERR! find VS
npm error gyp ERR! find VS Failure details: undefined
npm error gyp ERR! find VS could not use PowerShell to find Visual Studio 2017 or newer, try re-running with '--loglevel silly' for more details.
npm error gyp ERR! find VS
npm error gyp ERR! find VS Failure details: undefined
npm error gyp ERR! find VS not looking for VS2015 as it is only supported up to Node.js 18
npm error gyp ERR! find VS not looking for VS2013 as it is only supported up to Node.js 8
npm error gyp ERR! find VS
npm error gyp ERR! find VS **************************************************************
npm error gyp ERR! find VS You need to install the latest version of Visual Studio
npm error gyp ERR! find VS including the "Desktop development with C++" workload.
npm error gyp ERR! find VS For more information consult the documentation at:
npm error gyp ERR! find VS https://github.com/nodejs/node-gyp#on-windows
npm error gyp ERR! find VS **************************************************************
npm error gyp ERR! find VS
npm error gyp ERR! configure error
npm error gyp ERR! stack Error: Could not find any Visual Studio installation to use
npm error gyp ERR! stack at VisualStudioFinder.fail (E:\Program Files\nodejs\node_modules\npm\node_modules\node-gyp\lib\find-visualstudio.js:116:11)
npm error gyp ERR! stack at VisualStudioFinder.findVisualStudio (E:\Program Files\nodejs\node_modules\npm\node_modules\node-gyp\lib\find-visualstudio.js:72:17)
npm error gyp ERR! stack at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
npm error gyp ERR! stack at async createBuildDir (E:\Program Files\nodejs\node_modules\npm\node_modules\node-gyp\lib\configure.js:95:26)
npm error gyp ERR! stack at async run (E:\Program Files\nodejs\node_modules\npm\node_modules\node-gyp\bin\node-gyp.js:81:18)
npm error gyp ERR! System Windows_NT 10.0.22621
npm error gyp ERR! command "E:\\Program Files\\nodejs\\node.exe" "E:\\Program Files\\nodejs\\node_modules\\npm\\node_modules\\node-gyp\\bin\\node-gyp.js" "rebuild" "--release" "-j" "max"
npm error gyp ERR! cwd C:\Users\think\AppData\Roaming\npm\node_modules\webcrack\node_modules\isolated-vm
npm error gyp ERR! node -v v20.18.0
npm error gyp ERR! node-gyp -v v10.1.0
npm error gyp ERR! not ok
npm error A complete log of this run can be found in: C:\Users\think\AppData\Local\npm-cache\_logs\2026-05-02T02_10_12_738Z-debug-0.log
PS C:\Users\think>

看来我们在安装 webcrack 时撞上了一块“硬骨头”。这个报错是因为 webcrack 的一个核心依赖项 isolated-vm 需要在你的电脑上编译 C++ 代码，而你的 Windows 系统目前缺少编译环境（Visual Studio 和 C++ 工作负载）。
对于只想快速查看插件逻辑的你来说，去安装好几个 GB 的 Visual Studio 可能太沉重了。咱们换两个更轻量、不报错的替代方案：

方案 A：使用 js-beautify（仅美化，不反混淆）
如果插件代码只是被压缩了（去掉了空格和换行），没有进行深度混淆，这个工具就足够了。

安装：
npm install -g js-beautify


使用：
进入插件目录，运行：
js-beautify main.js -o readable.js



方案 B：使用在线反混淆工具（最省事）
既然本地安装环境比较折腾，我们可以直接利用现成的在线解密引擎，效果通常比本地脚本还好：

打开网站： deobfuscate.io 或 webcrack.netlify.app（这是 webcrack 的在线版，不需要安装）。
操作： 把你的 main.js 代码全选复制，粘贴进去。
结果： 点击转换，它会自动帮你把混淆的变量名还原成更有意义的逻辑，并整理好格式。


关于 Defuddle 的小提醒
看到你图片中尝试运行了我之前给出的示例命令，结果出现了 404 Not Found。这是因为 https://example.com/rules 只是一个我举例用的占位符。
如果你想测试 Defuddle 的采集能力，可以试试采集一个真实的短视频平台规则页面（例如抖音或微信视频号的官方公告页）。

建议操作路径
由于你目前的任务是配置 Obsidian 插件和研究平台规则，我建议：

代码分析： 直接用 webcrack 在线版 处理那个 main.js。
环境清理： 既然 webcrack 本地安装失败且留下了报错碎屑，你可以运行 npm uninstall -g webcrack 稍微清理一下，以免占用空间。

你现在最想看清逻辑的是哪个插件？我可以帮你看看它的代码有没有什么特殊的“坑”。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-02*
