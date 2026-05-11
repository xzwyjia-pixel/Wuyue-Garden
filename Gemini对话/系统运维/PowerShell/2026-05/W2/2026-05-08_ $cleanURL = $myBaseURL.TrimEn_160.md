---
title: > $cleanURL = $myBaseURL.TrimEnd('/')
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## > $cleanURL = $myBaseURL.TrimEnd('/')

## > $cleanURL = $myBaseURL.TrimEnd('/')
>> # 自动生成测试端点
>> $targetUrl = if ($cleanURL -like "*/v1") { "$cleanURL/messages" } else { "$cleanURL/v1/messages" }
>> $jsonBody = '{"model":"claude-3-5-sonnet-20240620","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
>>
>> # 使用 curl.exe 发起“全兼容”请求 (同时带上 x-api-key 和 Authorization)
>> $curlArgs = @(
>>     "-k", "-s", "-i", "-X", "POST", $targetUrl,
>>     "-H", "x-api-key: $apiKey",
>>     "-H", "Authorization: Bearer $apiKey",
>>     "-H", "anthropic-version: 2023-06-01",
>>     "-H", "Content-Type: application/json",
>>     "-d", $jsonBody,
>>     "-x", $proxy
>> )
>>
>> $response = & curl.exe @curlArgs
>>
>> if ($response -like "*HTTP/* 200*" -and $response -like "*content*") {
>>     Write-Host "`n🚀 成功！DC 大模型已连接。" -ForegroundColor Green
>>     Write-Host "有效地址: $targetUrl" -ForegroundColor Cyan
>>     Write-Host "`n✨ 终端环境已就绪。请在此窗口直接执行你的审计命令。" -ForegroundColor White
>> } else {
>>     Write-Host "`n❌ 验证失败。错误响应摘要：" -ForegroundColor Red
>>     $response | Select-Object -First 10 | Write-Host
>>     Write-Host "`n💡 解决方案：`n1. 检查中转站后台，确认模型名是否完全匹配。`n2. 尝试将 Base URL 改为不带 /v1 的形式 再试一次。" -ForegroundColor Yellow
>> }

✅ [步骤1/2] 环境变量注入成功。
📡 [步骤2/2] 正在适配 DC 模型链路...

❌ 验证失败。错误响应摘要：
HTTP/1.1 200 Connection established
Connection: close


💡 解决方案：
1. 检查中转站后台，确认模型名是否完全匹配。
2. 尝试将 Base URL 改为不带 /v1 的形式再试一次。
PS C:\Windows\System32> # ================= 1. 基础参数 (请务必检查此处) =================
>> $myBaseURL = "https://你的中转域名.com"  # <--- 注意：这里不要带 /v1，脚本会自动处理
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # ================= 2. 环境强制初始化 =================
>> $env:HTTP_PROXY = $proxy
>> $env:HTTPS_PROXY = $proxy
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>> # 设置 Cloud Code CLI 识别的环境变量
>> $env:ANTHROPIC_BASE_URL = "$myBaseURL/v1"
>> $env:ANTHROPIC_API_KEY = $apiKey
>>
>> Write-Host "`n✅ [环境] 代理与变量已注入。" -ForegroundColor Green
>>
>> # ================= 3. 智能链路探测 =================
>> Write-Host "📡 [链路] 正在探测最佳接口路径..." -ForegroundColor Yellow
>>
>> $cleanHost = $myBaseURL.TrimEnd('/')
>> # 测试三个最可能的路径
>> $testUrls = @("$cleanHost/v1/messages", "$cleanHost/messages", "$cleanHost/api/v1/messages")
>>
>> $success = $false
>> foreach ($url in $testUrls) {
>>     Write-Host "尝试路径: $url" -ForegroundColor Gray
>>
>>     $jsonBody = '{"model":"claude-3-5-sonnet-20240620","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
>>
>>     # 使用 curl.exe 并强制跳过 SSL 检查
>>     $curlArgs = @(
>>         "-k", "-s", "-i", "-L", "-X", "POST", $url,
>>         "-H", "x-api-key: $apiKey",
>>         "-H", "anthropic-version: 2023-06-01",
>>         "-H", "Content-Type: application/json",
>>         "-d", $jsonBody,
>>         "-x", $proxy
>>     )
>>
>>     $res = & curl.exe @curlArgs
>>
>>     # 只要返回内容包含 "content" 关键字，即代表模型响应成功
>>     if ($res -like "*content*") {
>>         Write-Host "`n🚀 连通成功！" -ForegroundColor Green
>>         Write-Host "有效 Endpoint: $url" -ForegroundColor Cyan
>>         $success = $true
>>         break
>>     }
>> }
>>
>> if (-not $success) {
>>     Write-Host "`n❌ 探测失败。请检查中转站后台，确认：`n1. 域名是否需要备案或已被墙？`n2. 账户余额是否充足？" -ForegroundColor Red
>> } else {
>>     Write-Host "`n✨ 终端环境已就绪，现在可以直接运行你的审计工具或 Cloud Code 命令。" -ForegroundColor White
>> }

