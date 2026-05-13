---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> ollama --version
ollama version is 0.22.0
PS C:\Users\think> ollama run qwen2:1.5b
pulling manifest
pulling 405b56374e02: 100% ▕██████████████████████████████████████████████████████████▏ 934 MB
pulling 62fbfd9ed093: 100% ▕██████████████████████████████████████████████████████████▏  182 B
pulling c156170b718e: 100% ▕██████████████████████████████████████████████████████████▏  11 KB
pulling f02dd72bb242: 100% ▕██████████████████████████████████████████████████████████▏   59 B
pulling c9f5e9ffbc5f: 100% ▕██████████████████████████████████████████████████████████▏  485 B
verifying sha256 digest
writing manifest
success
>>> 你好，帮我给“财务报表”文件夹起一个视觉关键词
好的，我帮你想一下。如果你正在寻找视觉关键词，可以用来描述“财务报表”这个主题或者文件夹内容的话，一些可能的视觉关键
词可能是 "经济报告"、"商业分析"、"会计数据" 或者 "企业报表"。这些关键词可以帮助你更好地将这个文件夹和其他相关的内容
区分开来，同时也能给浏览者留下清晰的印象。

>>> $body = @{
...     model = "qwen2:1.5b"
...     prompt = "Task: Analyze folder content. Files: [contract.pdf, bill.xlsx, logo.png]. Output a one-word visual the
... me."
...     stream = $false
... } | ConvertTo-Json
...
... Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/generate -Body $body -ContentType "application/json;
... charset=utf-8"
你的代码看起来是在尝试使用`Invoke-RestMethod`在后端与一个名为“generate”的API进行交互。这个API似乎接受请求并返回一
组数据，其中包含主题和文件类型的可视化结果。

你的代码中的关键部分是：

1. `@body = @{ ... }`: 创建了一个变量`@body`，其中包含了预设的参数和值。
2. `ConvertTo-Json`: 转换字符串到JSON格式。
3. `Invoke-RestMethod -Uri <uri>`: 发送HTTP请求至指定的URI。
4. `-Body $body` 和 `-ContentType "application/json; charset=utf-8"`: 将参数和内容类型传递给HTTP请求。

现在，关于你提到的"one-word visual theme"（视觉主题），根据这个API的要求，你的代码应该会返回一个一词的可视化主题作为
响应。这可能是一个文件类型（如"invoice"、"bill"等）或特定于这些文件的关键词（如"交易记录"、"账单"等）。请确保检查并
替换`@body`中的参数以适应实际需要，从而获得适当的视觉主题。

此外，要测试这个API，你需要提供一些文件作为请求的附件。你可能想要在运行时使用一个临时文件来模仿这个问题，并将其上传
到指定的URI。请注意，这只是一个简单的示例，实际操作可能会复杂得多，具体取决于你的环境和API的要求。
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> ollama --version
ollama version is 0.22.0
PS C:\Users\think> ollama run qwen2:1.5b
pulling manifest
pulling 405b56374e02: 100% ▕██████████████████████████████████████████████████████████▏ 934 MB
pulling 62fbfd9ed093: 100% ▕██████████████████████████████████████████████████████████▏  182 B
pulling c156170b718e: 100% ▕██████████████████████████████████████████████████████████▏  11 KB
pulling f02dd72bb242: 100% ▕██████████████████████████████████████████████████████████▏   59 B
pulling c9f5e9ffbc5f: 100% ▕██████████████████████████████████████████████████████████▏  485 B
verifying sha256 digest
writing manifest
success
>>> 你好，帮我给“财务报表”文件夹起一个视觉关键词
好的，我帮你想一下。如果你正在寻找视觉关键词，可以用来描述“财务报表”这个主题或者文件夹内容的话，一些可能的视觉关键
词可能是 "经济报告"、"商业分析"、"会计数据" 或者 "企业报表"。这些关键词可以帮助你更好地将这个文件夹和其他相关的内容
区分开来，同时也能给浏览者留下清晰的印象。

>>> $body = @{
...     model = "qwen2:1.5b"
...     prompt = "Task: Analyze folder content. Files: [contract.pdf, bill.xlsx, logo.png]. Output a one-word visual the
... me."
...     stream = $false
... } | ConvertTo-Json
...
... Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/generate -Body $body -ContentType "application/json;
... charset=utf-8"
你的代码看起来是在尝试使用`Invoke-RestMethod`在后端与一个名为“generate”的API进行交互。这个API似乎接受请求并返回一
组数据，其中包含主题和文件类型的可视化结果。

