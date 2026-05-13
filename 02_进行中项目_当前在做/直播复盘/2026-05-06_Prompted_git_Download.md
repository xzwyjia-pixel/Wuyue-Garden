---
title: Prompted
source: gemini
date: 2026-05-06
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

看报错提示，你的 git clone 因为网络连接重置（Connection was reset）失败了，所以后续 cd 找不到文件夹。这是在国内访问 GitHub 常见的网络波动问题。
既然你要批量处理资料，我们换两个更稳妥、更符合你技术背景的办法：
方案一：绕过 Git 直接下载 Zip 包（最快）

直接下载： 打开浏览器，访问该项目地址：[https://github.com/Evil0ctal/Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)
点击绿色按钮： 找到页面上的绿色 <> Code 按钮，点击后选择 Download ZIP。
解压： 将下载好的压缩包解压到你的 C:\Users\think\ 目录下。
再次执行： 这时候你再回到 PowerShell，执行 cd Douyin_TikTok_Download_API-main（注意解压后的文件夹名后面可能带个 -main），就能进去了。

方案二：配置 Git 代理（一劳永逸）
如果你电脑上运行着代理软件（通常端口是 7890 或 1080），可以在 PowerShell 里运行这两行代码，让 Git 走代理：
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

注：请将 7890 替换为你实际的代理端口。执行完这两行后，你图片里的 git clone 命令就能跑通了。

⚠️ 进阶建议：针对“批量博主资料”的捷径
如果你觉得部署 GitHub 项目太麻烦，作为“规则甄查甄先生”，我建议你尝试一个更符合工业效率的闭环方案：

使用 Chrome 插件“抖音解析”： 在 Chrome 商店搜 抖音下载。很多插件支持一键导出当前博主主页的所有视频文案到 Excel。
本地 LLM 处理：

既然你本地有 Qwen2.5-Coder 和 Ollama，你不需要去下载几百个视频再转文字。
直接把导出的 Excel 文案内容复制出来，喂给 Qwen2.5。
Prompt： “你现在是一名规则审计员。这是我抓取的某抖音博主的全部文案。请帮我按照知识点进行分类，并剔除所有直播预告和营销话术，输出一个结构化的 Markdown 文档。”


上传 NotebookLM： 把 Qwen2.5 处理好的干净文档上传。

为什么推荐这个？
因为抖音博主的“干货”往往就在视频的**文字描述（Caption）**里。除非博主是那种纯靠口播、文案里啥也不写的类型，否则直接抓取文案列表的效率比下载视频转码要高 100 倍。
你需要我帮你写一段 Python 脚本来自动合并这些抓取到的文案吗？ 这样你可以直接生成一个完美的 PDF 喂给 NotebookLM。

---
*从 Gemini 导出，2026-05*
