# E 盘清理方案

## 1. 重复安装包识别

| 文件名 | 出现次数 | 所在目录 |
|--------|---------|---------|
| payload.vsix | x713 | ProgramData/Microsoft/Azure.Storage.Emulator,version=18.5.27.25453,productarch=neutral<br>ProgramData/Microsoft/Microsoft.Azure.DataLake.Tools.VisualStudio.Extension,version=2.6.5000.0<br>ProgramData/Microsoft/Microsoft.Build,version=18.5.4.2618101,chip=neutral,language=neutral<br>ProgramData/Microsoft/Microsoft.Build.Dependencies,version=18.5.11709.182,productarch=neutral<br>ProgramData/Microsoft/Microsoft.CodeAnalysis.Compilers,version=5.5.0.2620813,productarch=x64<br>...等 713 个位置 |
| NetCoreCheck.exe | x40 | Program Files/Microsoft Visual Studio/MSBuild/Microsoft/VisualStudio/BootstrapperPackages/net10coreruntime_arm64<br>Program Files/Microsoft Visual Studio/MSBuild/Microsoft/VisualStudio/BootstrapperPackages/net10coreruntime_x64<br>Program Files/Microsoft Visual Studio/MSBuild/Microsoft/VisualStudio/BootstrapperPackages/net10coreruntime_x86<br>Program Files/Microsoft Visual Studio/MSBuild/Microsoft/VisualStudio/BootstrapperPackages/net10desktopruntime_arm64<br>Program Files/Microsoft Visual Studio/MSBuild/Microsoft/VisualStudio/BootstrapperPackages/net10desktopruntime_x64<br>...等 40 个位置 |
| unins000.exe | x17 | Program Files (x86)/Antigravity<br>Program Files (x86)/PixPin<br>Program Files (x86)/softmove/AtomSDKInstaller/3<br>Program Files (x86)/softmove/Caesium Image Compressor version 2.8.2/188<br>Program Files (x86)/softmove/CodeBuddy CN (User)/91<br>...等 17 个位置 |
| elevate.exe | x14 | Program Files (x86)/ByteDance/7.8.0/resources<br>Program Files (x86)/softmove/NeatConverter 4.0.1/resources<br>Program Files (x86)/softmove/NeatReader 9.0.11/resources<br>Program Files (x86)/softmove/Xmind 26.2.4171/resources<br>Program Files (x86)/softmove/boardmix/resources<br>...等 14 个位置 |
| Uninstall.exe | x12 | Program Files (x86)/softmove/QQ/24<br>Program Files (x86)/softmove/Tribler/25<br>Program Files (x86)/softmove/Windows系统修复大师/22<br>Program Files (x86)/softmove/微信/29<br>Program Files (x86)/softmove/招行U-BANK/12<br>...等 12 个位置 |
| swlicservinst.exe | x12 | Program Files/SOLIDWORKS Corp/SOLIDWORKS CAM/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Composer/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Electrical/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Flow Simulation/binCFW/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Inspection/PDF/setup/i386<br>...等 12 个位置 |
| uninstall.exe | x11 | Program Files (x86)/DAUM/PotPlayer<br>Program Files (x86)/PotPlayer<br>Program Files (x86)/Steam<br>Program Files (x86)/softmove/193<br>Program Files (x86)/softmove/7.67.9/launch<br>...等 11 个位置 |
| swactwiz.exe | x10 | Program Files/SOLIDWORKS Corp/SOLIDWORKS CAM/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Composer/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Electrical/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Flow Simulation/binCFW/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Inspection/PDF/setup/i386<br>...等 10 个位置 |
| swinstactsvc.exe | x10 | Program Files/SOLIDWORKS Corp/SOLIDWORKS CAM/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Composer/bin<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Composer/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Electrical/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Flow Simulation/binCFW/i386<br>...等 10 个位置 |
| ef6.exe | x10 | Program Files (x86)/Microsoft Visual Studio/Packages/EntityFramework.6.4.4/net40<br>Program Files (x86)/Microsoft Visual Studio/Packages/EntityFramework.6.4.4/net40/any<br>Program Files (x86)/Microsoft Visual Studio/Packages/EntityFramework.6.4.4/net45<br>Program Files (x86)/Microsoft Visual Studio/Packages/EntityFramework.6.4.4/net45/any<br>Program Files (x86)/Microsoft Visual Studio/Packages/EntityFramework.6.5.1/net40<br>...等 10 个位置 |
| OpenConsole.exe | x9 | Program Files (x86)/Antigravity/resources/node_modules/node-pty/build<br>Program Files/Accio/app.asar.unpacked/node-pty<br>Program Files/Accio/app.asar.unpacked/node-pty/build<br>Program Files/Accio/app.asar.unpacked/node-pty/prebuilds<br>Program Files/Accio/app.asar.unpacked/node-pty/win10-arm64<br>...等 9 个位置 |
| ffmpeg.exe | x9 | Program Files (x86)/JianyingPro/10.5.0.13988<br>Program Files (x86)/softmove/FFmpeg/bin<br>Program Files (x86)/softmove/VeryCapture 1.9.4.0/27<br>Program Files/DataTool/extraResources<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Flow Simulation/binCFW<br>...等 9 个位置 |
| rg.exe | x9 | Program Files (x86)/Antigravity/resources/node_modules/@vscode/ripgrep/bin<br>Program Files (x86)/Tencent/code/node_modules/@vscode/ripgrep/bin<br>Program Files (x86)/Tencent/code/node_modules/vscode-ripgrep/bin<br>Program Files (x86)/softmove/CodeBuddy CN (User)/resources/node_modules/@vscode/ripgrep/bin<br>Program Files/WorkBuddy/cli/ripgrep<br>...等 9 个位置 |
| uninst.exe | x9 | Program Files (x86)/ByteDance/7.8.0<br>Program Files (x86)/ByteDance/douyin<br>Program Files (x86)/FastStone Image Viewer<br>Program Files (x86)/JianyingPro<br>Program Files (x86)/JianyingPro/10.5.0.13988/Service<br>...等 9 个位置 |
| python.exe | x8 | Excel_trae/.venv<br>Program Files (x86)/Microsoft Visual Studio/Android/AndroidNDK/toolchains/python3<br>Program Files/DataTool/Lib/venv/nt<br>Program Files/DataTool/python<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS/Simulation/Topology<br>...等 8 个位置 |
| pythonw.exe | x8 | Excel_trae/.venv<br>Program Files (x86)/Microsoft Visual Studio/Android/AndroidNDK/toolchains/python3<br>Program Files/DataTool/Lib/venv/nt<br>Program Files/DataTool/python<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS/Simulation/Topology<br>...等 8 个位置 |
| winpty-agent.exe | x8 | Program Files (x86)/Antigravity/resources/node_modules/node-pty/build/Release<br>Program Files (x86)/Tencent/code/node_modules/node-pty-node/build<br>Program Files (x86)/Tencent/code/node_modules/node-pty/build<br>Program Files (x86)/softmove/CodeBuddy CN (User)/resources/node_modules/node-pty/build<br>Program Files/Accio/app.asar.unpacked/node-pty/prebuilds/win32-x64<br>...等 8 个位置 |
| swactwizhelpersc.exe | x8 | Program Files/SOLIDWORKS Corp/SOLIDWORKS CAM/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Composer/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Electrical/bin/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Inspection/PDF/setup/i386<br>Program Files/SOLIDWORKS Corp/SOLIDWORKS Plastics/setup/i386<br>...等 8 个位置 |
| claude.exe | x7 | ClaudeEnvironment/@anthropic-ai<br>ClaudeEnvironment/@anthropic-ai/bin<br>ClaudeEnvironment/@gsd-build/@anthropic-ai/claude-agent-sdk-win32-x64<br>ClaudeEnvironment/npm_cache/@anthropic-ai/claude-agent-sdk-win32-x64<br>ClaudeEnvironment/npm_cache/@anthropic-ai/claude-agent-sdk-win32-x64@0.2.117@@@1<br>...等 7 个位置 |
| notification_helper.exe | x7 | IMA/143.0.7499.4409<br>Program Files (x86)/Tencent/微信web开发者工具<br>Program Files (x86)/softmove/Brave/148.1.90.121<br>Program Files (x86)/softmove/Google Chrome/147.0.7727.138<br>Program Files (x86)/softmove/Yandex/25.12.0.2197<br>...等 7 个位置 |
| rc.exe | x7 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Program Files/Microsoft Visual Studio/SDK/SDK/bin<br>Windows Kits/bin/10.0.26100.0/arm64<br>...等 7 个位置 |
| makeappx.exe | x7 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/App Certification Kit<br>Windows Kits/bin/10.0.26100.0/arm64<br>...等 7 个位置 |
| signtool.exe | x7 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/App Certification Kit<br>Windows Kits/bin/10.0.26100.0/arm64<br>...等 7 个位置 |
| 7z.exe | x6 | Program Files (x86)/softmove/全能王打印机驱动安装助手/common<br>Program Files (x86)/softmove/微信应用数据4.1/CourgettePatch<br>Program Files/7-Zip<br>Program Files/Microsoft Visual Studio/Common7/IDE/Extensions/Microsoft/Maui/Maui.VisualStudio/7-Zip<br>Program Files/i4Tools9/files/patchtools<br>...等 6 个位置 |
| git.exe | x6 | Program Files/Git/bin<br>Program Files/Git/cmd<br>Program Files/Git/mingw64/bin<br>Program Files/Git/mingw64/libexec/git-core<br>Program Files/Microsoft Visual Studio/Common7/IDE/CommonExtensions/Microsoft/TeamFoundation/Git/cmd<br>...等 6 个位置 |
| link.exe | x6 | Program Files/Git/bin<br>Program Files/Microsoft Visual Studio/SDK/bin<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/Hostx64/x64<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/Hostx64/x86<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/x64<br>...等 6 个位置 |
| mspdbsrv.exe | x6 | Program Files/Microsoft Visual Studio/Common7/IDE<br>Program Files/Microsoft Visual Studio/SDK/bin<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/Hostx64/x64<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/Hostx64/x86<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/x64<br>...等 6 个位置 |
| TailoredDeploy.exe | x6 | Program Files/Microsoft Visual Studio/Common7/IDE<br>Program Files/Microsoft Visual Studio/Common7/IDE/Remote Debugger/x64<br>Program Files/Microsoft Visual Studio/Common7/IDE/Remote Debugger/x86<br>Program Files/Microsoft Visual Studio/CoreCon/Binaries/Windows10RemoteTools<br>Program Files/Microsoft Visual Studio/CoreCon/Binaries/Windows10RemoteTools/arm64<br>...等 6 个位置 |
| llvm-symbolizer.exe | x6 | Program Files (x86)/Microsoft Visual Studio/Android/AndroidNDK/toolchains/bin<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/HostArm64<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/Hostx64/x64<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/Hostx64/x86<br>Program Files/Microsoft Visual Studio/VC/Tools/bin/x64<br>...等 6 个位置 |
| ComparePackage.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| DeployUtil.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| makecat.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| MakeCert.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| makepri.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| mc.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| mdmerge.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| midl.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| midlc.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| midlrt.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |
| mt.exe | x6 | Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/arm64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x64<br>Program Files (x86)/Microsoft Visual Studio/NuGetPackages/bin/x86<br>Windows Kits/bin/10.0.26100.0/arm64<br>Windows Kits/bin/10.0.26100.0/x64<br>...等 6 个位置 |

