---
title: Prompted
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

看来直接用 pip 安装 Aider 遇到了网络连接重置（Connection Reset）的问题。这在国内环境非常普遍，通常是因为默认的 Python 官方镜像源连接不稳定。
甄先生，针对这种“环境阻碍”，我们需要换一种更稳健的安装方式，使用国内的镜像源来加速并稳定连接。
解决办法：使用清华大学镜像源安装
请直接复制并运行下面这条命令，它会强制 pip 从清华大学的服务器获取安装包：
pip install aider-chat -i https://pypi.tuna.tsinghua.edu.cn/simple


💡 如果还是报错，尝试“Plan C”：VS Code 插件方案
如果你觉得命令行（PowerShell）的折腾成本太高，不符合“极简精密”的效率原则，我建议你直接在 VS Code 里操作。这是目前最稳定且不需要国外手机号的方案：

安装插件： 在 VS Code 插件市场搜索并安装 Cline (原名 Claude Dev) 或 Roo Code。
配置 API：

在插件设置里选择 API Provider: Anthropic。
填入你那个以 sk-ant-api03- 开头的 API Key。


使用： 在 VS Code 左侧点击图标，你就可以直接在对话框里让它帮你写代码了。

优势： 它原生支持读取项目文件，不需要你手动输入 Set-Content，而且它也有类似 Superpowers 的“模式”可以选择。



总结建议
由于你目前在做“规则情报局”的自动化工具，VS Code + Cline/Roo Code 其实是目前最工业级的组合，比 Claude Code 的命令行版更易于调试和查看文件结构。
你可以先试一下清华源安装 Aider，如果 30 秒内没跑起来进度条，我们直接切 VS Code 方案？

---
*从 Gemini 导出，2026-05*
