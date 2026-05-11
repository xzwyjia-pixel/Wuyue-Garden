---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> # 进入你的项目盘符和目录
>>
>> E:
>>
>> cd E:\MyCodeProjects
>>
>>
>>
>> # 初始化各个工具
>>
>> gsd init
>>
>> opsx init
gsd:
Line |
  11 |  gsd init
     |  ~~~
     | The term 'gsd' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
opsx:
Line |
  13 |  opsx init
     |  ~~~~
     | The term 'opsx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects>

看来虽然你已经升级到了 PowerShell 7，但系统还没能立刻“认出”新装的工具。这通常是因为 npm 安装路径没有实时刷新到当前窗口的环境变量里。
别担心，这是 Windows 环境下最常见的小波折。我们可以通过以下几步快速解决：
1. 刷新环境变量（最简单的方法）
直接关闭当前的 PowerShell 窗口，重新打开一个新的。
Windows 在启动新窗口时会重新读取 C 盘下的全局工具路径。
2. 确认安装路径是否正确
如果重启窗口还是报错，我们需要确认 npm 把东西装到哪了。请在 PowerShell 中输入：
npm config get prefix

通常返回的是 C:\Users\think\AppData\Roaming\npm。
请检查这个文件夹下是否有 gsd.cmd 和 opsx.cmd 文件。如果没有，说明之前的 npm install -g 实际上失败了。
3. 如果还是找不到，尝试使用 npx 直接运行
如果你不想折腾环境变量，直接在你的项目目录 E:\MyCodeProjects 下使用 npx 强制调用。npx 会自动寻找并运行对应的工具，即使它不在你的 PATH 里：
# 运行 GSD 初始化
npx gsd-code-first init

# 运行 OpenSpec 初始化
npx @fission-ai/openspec init


⚠️ 给 45 岁专业项目管理者的“排坑”建议
既然你已经有 Superpowers，在运行 init 之前请务必注意：

文件冲突：这些工具在执行 init 时，都会尝试在项目根目录生成一个 CLAUDE.md 文件。
不要覆盖：如果命令提示 CLAUDE.md already exists, overwrite? (y/N)，请选择 N。
手动合并：建议你先让它们生成，比如改名为 CLAUDE.gsd.md，然后人工对比一下。

GSD 擅长的是任务阶段（Phases）划分。
OpenSpec 擅长的是需求规格（Spec）定义。
Superpowers 擅长的是测试驱动（TDD）指令。



你现在的配置非常强大，这几套工具合起来几乎覆盖了从设计、流程、配置到质量控制的所有维度，堪称“工业级”AI 开发环境。
下一步： 试试用 npx 运行。如果成功了，下次直接在 claudecode 里输入 gsd 也能生效。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
