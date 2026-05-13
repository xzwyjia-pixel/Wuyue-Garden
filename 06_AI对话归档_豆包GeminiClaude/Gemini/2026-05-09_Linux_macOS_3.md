---
title: \(node:19696) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
这个问题如何解决？
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## \(node:19696) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
这个问题如何解决？

看到这个警告，说明你的 Node.js 代码（或者你运行的某个工具）为了绕过 SSL 证书校验，将 NODE_TLS_REJECT_UNAUTHORIZED 设置为了 0。
这就像是为了进门而直接拆掉了保安系统。虽然程序能跑通，但你的数据传输将暴露在中间人攻击（MITM）的风险之下。

为什么会出现这个警告？
通常是因为你在访问一个使用了 自签名证书、证书已过期 或 配置不正确 的 HTTPS 接口。为了图省事，代码中可能写了这一行：
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

解决方案
1. 最佳方案：将自签名证书加入信任列表（推荐）
如果你是在开发环境访问公司内部服务器，与其关闭整个安全检查，不如只信任那张特定的证书。

步骤 A：获取服务器的 .pem 或 .crt 证书文件。
步骤 B：通过环境变量 NODE_EXTRA_CA_CERTS 指向该文件：
# Linux / macOS
export NODE_EXTRA_CA_CERTS="/path/to/your/certificate.pem"
node app.js

# Windows (PowerShell)
$env:NODE_EXTRA_CA_CERTS="C:\path\to\your\certificate.pem"
node app.js



2. 针对特定请求忽略校验（比全局关闭更安全）
如果你使用的是 axios 或 https 模块，你可以只针对这一个请求禁用校验，而不是关闭整个进程的安全检查。
Axios 示例：
const https = require('https');
const axios = require('axios');

const agent = new https.Agent({  
  rejectUnauthorized: false // 仅对该请求生效
});

axios.get('https://example.com', { httpsAgent: agent });

3. 生产环境：修复服务器证书
如果这个警告出现在生产环境，唯一的正确做法是给服务器配置有效的 SSL 证书（如使用 Let's Encrypt 申请免费的正式证书）。关闭校验在生产环境中是极其危险的行为。

如何排查代码哪里设置了它？
如果你不知道是谁设置了这个变量，可以使用警告提示中给出的命令：
node --trace-warnings your_script.js

这会打印出完整的堆栈追踪，告诉你到底是哪一行代码触发了 process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'。
总结

临时调试：可以使用环境变量，但不要写在代码里。
长期开发：使用 NODE_EXTRA_CA_CERTS 信任特定证书。
生产环境：必须使用合法的 CA 证书，严禁设置此变量。

---
*从 Gemini 导出，2026-05*