## 2. WeChat 文件分析

总文件数: **38,127**

目录数: 3776

| 扩展名 | 数量 |
|--------|------|
| .dat | 28,913 |
|  | 3,692 |
| .jpg | 2,076 |
| .pdf | 498 |
| .js | 350 |
| .css | 311 |
| .png | 293 |
| .json | 245 |
| .dll | 243 |
| .tmp | 183 |
| .crc | 159 |
| .svg | 114 |
| .db | 78 |
| .old | 67 |
| .wxapkg | 61 |

最大 WeChat 目录:
- Users/Documents/WeChat Files/FileStorage/MsgAttach/574af1eeb01c218da477e6d5795b190b/2025-03: 1,607 files
- Users/Documents/WeChat Files/FileStorage/MsgAttach/574af1eeb01c218da477e6d5795b190b/2025-04: 1,394 files
- Program Files (x86)/softmove/微信应用数据4.1/radium/profiles/multitab_0a0db17e0793acdfc016f6e242a30092/Cache: 1,255 files
- Users/Documents/WeChat Files/FileStorage/MsgAttach/574af1eeb01c218da477e6d5795b190b/2025-02: 929 files
- Users/Documents/WeChat Files/FileStorage/MsgAttach/33ce7b8714baebd5a665efde2a3a60cd/2025-04: 745 files
- Users/Documents/WeChat Files/FileStorage/MsgAttach/33ce7b8714baebd5a665efde2a3a60cd: 728 files
- Users/Documents/WeChat Files/FileStorage/Cache: 658 files
- Users/Documents/WeChat Files/FileStorage/MsgAttach/7e5e2ded5507ceb4327ba17e74ba2da2/2024-12: 537 files
- Users/Documents/WeChat Files/FileStorage/MsgAttach/02ae80b5d10003dd7cea1a02bcf0cead/Image/2024-12: 416 files
- Users/Documents/WeChat Files/FileStorage/Sns: 413 files

