---
title: Prompted
source: gemini
date: 2026-05-04
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

从图片 image_aafed6.png 的报错信息来看，你尝试安装的 minimax-sdk 和 minimax-api 在 PyPI 官方库中均不存在，因此导致了 No matching distribution found 错误。
针对你目前在 Python 环境下的开发需求（特别是考虑到你正在进行的 MCP 项目），建议采用以下官方推荐的方式：
1. 使用标准 OpenAI SDK（推荐方式）
MiniMax 官方现在全面兼容 OpenAI 和 Anthropic 的接口协议。这种方式最稳定，且不需要安装特定的小众 SDK：

安装命令：
pip install openai python-dotenv


配置方式：
在你的代码中，只需将 base_url 指向 MiniMax 的官方地址即可：

中国区： [https://api.minimaxi.com/v1](https://api.minimaxi.com/v1)
国际区： [https://api.minimax.io/v1](https://api.minimax.io/v1)




2. 若需安装特定包名
如果你确实想尝试直接针对 MiniMax 的库，根据 PyPI 上的收录情况，你应该使用的包名是：

官方/常用第三方包：
pip install minimax-python

注：minimax-python 是目前较为通用的名称，支持同步和异步调用。


3. 排查建议
如果上述命令依然报错，请检查以下几点：

网络连接： 建议使用国内镜像源（如清华源）以确保连接稳定：
pip install openai -i https://pypi.tuna.tsinghua.edu.cn/simple


API Key 匹配： 请务必确保你的 API Key 类型与所使用的 Endpoint（Host 地址） 区域一致，否则在后续调用时会出现 invalid api key 错误。

对于你正在构建的 内容审计工具 而言，使用 pip install openai 配合 MiniMax 的 base_url 是最简单且扩展性最强的方案。

---
*从 Gemini 导出，2026-05*