你的代码中的关键部分是：

1. `@body = @{ ... }`: 创建了一个变量`@body`，其中包含了预设的参数和值。
2. `ConvertTo-Json`: 转换字符串到JSON格式。
3. `Invoke-RestMethod -Uri <uri>`: 发送HTTP请求至指定的URI。
4. `-Body $body` 和 `-ContentType "application/json; charset=utf-8"`: 将参数和内容类型传递给HTTP请求。

现在，关于你提到的"one-word visual theme"（视觉主题），根据这个API的要求，你的代码应该会返回一个一词的可视化主题作为
响应。这可能是一个文件类型（如"invoice"、"bill"等）或特定于这些文件的关键词（如"交易记录"、"账单"等）。请确保检查并
替换`@body`中的参数以适应实际需要，从而获得适当的视觉主题。

此外，要测试这个API，你需要提供一些文件作为请求的附件。你可能想要在运行时使用一个临时文件来模仿这个问题，并将其上传
到指定的URI。请注意，这只是一个简单的示例，实际操作可能会复杂得多，具体取决于你的环境和API的要求。

太棒了！从你的 PowerShell 输出看，Ollama 已经完全跑通了。
你不仅成功拉取并运行了 qwen2:1.5b 模型，而且它已经能够准确理解你的意图并给出了语义建议（比如“经济报告”、“会计数据”）。
特别注意：
你在 PowerShell 中最后那段报错是因为你直接在 Ollama 的对话模式（>>> 提示符下） 粘贴了 PowerShell 脚本。Ollama 的对话框只能理解自然语言，不能直接执行 PowerShell 代码，所以它把代码当成聊天内容来回复你了。
下一步：真正的“自动化”点火
既然模型已就绪，我们现在进入产品开发阶段。为了实现“自动语义化图标”，你需要一份能自动扫描文件夹并调用 Ollama 的 Python 脚本。
请在你的 VS Code 中新建一个文件 analyze_folder.py，并将以下代码粘贴进去。这段代码是你的产品核心逻辑原型：
import requests
import json
import os

def get_folder_semantics(folder_path):
    # 1. 获取文件夹内的文件名
    try:
        files = os.listdir(folder_path)
        file_list_str = ", ".join(files[:10]) # 取前10个文件防止提示词过长
    except Exception as e:
        return f"读取文件夹失败: {e}"

    # 2. 构造发送给 Ollama 的指令
    prompt = f"""
    你是一个文件管理专家。请分析以下文件夹中的文件名，并给出一个最能代表该文件夹主题的【英文关键词】和【中文描述】。
    要求：关键词必须适合作为设计图标的灵感。
    
    文件名列表：[{file_list_str}]
    
    请按此 JSON 格式输出：{{"keyword": "英文单词", "description": "中文描述"}}
    """

    # 3. 调用本地 Ollama API
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "qwen2:1.5b",
        "prompt": prompt,
        "stream": False,
        "format": "json" # 强制输出 JSON 格式
    }

    print(f"正在分析文件夹: {folder_path} ...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = json.loads(response.json()['response'])
        return result
    else:
        return "API 调用失败"

# 测试点火：分析你当前的一个项目文件夹
test_path = r"C:\Users\think\Documents" # 你可以换成你自己的路径
semantics = get_folder_semantics(test_path)
print("\n--- 语义分析结果 ---")
print(semantics)

为什么这对你的产品至关重要？

极简精密逻辑： 这段代码实现了从“杂乱文件名”到“精准关键词”的转化。
本地化隐私： 所有分析都在你的 C:\Users\think 本地完成，完全符合你对隐私和效率的要求。
配合 Claude Code： 你现在可以把这段代码发给左侧侧边栏的 Claude Code，对它说：

“这是我跑通的本地 Ollama 调用脚本。现在请帮我完善它：当获取到 keyword 后，自动搜索本地的一个图标库，或者调用绘图 API 生成一个极简风格的图标文件。”



针对你目前状态的建议：

输入 /exit： 先在 PowerShell 里输入 /exit 退出 Ollama 的聊天模式，回到正常的 PS C:\Users\think> 状态。
运行脚本： 在正常的 PowerShell 状态下运行 python analyze_folder.py。

如果运行脚本时提示 No module named 'requests'，请先执行 pip install requests。
你的“AI 自动语义化图标”项目的第一块拼图已经拼上了！需要我继续帮你写图标替换部分的逻辑吗？

---
*从 Gemini 导出，2026-05*