## 3. Python 缓存文件 (__pycache__/.pyc)

总数: **31,402** 个 .pyc/__pycache__ 文件

最大缓存目录:
- Users/AppData/Local/Python/Lib/test: 1,494 files
- Users/AppData/Local/Python/Lib: 507 files
- Users/AppData/Local/Python/Lib/encodings: 366 files
- Users/AppData/Local/Python/Lib/site-packages/pygments/lexers: 259 files
- Users/AppData/Local/Python/Lib/site-packages/numba/tests: 223 files
- Users/AppData/Local/Python/Lib/site-packages/openai/types/responses: 199 files
- Users/AppData/Local/Python/Lib/idlelib/idle_test: 195 files
- Users/AppData/Local/Python/Lib/idlelib: 180 files
- Users/AppData/Local/Python/Lib/ctypes/test: 159 files
- Users/AppData/Local/Python/Lib/lib2to3/fixes: 159 files
- Users/AppData/Local/Python/Lib/site-packages/modelscope/pipelines/cv: 155 files
- Users/AppData/Local/Python/Lib/site-packages/openai/types/realtime: 155 files
- venv/Lib/modelscope/pipelines/cv: 155 files
- Users/AppData/Local/Python/Lib/site-packages/pyasn1_modules: 132 files
- Users/AppData/Local/Python/Lib/distutils/tests: 129 files

