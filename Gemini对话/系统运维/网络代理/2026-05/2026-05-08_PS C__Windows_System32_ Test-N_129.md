---
title: PS C:\Windows\System32> Test-NetConnection -ComputerName 127.0.0.1 -Port 7890
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: 网络代理
old_category: 编程开发
tags: [gemini, 系统运维, 网络代理]
---

## PS C:\Windows\System32> Test-NetConnection -ComputerName 127.0.0.1 -Port 7890

## PS C:\Windows\System32> Test-NetConnection -ComputerName 127.0.0.1 -Port 7890

ComputerName     : 127.0.0.1
RemoteAddress    : 127.0.0.1
RemotePort       : 7890
InterfaceAlias   : Loopback Pseudo-Interface 1
SourceAddress    : 127.0.0.1
TcpTestSucceeded : True

PS C:\Windows\System32>

既然 TcpTestSucceeded : True，说明你的代理软件端口是正常监听的。
状态码 000 且无法连通，在端口通畅的情况下，最核心的原因通常是 SSL 握手崩溃或代理协议冲突。由于你之前配置了大量的环境变量，它们可能在底层打架。
请执行以下**“终极清理+强制直通”**方案：
1. 彻底重置当前窗口环境
在同一个窗口依次粘贴并运行以下代码（不要带续行符，我直接给你整行格式）：
# 1. 强制清理环境变量干扰
$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
$env:ALL_PROXY = "http://127.0.0.1:7890"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

# 2. 重新定义参数
$apiKey = "sk-3e3869623f234533921586e27ce4ec91"
$url = "https://api.deepseek.com/chat/completions"

Write-Host "📡 正在尝试暴力测试 (强制无缓存 + 详细日志)..." -ForegroundColor Yellow

# 3. 使用全路径参数，禁用所有默认配置
$curlArgs = @(
    "-v", "-k", 
    "--proxy-ntlm", # 尝试兼容某些 Windows 代理环境
    "-X", "POST", $url,
    "-H", "Authorization: Bearer $apiKey",
    "-H", "Content-Type: application/json",
    "-d", '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}',
    "-x", "http://127.0.0.1:7890"
)

& curl.exe @curlArgs


2. 如果看到日志中有 "Proxy-Connection: Keep-Alive" 后报错
请检查你的代理软件（Clash/V2RayN/Nekoray）：

节点可用性：虽然 7890 端口通了，但你选中的节点可能已经过期或无法连接。请在代理软件里点一下“延迟测试”。
DNS 设置：如果是 Could not resolve host: api.deepseek.com，说明代理软件没有正确解析 DNS。请在代理软件中开启 "System Proxy" (系统代理) 开关。
日志排查：这是最关键的。请打开代理软件的“日志 (Logs)”窗口，观察你运行上述命令时，是否有红色的报错条目。

如果有 EOF，说明连接被中途切断。
如果有 Connection Refused，说明代理软件虽然占着端口但拒绝转发。



3. 一个小细节
你刚才成功的测试返回了 model: deepseek-v4-flash，这说明你可能之前连接的是一个中转站而非官方。而现在测试的是官方 api.deepseek.com。
如果你打算继续使用那个中转站，请把代码里的 $url 换回你之前成功的那个中转域名。
操作建议：
先去代理软件换一个非香港/国内的节点，然后重新运行上面的代码。只要能看到一行 HTTP/1.1 200 OK，你的“规则甄查”工具就能原地起飞。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / 网络代理 · 2026-05-08*
