---
title: 红色字体的问题怎么解决？
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## 红色字体的问题怎么解决？

截图中的红色字体是 Node.js 的安全警告。这通常是因为你在 PowerShell 中手动设置了环境变量 $env:NODE_TLS_REJECT_UNAUTHORIZED = '0'。
这个设置虽然能让你绕过网络抓包或非对称加密的证书验证（解决某些网络连接报错），但它会让你的所有 HTTPS 请求变得不安全。要彻底解决这个警告并恢复安全设置，请按照以下步骤操作：

1. 恢复安全设置（消除红色警告）
在当前的 PowerShell 窗口中，执行以下命令将其恢复为默认值（1 表示启用验证）：
$env:NODE_TLS_REJECT_UNAUTHORIZED = '1'

执行后，下次启动 npx @anthropic-ai/claude-code 时，红色警告就会消失。

2. 为什么你会设置它？（根源解决）
你设置这个变量通常是为了解决网络连接失败（例如连接 DeepSeek 或 Claude 接口时报错）。如果恢复为 1 后无法联网，建议改用以下更安全的方法：

检查系统代理： 确保你的加速器或代理软件开启了“系统代理”模式。
设置 npm 代理： 不要关闭安全验证，而是让 npm 走代理：
npm config set proxy http://127.0.0.1:7890
npm config set https-proxy http://127.0.0.1:7890

(注：端口号 7890 请根据你实际的代理软件修改)


3. 关于你的 Claude Code 环境
从截图中看到你正在使用 DeepSeek 的 API 运行 Claude Code：

API 密钥安全： 你的截图里泄露了 API Key (sk-cad1...)。虽然是个人使用，但建议你立刻去 DeepSeek 后台删除并重新生成一个 Key，以防被他人盗刷。
持久化设置： 如果你不想每次都输入那两行 $env: 命令，可以将它们添加到你的 PowerShell 配置文件（$PROFILE）中。


4. 补充：解决 Listary 拒绝访问的问题
看到你之前尝试停止 Listary 进程失败。这是因为普通用户权限无法结束系统服务或高级进程。

解决方法： 请关闭当前窗口，右键点击 PowerShell 图标，选择 “以管理员身份运行”。在管理员窗口中执行 Stop-Process -Name "Listary" -Force 即可成功。

操作建议： 先恢复安全变量（步骤 1），如果遇到报错连不上 DeepSeek，我们再针对性地配置网络代理。

---
*从 Gemini 导出，2026-05*