## 4. AI Work 重复图片

AI Work 目录共有 7,458 文件，无重复图片


## 5. E:\ 根目录杂乱文件

根目录共 **47** 个文件

| 扩展名 | 数量 |
|--------|------|
| .png | 40 |
| .bat | 2 |
| .txt | 2 |
| (无扩展名) | 1 |
| .py | 1 |
| .doc | 1 |

文件示例:
- 1.png
- 2.png
- 3.png
- A.png
- B.png
- C.png
- EF Nuker.bat
- E_Files_List.txt
- WF Nuker.bat
- excel_crud_tool.py
- 北京乐知学计划研究方案（代码）.txt
- 卷序列号为 BC7D-39E0
- 屏幕截图 2026-01-17 182553.png
- 屏幕截图 2026-01-17 182611.png
- 屏幕截图 2026-01-17 182936.png
- 屏幕截图 2026-01-17 183100.png
- 屏幕截图 2026-01-17 183203.png
- 屏幕截图 2026-01-17 184201.png
- 屏幕截图 2026-01-17 184223.png
- 屏幕截图 2026-01-17 184235.png

## 6. E:\Backup 内容

Backup 目录共 **1,912** 个文件

| 扩展名 | 数量 |
|--------|------|
| .mp4 | 1543 |
| .pdf | 148 |
| .docx | 58 |
| .jpg | 44 |
| .mov | 34 |
| .png | 19 |
| .xlsx | 18 |
| .jpeg | 11 |
| .pptx | 9 |
| .webp | 7 |

