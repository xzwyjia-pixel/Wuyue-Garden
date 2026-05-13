---
title: MINIMAX_API_KEY如何获得？
source: gemini
date: 2026-05-04
category: 审计合规
tags: [gemini, 审计合规]
---

## MINIMAX_API_KEY如何获得？

要获得 MiniMax API Key，你需要通过其官方的开发者平台进行注册和申请。由于你目前正在开发 Python 审计工具，获取 Key 是接入模型能力的关键一步。
以下是具体的获取流程：
1. 访问官方开放平台
打开浏览器，访问 MiniMax 官方开发者入口：

地址： platform.minimaxi.com

2. 账号注册与实名认证

注册： 使用你的手机号进行注册并登录。
实名制： 根据相关法规，使用 API 能力通常需要完成实名认证。对于你作为 Jingyuan Company 法定代表人的身份，建议使用企业认证，这通常能获得更高的初始配额（额度）和并发支持。

3. 创建 API Key

登录后台后，在左侧导航栏找到 「账户管理」 或 「接口密钥」 (API Keys) 选项。
点击 「创建密钥」 按钮。
重要提示： 密钥只会完整显示一次，请立即将其复制并安全保存到你的本地环境中。

4. 获取 Group ID
在 MiniMax 的调用中，除了 API_KEY，通常还需要一个 Group ID。

你可以在账号设置或概览页面找到这串数字 ID。
如果你使用兼容 OpenAI 的 SDK（如你之前安装的 openai 库），有时需要将 Group ID 包含在请求头或特定的配置字段中。

5. 充值与配额

新账号通常会有一定的赠送额度。
在正式将该功能集成到你的“规则甄查”短视频审计系统前，建议先在后台查看各模型（如 abab6.5 系列）的计费标准。


安全建议：
既然你熟悉 Python 开发，请务必不要将 API Key 直接写死在 audit_tool.py 代码中。建议使用你之前安装过的 python-dotenv 库，通过 .env 文件读取密钥：
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MINIMAX_API_KEY")

---
*从 Gemini 导出，2026-05*