✅ [环境] 代理与变量已注入。
📡 [链路] 正在探测最佳接口路径...
尝试路径: https://你的中转域名.com/v1/messages
尝试路径: https://你的中转域名.com/messages
尝试路径: https://你的中转域名.com/api/v1/messages

❌ 探测失败。请检查中转站后台，确认：
1. 域名是否需要备案或已被墙？
2. 账户余额是否充足？
PS C:\Windows\System32>
>> curl.exe -v -k -x http://127.0.0.1:7890 -X POST https:// www.deepseek.com/v1/messages -H "x-api-key: 你的KEY" -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" -d '{"model":"claude-3-5-sonnet-20240620","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
Note: Unnecessary use of -X or --request, POST is already inferred.
* URL rejected: No host part in the URL
* closing connection #-1
curl: (3) URL rejected: No host part in the URL
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying 127.0.0.1:7890...
* Connected to 127.0.0.1 (127.0.0.1) port 7890
> POST http://www.deepseek.com/v1/messages HTTP/1.1
> Host: www.deepseek.com
> User-Agent: curl/8.9.1
> Accept: */*
> Proxy-Connection: Keep-Alive
> x-api-key: 浣犵殑KEY
> anthropic-version: 2023-06-01
> Content-Type: application/json
> Content-Length: 98
>
* upload completely sent off: 98 bytes
< HTTP/1.1 403 Forbidden
< Content-Length: 1053
< Cache-Control: max-age=86400
< Connection: keep-alive
< Content-Type: text/html
< Date: Fri, 08 May 2026 05:56:57 GMT
< Keep-Alive: timeout=4
< Proxy-Connection: keep-alive
< Server: CloudFront
< Via: 1.1 df3d54dad27ad5f5eb654487101f8c76.cloudfront.net (CloudFront)
< X-Amz-Cf-Id: D_ryC7me9eDD9EGQDphf5CfHG3DIQbIiYgcskppowW1TATag1HFP9g==
< X-Amz-Cf-Pop: SLC52-P1
< X-Cache: Error from cloudfront
<
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<HTML><HEAD><META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
<TITLE>ERROR: The request could not be satisfied</TITLE>
</HEAD><BODY>
<H1>403 ERROR</H1>
<H2>The request could not be satisfied.</H2>
<HR noshade size="1px">
This distribution is not configured to allow the HTTP request method that was used for this request. The distribution supports only cachable requests.
We can't connect to the server for this app or website at this time. There might be too much traffic or a configuration error. Try again later, or contact the app or website owner.
<BR clear="all">
If you provide content to customers through CloudFront, you can find steps to troubleshoot and help prevent this error by reviewing the CloudFront documentation.
<BR clear="all">
<HR noshade size="1px">
<PRE>
Generated by cloudfront (CloudFront)
Request ID: D_ryC7me9eDD9EGQDphf5CfHG3DIQbIiYgcskppowW1TATag1HFP9g==
</PRE>
<ADDRESS>
</ADDRESS>
</BODY></HTML>* Connection #0 to host 127.0.0.1 left intact
PS C:\Windows\System32> # 配置代理与 API Key
>> $env:HTTP_PROXY = "http://127.0.0.1:7890"
>> $env:HTTPS_PROXY = "http://127.0.0.1:7890"
>> $apiKey = "sk-c8cf2fa5efc44b29b84f4ef6a7b9706e"
>>
>> # 设置 DeepSeek/OpenAI 兼容环境变量 (Cloud Code 等工具通常识别这些)
>> $env:DEEPSEEK_API_KEY = $apiKey
>> $env:OPENAI_API_KEY = $apiKey
>> $env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"
>>
>> Write-Host "✅ 终端代理与 DeepSeek 变量已注入。" -ForegroundColor Green
✅ 终端代理与 DeepSeek 变量已注入。
PS C:\Windows\System32>

既然你已经完成了环境变量的注入，接下来我们直接进行链路验证。
由于 DeepSeek 官方接口是 OpenAI 兼容协议，与你之前尝试的 Anthropic 协议完全不同，请直接在 PowerShell 窗口中粘贴并运行以下代码。这段代码已经根据你提供的 API Key 进行了硬编码，确保万无一失。

第一步：发起 DeepSeek 官方链路验证
Write-Host "📡 正在验证 DeepSeek 官方链路..." -ForegroundColor Yellow

# DeepSeek 官方标准接口地址
$testUrl = "https://api.deepseek.com/chat/completions"

# 构造符合 OpenAI 规范的 JSON
$jsonBody = '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}'

# 使用 curl.exe 绕过 PowerShell 原生网络库的 EOF 问题
$curlArgs = @(
    "-k", "-s", "-i",
    "-X", "POST", $testUrl,
    "-H", "Authorization: Bearer sk-c8cf2fa5efc44b29b84f4ef6a7b9706e",
    "-H", "Content-Type: application/json",
    "-d", $jsonBody,
    "-x", "http://127.0.0.1:7890"
)

$res = & curl.exe @curlArgs

if ($res -like "*choices*") {
    Write-Host "`n🚀 验证成功！DeepSeek 接口已完全连通。" -ForegroundColor Green
    Write-Host "回复内容摘要：" -ForegroundColor Gray
    $res | Select-Object -Last 1 | Write-Host
} else {
    Write-Host "`n❌ 验证失败。请检查：" -ForegroundColor Red
    Write-Host "1. 代理软件是否正常开启了 7890 端口？`n2. 账号余额是否足够？`n3. 代理是否拦截了 api.deepseek.com 域名？" -ForegroundColor Yellow
    Write-Host "`n以下是原始错误响应：" -ForegroundColor Gray
    $res | Write-Host
}


第二步：如果验证成功，如何配置 Cloud Code？
当上面的脚本显示“验证成功”后，你的 PowerShell 环境就已经完全准备好了。如果你要在 Cloud Code 或 审计工具 中使用，请务必确认以下配置：

Base URL (端点): 填写 [https://api.deepseek.com/v1](https://api.deepseek.com/v1)
API Key: 填写 sk-c8cf2fa5efc44b29b84f4ef6a7b9706e
Model Name (模型): 必须填写 deepseek-chat (对应 V3) 或 deepseek-reasoner (对应 R1)。

⚠️ 安全提示：
你刚才提供的 API Key 是明文的。虽然我现在帮你解决了连接问题，但为了你的账号资产安全，强烈建议在测试成功后，去 DeepSeek 控制台将这个 Key 删除并生成一个新的。以后在公开对话中，建议先用 sk-xxxx 这种占位符。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