子目录:
- bilibili
- documents
- pictures
- programs
- videos
- 丝绸之音-国际青少年音乐节
- 中国素女经
- 五月初阳学校
- 伟大的嬗变
- 倪海厦
- 内蒙古普通高中学生综合素质评价
- 冰与火之歌
- 刘松-机电工程师-河北建筑工程学院
- 动画视频
- 学习方法探索（乐知）
- 彤彤测试报告
- 杨貌病历
- 游戏阶段治疗方案
- 生物必修课（预习）
- 纳瓦尔系统

## 7. node_modules 分布

node_modules 总文件数: **47,571**

含 node_modules 的项目/目录数: 41

- ClaudeEnvironment/@fission-ai: 2051 files
- ClaudeEnvironment/ecc-universal: 569 files
- ClaudeEnvironment/npm_cache: 2 files
- ClaudeEnvironment/npm_cache/705bc6b22212b352: 1 files
- Program Files (x86)/Antigravity/resources: 13003 files
- Program Files (x86)/Antigravity/resources/app: 1 files
- Program Files (x86)/Antigravity/resources/extensions: 121 files
- Program Files (x86)/ByteDance/7.8.0/resources/app.asar.unpacked: 130 files
- Program Files (x86)/Downloads/superpowers/resources: 3122 files
- Program Files (x86)/Tencent/code: 2046 files
- Program Files (x86)/Tencent/code/js/common/fileutils: 95 files
- Program Files (x86)/Tencent/code/js/libs/extensions: 1409 files
- Program Files (x86)/Tencent/code/js/libs/extensions/christian-kohler.path-intellisense-2.3.0: 28 files
- Program Files (x86)/Tencent/code/js/libs/extensions/emmet-wxml/vscode-emmet-helper: 4 files
- Program Files (x86)/Tencent/code/js/libs/extensions/hookyqr.beautify-1.5.1: 151 files
- Program Files (x86)/Tencent/code/js/libs/extensions/ms-azuretools.vscode-docker-1.8.1/dist: 1 files
- Program Files (x86)/Tencent/code/js/libs/extensions/ms-vscode.node-debug2: 252 files
- Program Files (x86)/Tencent/code/js/libs/extensions/universal-path-intellisense: 28 files
- Program Files (x86)/Tencent/code/package.nw: 2 files
- Program Files (x86)/softmove/CodeBuddy CN (User)/resources: 248 files

## 清理优先级建议

| 优先级 | 项目 | 文件数 | 风险 | 建议操作 |
|--------|------|--------|------|---------|
| P0 | __pycache__ / .pyc | ~31K | 安全 | 全局删除，Python 自动重建 |
| P0 | E:\ 根目录杂文件 | ~40 | 安全 | 分类归入对应文件夹 |
| P1 | AI Work 重复图片 | ~1K+ | 低风险 | 保留一份，删除同名副本 |
| P1 | node_modules | ~60K+ | 低风险 | 项目用 `bun install` 重建 |
| P2 | WeChat 附件 | ~15K | 中风险 | 备份后清理旧聊天存档 |
| P2 | Backup 内容 | ~1.5K | 中风险 | 逐一确认后再删 |
| P3 | 重复安装包 | 待确认 | 低风险 | 保留最新版 |