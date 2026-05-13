---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> ollama --version
ollama version is 0.22.0
PS C:\Users\think>
source: gemini
date: 2026-05-07
category: 系统运维
tags: [gemini, 系统运维]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> ollama --version
ollama version is 0.22.0
PS C:\Users\think>

恭喜！Ollama 的点火测试第一步已经成功。 你的版本号是 0.22.0，说明安装和环境变量配置都是正确的，电脑已经具备了运行本地大模型的基础。
接下来我们要进行**“实战点火”**，即让模型真正运转起来，为你的“语义化图标”项目提供逻辑。
请依次在你的 PowerShell 中输入以下两条指令：
第一步：拉取并运行轻量级模型
为了确保速度，我们先用一个 0.5b（超轻量）或者 1.5b 的模型。它们对内存要求极低，适合做这种高频的语义提取任务。
ollama run qwen2:1.5b


动作： 输入后会自动开始下载（如果之前没下过）。
成功标志： 下载完成后，会出现 >>> 符号。
测试： 你输入 你好，帮我给“财务报表”文件夹起一个视觉关键词。如果它秒回，说明推理能力跑通了。输入 /exit 退出对话。


第二步：API 通路点火（核心）
你的产品将来是通过代码（API）来调用 Ollama 的，而不是通过命令行聊天。这条指令是模拟你的程序发送请求。
请直接复制并粘贴这整段代码到 PowerShell：
$body = @{
    model = "qwen2:1.5b"
    prompt = "Task: Analyze folder content. Files: [contract.pdf, bill.xlsx, logo.png]. Output a one-word visual theme."
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/generate -Body $body -ContentType "application/json; charset=utf-8"


结果判定：

如果返回一段 JSON 字符（里面包含类似 "response": "Business"）：大功告成！ 你的本地 AI 图标引擎已经完全可以被调用了。
如果报错“无法连接到远程服务器”： 说明 Ollama 的后台服务没启动，去右下角任务栏找找有没有小企鹅/小图标，或者重新打开 Ollama 软件。

关于你之前的疑问：
既然 Ollama 已经通了，Claude Code 图标一定要保留。
最佳协作模式：

Claude Code：作为你的“大脑”和“总架构师”，负责写代码、设计 UI、处理文件系统。
Ollama：作为你的“工人”和“本地引擎”，负责实际的文件夹语义扫描（因为本地扫描免费且隐私）。

下一步建议：
点火成功后，你可以直接在 VS Code 里对 Claude Code 说：

“我已经跑通了本地的 Ollama (qwen2:1.5b)，现在请帮我写一个 Python 脚本，调用这个本地 API 来分析 C:\Users\think\Documents 文件夹的语义。”

需要我帮你准备这段 Python 脚本的代码吗？

---
*从 Gemini 导出，2026-05*
