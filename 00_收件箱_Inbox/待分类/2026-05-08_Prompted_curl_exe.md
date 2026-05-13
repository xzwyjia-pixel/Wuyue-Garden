---
title: Prompted
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

从你提供的截图来看，关键报错在于 curl: (56) Failure when receiving data from the peer。这通常意味着连接虽然建立了，但在数据传输过程中被“对端”或中间代理强行断开了。
既然你提到了正在使用代理和第三方中转站，这很可能是代理配置不一致或TLS 握手失败导致的。
1. 验证代理是否真正生效
在 PowerShell 中设置环境变量 $env:HTTP_PROXY 仅对当前会话有效。请执行以下命令测试代理是否通畅：
# 测试通过代理访问 Google 
curl.exe -I https://www.google.com

# 测试你的中转站地址 (替换为你的实际 API 域名)
curl.exe -I https://你的中转站域名.com

如果 curl 依然报 56 错误，说明当前的命令行会话并没有成功通过你的 VPN 代理出口。
2. 强制使用命令行代理 (建议尝试)
有时候系统环境变量不一定被 curl 或 Node.js 完美识别，你可以尝试在 curl 命令中直接指定代理：
curl.exe -x http://127.0.0.1:7890 -I https://api.anthropic.com

如果加上 -x 参数后能返回 HTTP/2 200 或 403，说明是全局变量没生效；如果依然报 56，则是代理软件本身无法处理该请求。
3. 针对 Claude/Cloud Code 的配置
由于你提到想把中文版的换成 DC (Claude)，请确保你的配置文件（通常是 .env 或 IDE 设置）中：

Base URL: 修改为中转站提供的地址。
API Key: 确保使用的是中转站对应的 Key。

4. 检查 SSL/TLS 干扰
Failure when receiving data 经常是因为代理软件尝试解密 SSL 包（MITM）但证书不被信任。

尝试临时跳过证书检查看看是否能通：
curl.exe -k -I https://api.anthropic.com




下一步建议：
你可以检查一下你的代理软件（如 Clash/V2Ray）的 Logs（日志）。如果日志里显示 Remote error: tls: alert(10) 或 connection reset，那问题就在于中转站的节点不稳定，或者你的本地代理端口（7890）未开启“局域网共享”或“系统代理”模式。
现在运行 curl.exe -x http://127.0.0.1:7890 -I https://api.anthropic.com 的结果是什么？

---
*从 Gemini 导出，2026-05*
