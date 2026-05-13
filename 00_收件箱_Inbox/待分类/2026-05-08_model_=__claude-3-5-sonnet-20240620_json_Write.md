---
title:     model = "claude-3-5-sonnet-20240620"
>>     max_tokens = 10
>>     messages = @(@{ role = "user"; content = "hi" })
>> } | ConvertTo-Json
>>
>> try {
>>     $response = Invoke-RestMethod -Uri "$myBaseURL/messages" `
>>         -Method Post `
>>         -Headers @{ "x-api-key" = $apiKey; "anthropic-version" = "2023-06-01"; "Content-Type" = "application/json" } `
>>         -Body $testPayload `
>>         -SkipCertificateCheck
>>     Write-Host "🚀 测试成功！模型回复: $($response.content[0].text)" -ForegroundColor Cyan
>> } catch {
>>     Write-Error "❌ 连接依然失败。错误信息: $_"
>>     Write-Host "提示：请检查你的代理软件是否开启了 TUN 模式，或者中转域名是否拼写正确（是否需要加 /v1）。" -ForegroundColor Yellow
>> }
✅ VS Code 配置已成功强制更新。
Write-Error: ❌ 连接依然失败。错误信息: Received an unexpected EOF or 0 bytes from the transport stream.
提示：请检查你的代理软件是否开启了 TUN 模式，或者中转域名是否拼写正确（是否需要加 /v1）。
PS C:\Windows\System32> # ================= 1. 请在此处修改你的参数 =================
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>>
>> # ================= 2. 直接复制以下全部内容并运行 =================
>> Write-Host "🚀 开始自动化配置..." -ForegroundColor Cyan
>>
>> # 强制设置当前会话的 TLS 协议和代理环境
>> [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
>> $env:HTTP_PROXY = "http://127.0.0.1:7890"; $env:HTTPS_PROXY = "http://127.0.0.1:7890"
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 自动定位并修改 VS Code 配置文件
>> $settingsPath = "$env:APPDATA\Code\User\settings.json"
>> if (Test-Path $settingsPath) {
>>     try {
>>         $json = Get-Content $settingsPath -Raw -Encoding utf8 | ConvertFrom-Json
>>         # 批量强制注入 Base URL (无论原字段是否存在)
>>         $fields = @("cline.anthropicBaseUrl", "anthropic.baseUrl", "cloudcode.claude.baseUrl")
>>         foreach ($f in $fields) {
>>             if ($json.PSObject.Properties[$f]) { $json.$f = $myBaseURL }
>>             else { $json | Add-Member -MemberType NoteProperty -Name $f -Value $myBaseURL }
>>         }
>>         $json | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
>>         Write-Host "✅ VS Code 配置文件已自动更新。" -ForegroundColor Green
>>     } catch {
>>         Write-Warning "配置文件解析异常，请检查 JSON 格式。"
>>     }
>> }
>>
>> # 自动发起接口测试
>> Write-Host "📡 正在验证链路..." -ForegroundColor Yellow
>> $body = @{ model="claude-3-5-sonnet-20240620"; max_tokens=10; messages=@(@{role="user"; content="hi"}) } | ConvertTo-Json
>> try {
>>     $res = Invoke-RestMethod -Uri "$myBaseURL/messages" -Method Post -Headers @{
>>         "x-api-key"=$apiKey; "anthropic-version"="2023-06-01"; "Content-Type"="application/json"
>>     } -Body $body -SkipCertificateCheck -TimeoutSec 15
>>     Write-Host "🚀 测试成功！模型已响应：$($res.content[0].text)" -ForegroundColor Green
>> } catch {
>>     Write-Host "❌ 依然 EOF 或连接超时。建议：1. 确认代理端口是 7890；2. 尝试给 Base URL 末尾加上/去掉 /v1" -ForegroundColor Red
>> }
🚀 开始自动化配置...
✅ VS Code 配置文件已自动更新。
📡 正在验证链路...
❌ 依然 EOF 或连接超时。建议：1. 确认代理端口是 7890；2. 尝试给 Base URL 末尾加上/去掉 /v1
PS C:\Windows\System32> # 1. 基础参数配置
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 自动化注入终端环境变量 (针对 Cloud Code CLI 和 DC 对接)
>> Write-Host "🛠️ 正在配置 PowerShell 终端环境..."  -ForegroundColor Cyan
>>
>> # 设置通用代理变量
>> $env:HTTP_PROXY  = $proxy
>> $env:HTTPS_PROXY = $proxy
>>
>> # 注入 Cloud Code 和 Claude 识别的标准环境变量
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY  = $apiKey
>>
>> # 针对 Node.js 运行时（Cloud Code 底层）的 SSL 豁免
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 3. 验证终端是否能够直连 DC 模型
>> Write-Host "📡 正在验证终端与 DC 大模型的连接..." -ForegroundColor Yellow
>>
>> $testUrl = if ($myBaseURL -like "*/v1*") { "$myBaseURL/messages" } else { "$myBaseURL/v1/messages" }
>>
>> # 使用 curl.exe 验证（避开 PowerShell 原生 netstack 的 EOF 问题）
>> $testCmd = "curl.exe -k -s -X POST `"$testUrl`" " +
>>            "-H `"x-api-key: $apiKey`" " +
>>            "-H `"anthropic-version: 2023-06-01`" " +
>>            "-H `"Content-Type: application/json`" " +
>>            "-d `"{`"model`": `"claude-3-5-sonnet-20240620`", `"max_tokens`": 10, `"messages`": [{`"role`": `"user`", `"content`": `"hi`"}]}`" " +
>>            "-x $proxy"
>>
>> $response = iex $testCmd
>>
>> if ($response -like "*content*") {
>>     Write-Host "✅ 验证成功！终端已成功对接 DC 大模型。" -ForegroundColor Green
>>     Write-Host "现在你可以直接在当前 PowerShell 会话运行 Cloud Code 审计工具了。" -ForegroundColor White
>> } else {
>>     Write-Host "❌ 验证失败，返回结果：$response" -ForegroundColor Red
>>     Write-Host "💡 请检查：1. 中转域名后缀是否正确；2. 代理端口 7890 是否开启。" -ForegroundColor Yellow
>> }
🛠️ 正在配置 PowerShell 终端环境...
📡 正在验证终端与 DC 大模型的连接...
❌ 验证失败，返回结果：
💡 请检查：1. 中转域名后缀是否正确；2. 代理端口 7890 是否开启。
PS C:\Windows\System32> # 1. 基础参数配置
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入终端环境变量 (让 Cloud Code CLI 能够识别 DC 模型)
>> $env:HTTP_PROXY = $proxy
>> $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> Write-Host "✅ 当前会话环境变量已注入。" -ForegroundColor Green
>>
>> # 3. 自动化验证连接 (改用更稳定的方式处理 curl 参数)
>> $testUrl = if ($myBaseURL -like "*/v1*") { "$myBaseURL/messages" } else { "$myBaseURL/v1/messages" }
>> $jsonPayload = '{"model": "claude-3-5-sonnet-20240620", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}'
>>
>> Write-Host "📡 正在验证终端与 DC 大模型的连接..." -ForegroundColor Yellow
>>
>> # 使用 Start-Process 配合 ArgumentList，完美避开引号解析错误
>> $curlArgs = @("-k", "-s", "-X", "POST", $testUrl,
>>               "-H", "x-api-key: $apiKey",
>>               "-H", "anthropic-version: 2023-06-01",
>>               "-H", "Content-Type: application/json",
>>               "-d", $jsonPayload,
>>               "-x", $proxy)
>>
>> $response = & curl.exe @curlArgs
>>
>> if ($response -like "*content*") {
>>     Write-Host "🚀 验证成功！你的 PowerShell 终端已对接 DC 大模型。" -ForegroundColor Green
>>     Write-Host "提示：请就在当前窗口执行你的 Cloud Code 或审计工具命令。" -ForegroundColor White
>> } else {
>>     Write-Host "❌ 验证返回空或错误。请确认：`n1. 中转域名是否拼写正确（$myBaseURL）`n2. 代理端口 $proxy 是否在运行。" -ForegroundColor Red
>>     $response | Write-Host
>> }
✅ 当前会话环境变量已注入。
📡 正在验证终端与 DC 大模型的连接...
❌ 验证返回空或错误。请确认：
1. 中转域名是否拼写正确（https://你的中转域名.com/v1）
2. 代理端口 http://127.0.0.1:7890 是否在运行。
PS C:\Windows\System32> # 1. 基础参数 (请替换为你的真实信息)
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入终端环境变量 (强制 Cloud Code CLI 及其它审计工具走中转路径)
>> $env:HTTP_PROXY = $proxy
>> $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0" # 豁免 Node.js/Cloud Code 的 SSL 校验
>>
>> Write-Host "`n✅ [步骤1/2] 终端环境变量注入成功。" -ForegroundColor Green
>>
>> # 3. 自动化链路验证 (支持多路径自动匹配)
>> Write-Host "📡 [步骤2/2] 正在自动探测最佳连接路径..." -ForegroundColor Yellow
>>
>> $cleanURL = $myBaseURL.TrimEnd('/')
>> $testPaths = @("$cleanURL/messages", "$cleanURL/v1/messages")
>> $success = $false
>>
>> foreach ($url in $testPaths) {
>>     Write-Host "正在尝试: $url" -ForegroundColor Gray
>>     $jsonPayload = '{"model": "claude-3-5-sonnet-20240620", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}'
>>     $curlArgs = @("-k", "-s", "-i", "-X", "POST", $url,
>>                   "-H", "x-api-key: $apiKey",
>>                   "-H", "anthropic-version: 2023-06-01",
>>                   "-H", "Content-Type: application/json",
>>                   "-d", $jsonPayload,
>>                   "-x", $proxy)
>>
>>     $rawResponse = & curl.exe @curlArgs
>>
>>     if ($rawResponse -like "*HTTP/* 200*" -and $rawResponse -like "*content*") {
>>         Write-Host "`n🚀 验证成功！" -ForegroundColor Green
>>         Write-Host "有效接口地址: $url" -ForegroundColor Cyan
>>         $success = $true
>>         break
>>     }
>> }
>>
>> if ($success) {
>>     Write-Host "`n✨ 终端环境已就绪！你现在可以在此窗口直接运行 Cloud Code 审计命令了。" -ForegroundColor White
>> } else {
>>     Write-Host "`n❌ 验证失败。请检查：" -ForegroundColor Red
>>     Write-Host "1. 中转站余额是否充足？`n2. 代理 $proxy 是否允许了外部连接？`n3. 尝试手动访问 $myBaseURL 看看域名是否活着。" -ForegroundColor Yellow
>> }

✅ [步骤1/2] 终端环境变量注入成功。
📡 [步骤2/2] 正在自动探测最佳连接路径...
正在尝试: https://你的中转域名.com/v1/messages
正在尝试: https://你的中转域名.com/v1/v1/messages

❌ 验证失败。请检查：
1. 中转站余额是否充足？
2. 代理 http://127.0.0.1:7890 是否允许了外部连接？
3. 尝试手动访问 https://你的中转域名.com/v1 看看域名是否活着。
PS C:\Windows\System32> # 1. 核心参数
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入全局环境变量 (确保后续 Cloud Code CLI 直接可用)
>> $env:HTTP_PROXY = $proxy; $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> Write-Host "`n✅ [环境变量] 注入成功。" -ForegroundColor Green
>>
>> # 3. 暴力尝试所有可能的接口组合 (路径 x 鉴权方式)
>> $cleanURL = $myBaseURL.TrimEnd('/')
>> $paths = @("$cleanURL/messages", "$cleanURL/v1/messages", "$cleanURL")
>> $headerStyles = @(
>>     @{ "x-api-key" = $apiKey },                             # 标准 Anthropic 格式
>>     @{ "Authorization" = "Bearer $apiKey" }                 # 某些 OpenAI 格式的中转站
>> )
>>
>> Write-Host "📡 [链路验证] 正在尝试多种协议组合对接 DC 模型..." -ForegroundColor Yellow
>>
>> $success = $false
>> foreach ($p in $paths) {
>>     foreach ($h in $headerStyles) {
>>         $json = '{"model":"claude-3-5-sonnet-20240620","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
>>
>>         # 组装 curl 命令，加上 -i 显示 Header 辅助诊断
>>         $curlArgs = @("-k", "-s", "-i", "-X", "POST", $p, "-d", $json, "-x", $proxy, "-H", "Content-Type: application/json", "-H", "anthropic-version: 2023-06-01")
>>         foreach ($key in $h.Keys) { $curlArgs += "-H"; $curlArgs += "$key: $($h[$key])" }
>>
>>         $res = & curl.exe @curlArgs
>>         if ($res -like "*HTTP/* 200*" -and $res -like "*content*") {
>>             Write-Host "`n🚀 成功连通！有效接口：$p" -ForegroundColor Green
>>             Write-Host "使用的鉴权方式：$($h.Keys)" -ForegroundColor Cyan
>>             $success = $true; break
>>         }
>>     }
>>     if ($success) { break }
>> }
>>
>> if ($success) {
>>     Write-Host "`n✨ 终端对接完成！你现在可以运行 Cloud Code 审计命令了。" -ForegroundColor White
>> } else {
>>     Write-Host "`n❌ 所有组合均失败。请检查：`n1. 代理软件（如 Clash）的日志是否有红色条目？`n2. 中转站是否要求特定的 Header？" -ForegroundColor Red
>> }
ParserError:
Line |
  31 |  … ch ($key in $h.Keys) { $curlArgs += "-H"; $curlArgs += "$key: $($h[$k …
     |                                                            ~~~~~
     | Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to
     | delimit the name.
PS C:\Windows\System32> # 1. 核心参数 (请修改为你真实的域名和 Key)
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入全局环境变量 (强制 Cloud Code CLI 对齐 DC 模型)
>> $env:HTTP_PROXY = $proxy; $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> Write-Host "`n✅ [步骤1/2] 环境变量注入成功。" -ForegroundColor Green
>>
>> # 3. 最终验证 (暴力适配：同时发送两种主流鉴权 Header)
>> Write-Host "📡 [步骤2/2] 正在适配 DC 模型链路..." -ForegroundColor Yellow
>>
>> $cleanURL = $myBaseURL.TrimEnd('/')
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
PS C:\Windows\System32> Write-Host "📡 正在验证 DeepSeek 官方链路..." -ForegroundColor Yellow
>>
>> # DeepSeek 官方标准接口地址
>> $testUrl = "https://api.deepseek.com/chat/completions"
>>
>> # 构造符合 OpenAI 规范的 JSON
>> $jsonBody = '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}'
>>
>> # 使用 curl.exe 绕过 PowerShell 原生网络库的 EOF 问题
>> $curlArgs = @(
>>     "-k", "-s", "-i",
>>     "-X", "POST", $testUrl,
>>     "-H", "Authorization: Bearer sk-c8cf2fa5efc44b29b84f4ef6a7b9706e",
>>     "-H", "Content-Type: application/json",
>>     "-d", $jsonBody,
>>     "-x", "http://127.0.0.1:7890"
>> )
>>
>> $res = & curl.exe @curlArgs
>>
>> if ($res -like "*choices*") {
>>     Write-Host "`n🚀 验证成功！DeepSeek 接口已完全连通。" -ForegroundColor Green
>>     Write-Host "回复内容摘要：" -ForegroundColor Gray
>>     $res | Select-Object -Last 1 | Write-Host
>> } else {
>>     Write-Host "`n❌ 验证失败。请检查：" -ForegroundColor Red
>>     Write-Host "1. 代理软件是否正常开启了 7890 端口？`n2. 账号余额是否足够？`n3. 代理是否拦截了 api.deepseek.com 域名？" -ForegroundColor Yellow
>>     Write-Host "`n以下是原始错误响应：" -ForegroundColor Gray
>>     $res | Write-Host
>> }
📡 正在验证 DeepSeek 官方链路...

🚀 验证成功！DeepSeek 接口已完全连通。
回复内容摘要：
{"id":"daa81cff-c5b8-421d-9b51-ca7fd364ba7e","object":"chat.completion","created":1778220027,"model":"deepseek-v4-flash","choices":[{"index":0,"message":{"role":"assistant","content":"Hello! How can I help you today?"},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":5,"completion_tokens":9,"total_tokens":14,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":5},"system_fingerprint":"fp_058df29938_prod0820_fp8_kvcache_20260402"}
PS C:\Windows\System32> # 永久写入用户环境变量（以后开机即用）
>> [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-c8cf2fa5efc44b29b84f4ef6a7b9706e", "User")
>> [Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "https://api.deepseek.com/v1", "User")
>> # 设置 Node.js/Cloud Code 忽略 SSL（针对某些中转或代理抓包）
>> [Environment]::SetEnvironmentVariable("NODE_TLS_REJECT_UNAUTHORIZED", "0", "User")
PS C:\Windows\System32> # 1. 替换为你的新 Key
>>
>> $newKey = "sk-3e3869623f234533921586e27ce4ec91"
>>
>>
>>
>> # 2. 注入当前窗口变量
>>
>> $env:DEEPSEEK_API_KEY = $newKey
>>
>> $env:OPENAI_API_KEY = $newKey
>>
>> $env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"
>>
>>
>>
>> # 3. 快速静默验证 (只要返回 200 即代表新 Key 有效)
>>
>> $test = curl.exe -k -s -o /dev/null -w "%{http_code}" -X POST "https://api.deepseek.com/chat/completions" `
>>
>>     -H "Authorization: Bearer $newKey" `
>>
>>     -H "Content-Type: application/json" `
>>
>>     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}' `
>>
>>     -x "http://127.0.0.1:7890"
>>
>>
>>
>> if ($test -eq "200") {
>>
>>     Write-Host "🚀 新 Key 验证成功！状态码: 200" -ForegroundColor Green
>>
>> } else {
>>
>>     Write-Host "❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: $test" -ForegroundColor Red
>>
>> }
-H:
Line |
  21 |      -H "Authorization: Bearer $newKey" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-H:
Line |
  23 |      -H "Content-Type: application/json" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-d:
Line |
  25 |      -d '{"model":"deepseek-chat","messages":[{"role":"user","content" …
     |      ~~
     | The term '-d' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-x:
Line |
  27 |      -x "http://127.0.0.1:7890"
     |      ~~
     | The term '-x' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: 401
PS C:\Windows\System32> # 1. 替换为你的新 Key
>>
>> $newKey = "sk-3e3869623f234533921586e27ce4ec91"
>>
>>
>>
>> # 2. 注入当前窗口变量
>>
>> $env:DEEPSEEK_API_KEY = $newKey
>>
>> $env:OPENAI_API_KEY = $newKey
>>
>> $env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"
>>
>>
>>
>> # 3. 快速静默验证 (只要返回 200 即代表新 Key 有效)
>>
>> $test = curl.exe -k -s -o /dev/null -w "%{http_code}" -X POST "https://api.deepseek.com/chat/completions" `
>>
>>     -H "Authorization: Bearer $newKey" `
>>
>>     -H "Content-Type: application/json" `
>>
>>     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}' `
>>
>>     -x "http://127.0.0.1:7890"
>>
>>
>>
>> if ($test -eq "200") {
>>
>>     Write-Host "🚀 新 Key 验证成功！状态码: 200" -ForegroundColor Green
>>
>> } else {
>>
>>     Write-Host "❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: $test" -ForegroundColor Red
>>
>> }
-H:
Line |
  21 |      -H "Authorization: Bearer $newKey" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-H:
Line |
  23 |      -H "Content-Type: application/json" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-d:
Line |
  25 |      -d '{"model":"deepseek-chat","messages":[{"role":"user","content" …
     |      ~~
     | The term '-d' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-x:
Line |
  27 |      -x "http://127.0.0.1:7890"
     |      ~~
     | The term '-x' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: 000
PS C:\Windows\System32>
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

##     model = "claude-3-5-sonnet-20240620"
>>     max_tokens = 10
>>     messages = @(@{ role = "user"; content = "hi" })
>> } | ConvertTo-Json
>>
>> try {
>>     $response = Invoke-RestMethod -Uri "$myBaseURL/messages" `
>>         -Method Post `
>>         -Headers @{ "x-api-key" = $apiKey; "anthropic-version" = "2023-06-01"; "Content-Type" = "application/json" } `
>>         -Body $testPayload `
>>         -SkipCertificateCheck
>>     Write-Host "🚀 测试成功！模型回复: $($response.content[0].text)" -ForegroundColor Cyan
>> } catch {
>>     Write-Error "❌ 连接依然失败。错误信息: $_"
>>     Write-Host "提示：请检查你的代理软件是否开启了 TUN 模式，或者中转域名是否拼写正确（是否需要加 /v1）。" -ForegroundColor Yellow
>> }
✅ VS Code 配置已成功强制更新。
Write-Error: ❌ 连接依然失败。错误信息: Received an unexpected EOF or 0 bytes from the transport stream.
提示：请检查你的代理软件是否开启了 TUN 模式，或者中转域名是否拼写正确（是否需要加 /v1）。
PS C:\Windows\System32> # ================= 1. 请在此处修改你的参数 =================
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>>
>> # ================= 2. 直接复制以下全部内容并运行 =================
>> Write-Host "🚀 开始自动化配置..." -ForegroundColor Cyan
>>
>> # 强制设置当前会话的 TLS 协议和代理环境
>> [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
>> $env:HTTP_PROXY = "http://127.0.0.1:7890"; $env:HTTPS_PROXY = "http://127.0.0.1:7890"
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 自动定位并修改 VS Code 配置文件
>> $settingsPath = "$env:APPDATA\Code\User\settings.json"
>> if (Test-Path $settingsPath) {
>>     try {
>>         $json = Get-Content $settingsPath -Raw -Encoding utf8 | ConvertFrom-Json
>>         # 批量强制注入 Base URL (无论原字段是否存在)
>>         $fields = @("cline.anthropicBaseUrl", "anthropic.baseUrl", "cloudcode.claude.baseUrl")
>>         foreach ($f in $fields) {
>>             if ($json.PSObject.Properties[$f]) { $json.$f = $myBaseURL }
>>             else { $json | Add-Member -MemberType NoteProperty -Name $f -Value $myBaseURL }
>>         }
>>         $json | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
>>         Write-Host "✅ VS Code 配置文件已自动更新。" -ForegroundColor Green
>>     } catch {
>>         Write-Warning "配置文件解析异常，请检查 JSON 格式。"
>>     }
>> }
>>
>> # 自动发起接口测试
>> Write-Host "📡 正在验证链路..." -ForegroundColor Yellow
>> $body = @{ model="claude-3-5-sonnet-20240620"; max_tokens=10; messages=@(@{role="user"; content="hi"}) } | ConvertTo-Json
>> try {
>>     $res = Invoke-RestMethod -Uri "$myBaseURL/messages" -Method Post -Headers @{
>>         "x-api-key"=$apiKey; "anthropic-version"="2023-06-01"; "Content-Type"="application/json"
>>     } -Body $body -SkipCertificateCheck -TimeoutSec 15
>>     Write-Host "🚀 测试成功！模型已响应：$($res.content[0].text)" -ForegroundColor Green
>> } catch {
>>     Write-Host "❌ 依然 EOF 或连接超时。建议：1. 确认代理端口是 7890；2. 尝试给 Base URL 末尾加上/去掉 /v1" -ForegroundColor Red
>> }
🚀 开始自动化配置...
✅ VS Code 配置文件已自动更新。
📡 正在验证链路...
❌ 依然 EOF 或连接超时。建议：1. 确认代理端口是 7890；2. 尝试给 Base URL 末尾加上/去掉 /v1
PS C:\Windows\System32> # 1. 基础参数配置
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 自动化注入终端环境变量 (针对 Cloud Code CLI 和 DC 对接)
>> Write-Host "🛠️ 正在配置 PowerShell 终端环境..."  -ForegroundColor Cyan
>>
>> # 设置通用代理变量
>> $env:HTTP_PROXY  = $proxy
>> $env:HTTPS_PROXY = $proxy
>>
>> # 注入 Cloud Code 和 Claude 识别的标准环境变量
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY  = $apiKey
>>
>> # 针对 Node.js 运行时（Cloud Code 底层）的 SSL 豁免
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 3. 验证终端是否能够直连 DC 模型
>> Write-Host "📡 正在验证终端与 DC 大模型的连接..." -ForegroundColor Yellow
>>
>> $testUrl = if ($myBaseURL -like "*/v1*") { "$myBaseURL/messages" } else { "$myBaseURL/v1/messages" }
>>
>> # 使用 curl.exe 验证（避开 PowerShell 原生 netstack 的 EOF 问题）
>> $testCmd = "curl.exe -k -s -X POST `"$testUrl`" " +
>>            "-H `"x-api-key: $apiKey`" " +
>>            "-H `"anthropic-version: 2023-06-01`" " +
>>            "-H `"Content-Type: application/json`" " +
>>            "-d `"{`"model`": `"claude-3-5-sonnet-20240620`", `"max_tokens`": 10, `"messages`": [{`"role`": `"user`", `"content`": `"hi`"}]}`" " +
>>            "-x $proxy"
>>
>> $response = iex $testCmd
>>
>> if ($response -like "*content*") {
>>     Write-Host "✅ 验证成功！终端已成功对接 DC 大模型。" -ForegroundColor Green
>>     Write-Host "现在你可以直接在当前 PowerShell 会话运行 Cloud Code 审计工具了。" -ForegroundColor White
>> } else {
>>     Write-Host "❌ 验证失败，返回结果：$response" -ForegroundColor Red
>>     Write-Host "💡 请检查：1. 中转域名后缀是否正确；2. 代理端口 7890 是否开启。" -ForegroundColor Yellow
>> }
🛠️ 正在配置 PowerShell 终端环境...
📡 正在验证终端与 DC 大模型的连接...
❌ 验证失败，返回结果：
💡 请检查：1. 中转域名后缀是否正确；2. 代理端口 7890 是否开启。
PS C:\Windows\System32> # 1. 基础参数配置
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入终端环境变量 (让 Cloud Code CLI 能够识别 DC 模型)
>> $env:HTTP_PROXY = $proxy
>> $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> Write-Host "✅ 当前会话环境变量已注入。" -ForegroundColor Green
>>
>> # 3. 自动化验证连接 (改用更稳定的方式处理 curl 参数)
>> $testUrl = if ($myBaseURL -like "*/v1*") { "$myBaseURL/messages" } else { "$myBaseURL/v1/messages" }
>> $jsonPayload = '{"model": "claude-3-5-sonnet-20240620", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}'
>>
>> Write-Host "📡 正在验证终端与 DC 大模型的连接..." -ForegroundColor Yellow
>>
>> # 使用 Start-Process 配合 ArgumentList，完美避开引号解析错误
>> $curlArgs = @("-k", "-s", "-X", "POST", $testUrl,
>>               "-H", "x-api-key: $apiKey",
>>               "-H", "anthropic-version: 2023-06-01",
>>               "-H", "Content-Type: application/json",
>>               "-d", $jsonPayload,
>>               "-x", $proxy)
>>
>> $response = & curl.exe @curlArgs
>>
>> if ($response -like "*content*") {
>>     Write-Host "🚀 验证成功！你的 PowerShell 终端已对接 DC 大模型。" -ForegroundColor Green
>>     Write-Host "提示：请就在当前窗口执行你的 Cloud Code 或审计工具命令。" -ForegroundColor White
>> } else {
>>     Write-Host "❌ 验证返回空或错误。请确认：`n1. 中转域名是否拼写正确（$myBaseURL）`n2. 代理端口 $proxy 是否在运行。" -ForegroundColor Red
>>     $response | Write-Host
>> }
✅ 当前会话环境变量已注入。
📡 正在验证终端与 DC 大模型的连接...
❌ 验证返回空或错误。请确认：
1. 中转域名是否拼写正确（https://你的中转域名.com/v1）
2. 代理端口 http://127.0.0.1:7890 是否在运行。
PS C:\Windows\System32> # 1. 基础参数 (请替换为你的真实信息)
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入终端环境变量 (强制 Cloud Code CLI 及其它审计工具走中转路径)
>> $env:HTTP_PROXY = $proxy
>> $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0" # 豁免 Node.js/Cloud Code 的 SSL 校验
>>
>> Write-Host "`n✅ [步骤1/2] 终端环境变量注入成功。" -ForegroundColor Green
>>
>> # 3. 自动化链路验证 (支持多路径自动匹配)
>> Write-Host "📡 [步骤2/2] 正在自动探测最佳连接路径..." -ForegroundColor Yellow
>>
>> $cleanURL = $myBaseURL.TrimEnd('/')
>> $testPaths = @("$cleanURL/messages", "$cleanURL/v1/messages")
>> $success = $false
>>
>> foreach ($url in $testPaths) {
>>     Write-Host "正在尝试: $url" -ForegroundColor Gray
>>     $jsonPayload = '{"model": "claude-3-5-sonnet-20240620", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}'
>>     $curlArgs = @("-k", "-s", "-i", "-X", "POST", $url,
>>                   "-H", "x-api-key: $apiKey",
>>                   "-H", "anthropic-version: 2023-06-01",
>>                   "-H", "Content-Type: application/json",
>>                   "-d", $jsonPayload,
>>                   "-x", $proxy)
>>
>>     $rawResponse = & curl.exe @curlArgs
>>
>>     if ($rawResponse -like "*HTTP/* 200*" -and $rawResponse -like "*content*") {
>>         Write-Host "`n🚀 验证成功！" -ForegroundColor Green
>>         Write-Host "有效接口地址: $url" -ForegroundColor Cyan
>>         $success = $true
>>         break
>>     }
>> }
>>
>> if ($success) {
>>     Write-Host "`n✨ 终端环境已就绪！你现在可以在此窗口直接运行 Cloud Code 审计命令了。" -ForegroundColor White
>> } else {
>>     Write-Host "`n❌ 验证失败。请检查：" -ForegroundColor Red
>>     Write-Host "1. 中转站余额是否充足？`n2. 代理 $proxy 是否允许了外部连接？`n3. 尝试手动访问 $myBaseURL 看看域名是否活着。" -ForegroundColor Yellow
>> }

✅ [步骤1/2] 终端环境变量注入成功。
📡 [步骤2/2] 正在自动探测最佳连接路径...
正在尝试: https://你的中转域名.com/v1/messages
正在尝试: https://你的中转域名.com/v1/v1/messages

❌ 验证失败。请检查：
1. 中转站余额是否充足？
2. 代理 http://127.0.0.1:7890 是否允许了外部连接？
3. 尝试手动访问 https://你的中转域名.com/v1 看看域名是否活着。
PS C:\Windows\System32> # 1. 核心参数
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入全局环境变量 (确保后续 Cloud Code CLI 直接可用)
>> $env:HTTP_PROXY = $proxy; $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> Write-Host "`n✅ [环境变量] 注入成功。" -ForegroundColor Green
>>
>> # 3. 暴力尝试所有可能的接口组合 (路径 x 鉴权方式)
>> $cleanURL = $myBaseURL.TrimEnd('/')
>> $paths = @("$cleanURL/messages", "$cleanURL/v1/messages", "$cleanURL")
>> $headerStyles = @(
>>     @{ "x-api-key" = $apiKey },                             # 标准 Anthropic 格式
>>     @{ "Authorization" = "Bearer $apiKey" }                 # 某些 OpenAI 格式的中转站
>> )
>>
>> Write-Host "📡 [链路验证] 正在尝试多种协议组合对接 DC 模型..." -ForegroundColor Yellow
>>
>> $success = $false
>> foreach ($p in $paths) {
>>     foreach ($h in $headerStyles) {
>>         $json = '{"model":"claude-3-5-sonnet-20240620","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
>>
>>         # 组装 curl 命令，加上 -i 显示 Header 辅助诊断
>>         $curlArgs = @("-k", "-s", "-i", "-X", "POST", $p, "-d", $json, "-x", $proxy, "-H", "Content-Type: application/json", "-H", "anthropic-version: 2023-06-01")
>>         foreach ($key in $h.Keys) { $curlArgs += "-H"; $curlArgs += "$key: $($h[$key])" }
>>
>>         $res = & curl.exe @curlArgs
>>         if ($res -like "*HTTP/* 200*" -and $res -like "*content*") {
>>             Write-Host "`n🚀 成功连通！有效接口：$p" -ForegroundColor Green
>>             Write-Host "使用的鉴权方式：$($h.Keys)" -ForegroundColor Cyan
>>             $success = $true; break
>>         }
>>     }
>>     if ($success) { break }
>> }
>>
>> if ($success) {
>>     Write-Host "`n✨ 终端对接完成！你现在可以运行 Cloud Code 审计命令了。" -ForegroundColor White
>> } else {
>>     Write-Host "`n❌ 所有组合均失败。请检查：`n1. 代理软件（如 Clash）的日志是否有红色条目？`n2. 中转站是否要求特定的 Header？" -ForegroundColor Red
>> }
ParserError:
Line |
  31 |  … ch ($key in $h.Keys) { $curlArgs += "-H"; $curlArgs += "$key: $($h[$k …
     |                                                            ~~~~~
     | Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to
     | delimit the name.
PS C:\Windows\System32> # 1. 核心参数 (请修改为你真实的域名和 Key)
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>> $proxy = "http://127.0.0.1:7890"
>>
>> # 2. 注入全局环境变量 (强制 Cloud Code CLI 对齐 DC 模型)
>> $env:HTTP_PROXY = $proxy; $env:HTTPS_PROXY = $proxy
>> $env:ANTHROPIC_BASE_URL = $myBaseURL
>> $env:ANTHROPIC_API_KEY = $apiKey
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> Write-Host "`n✅ [步骤1/2] 环境变量注入成功。" -ForegroundColor Green
>>
>> # 3. 最终验证 (暴力适配：同时发送两种主流鉴权 Header)
>> Write-Host "📡 [步骤2/2] 正在适配 DC 模型链路..." -ForegroundColor Yellow
>>
>> $cleanURL = $myBaseURL.TrimEnd('/')
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
PS C:\Windows\System32> Write-Host "📡 正在验证 DeepSeek 官方链路..." -ForegroundColor Yellow
>>
>> # DeepSeek 官方标准接口地址
>> $testUrl = "https://api.deepseek.com/chat/completions"
>>
>> # 构造符合 OpenAI 规范的 JSON
>> $jsonBody = '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}'
>>
>> # 使用 curl.exe 绕过 PowerShell 原生网络库的 EOF 问题
>> $curlArgs = @(
>>     "-k", "-s", "-i",
>>     "-X", "POST", $testUrl,
>>     "-H", "Authorization: Bearer sk-c8cf2fa5efc44b29b84f4ef6a7b9706e",
>>     "-H", "Content-Type: application/json",
>>     "-d", $jsonBody,
>>     "-x", "http://127.0.0.1:7890"
>> )
>>
>> $res = & curl.exe @curlArgs
>>
>> if ($res -like "*choices*") {
>>     Write-Host "`n🚀 验证成功！DeepSeek 接口已完全连通。" -ForegroundColor Green
>>     Write-Host "回复内容摘要：" -ForegroundColor Gray
>>     $res | Select-Object -Last 1 | Write-Host
>> } else {
>>     Write-Host "`n❌ 验证失败。请检查：" -ForegroundColor Red
>>     Write-Host "1. 代理软件是否正常开启了 7890 端口？`n2. 账号余额是否足够？`n3. 代理是否拦截了 api.deepseek.com 域名？" -ForegroundColor Yellow
>>     Write-Host "`n以下是原始错误响应：" -ForegroundColor Gray
>>     $res | Write-Host
>> }
📡 正在验证 DeepSeek 官方链路...

🚀 验证成功！DeepSeek 接口已完全连通。
回复内容摘要：
{"id":"daa81cff-c5b8-421d-9b51-ca7fd364ba7e","object":"chat.completion","created":1778220027,"model":"deepseek-v4-flash","choices":[{"index":0,"message":{"role":"assistant","content":"Hello! How can I help you today?"},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":5,"completion_tokens":9,"total_tokens":14,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":5},"system_fingerprint":"fp_058df29938_prod0820_fp8_kvcache_20260402"}
PS C:\Windows\System32> # 永久写入用户环境变量（以后开机即用）
>> [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-c8cf2fa5efc44b29b84f4ef6a7b9706e", "User")
>> [Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "https://api.deepseek.com/v1", "User")
>> # 设置 Node.js/Cloud Code 忽略 SSL（针对某些中转或代理抓包）
>> [Environment]::SetEnvironmentVariable("NODE_TLS_REJECT_UNAUTHORIZED", "0", "User")
PS C:\Windows\System32> # 1. 替换为你的新 Key
>>
>> $newKey = "sk-3e3869623f234533921586e27ce4ec91"
>>
>>
>>
>> # 2. 注入当前窗口变量
>>
>> $env:DEEPSEEK_API_KEY = $newKey
>>
>> $env:OPENAI_API_KEY = $newKey
>>
>> $env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"
>>
>>
>>
>> # 3. 快速静默验证 (只要返回 200 即代表新 Key 有效)
>>
>> $test = curl.exe -k -s -o /dev/null -w "%{http_code}" -X POST "https://api.deepseek.com/chat/completions" `
>>
>>     -H "Authorization: Bearer $newKey" `
>>
>>     -H "Content-Type: application/json" `
>>
>>     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}' `
>>
>>     -x "http://127.0.0.1:7890"
>>
>>
>>
>> if ($test -eq "200") {
>>
>>     Write-Host "🚀 新 Key 验证成功！状态码: 200" -ForegroundColor Green
>>
>> } else {
>>
>>     Write-Host "❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: $test" -ForegroundColor Red
>>
>> }
-H:
Line |
  21 |      -H "Authorization: Bearer $newKey" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-H:
Line |
  23 |      -H "Content-Type: application/json" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-d:
Line |
  25 |      -d '{"model":"deepseek-chat","messages":[{"role":"user","content" …
     |      ~~
     | The term '-d' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-x:
Line |
  27 |      -x "http://127.0.0.1:7890"
     |      ~~
     | The term '-x' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: 401
PS C:\Windows\System32> # 1. 替换为你的新 Key
>>
>> $newKey = "sk-3e3869623f234533921586e27ce4ec91"
>>
>>
>>
>> # 2. 注入当前窗口变量
>>
>> $env:DEEPSEEK_API_KEY = $newKey
>>
>> $env:OPENAI_API_KEY = $newKey
>>
>> $env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"
>>
>>
>>
>> # 3. 快速静默验证 (只要返回 200 即代表新 Key 有效)
>>
>> $test = curl.exe -k -s -o /dev/null -w "%{http_code}" -X POST "https://api.deepseek.com/chat/completions" `
>>
>>     -H "Authorization: Bearer $newKey" `
>>
>>     -H "Content-Type: application/json" `
>>
>>     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}' `
>>
>>     -x "http://127.0.0.1:7890"
>>
>>
>>
>> if ($test -eq "200") {
>>
>>     Write-Host "🚀 新 Key 验证成功！状态码: 200" -ForegroundColor Green
>>
>> } else {
>>
>>     Write-Host "❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: $test" -ForegroundColor Red
>>
>> }
-H:
Line |
  21 |      -H "Authorization: Bearer $newKey" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-H:
Line |
  23 |      -H "Content-Type: application/json" `
     |      ~~
     | The term '-H' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-d:
Line |
  25 |      -d '{"model":"deepseek-chat","messages":[{"role":"user","content" …
     |      ~~
     | The term '-d' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
-x:
Line |
  27 |      -x "http://127.0.0.1:7890"
     |      ~~
     | The term '-x' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
❌ 新 Key 验证失败，请检查是否填写正确或额度是否激活。状态码: 000
PS C:\Windows\System32>

刚才的报错是因为 PowerShell 在处理多行命令的续行符（`）时出现了解析断点，导致它把 -H、-d 等参数当成了独立的命令去执行，所以报了“找不到命令”的错误，并最终返回了 401 或 000 状态码。
为了彻底避开 PowerShell 的换行解析问题，我们改用单行模式或者数组模式来执行。请直接复制下面这段经过修正的代码，它对格式进行了加固：
# 1. 注入新 Key
$newKey = "sk-3e3869623f234533921586e27ce4ec91"
$env:DEEPSEEK_API_KEY = $newKey
$env:OPENAI_API_KEY = $newKey
$env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"

Write-Host "📡 正在通过单行命令验证新 Key..." -ForegroundColor Yellow

# 2. 使用数组打包参数，这是 PowerShell 调用外部 exe 最稳健的方式
$curlArgs = @(
    "-k", "-s", "-o", "/dev/null", 
    "-w", "%{http_code}", 
    "-X", "POST", "https://api.deepseek.com/chat/completions",
    "-H", "Authorization: Bearer $newKey",
    "-H", "Content-Type: application/json",
    "-d", '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}',
    "-x", "http://127.0.0.1:7890"
)

$statusCode = & curl.exe @curlArgs

# 3. 判断结果
if ($statusCode -eq "200") {
    Write-Host "`n🚀 验证成功！新 Key 已激活且链路畅通。" -ForegroundColor Green
    Write-Host "环境变量已在当前窗口生效。" -ForegroundColor White
} else {
    Write-Host "`n❌ 验证失败。状态码: $statusCode" -ForegroundColor Red
    Write-Host "💡 提示：如果状态码是 401，请检查 Key 是否复制完整；如果是 000，请检查代理端口 7890 是否正常。" -ForegroundColor Yellow
}

为什么之前会失败？
PowerShell 窗口在粘贴带续行符（`）的多行代码时，如果行尾有额外的空格或者粘贴速度过快，它会认为第一行命令已经结束，从而把接下来的 -H 等参数当作新命令。这次使用的 @() 数组传参法是工业级标准，能完美避开这个问题。
执行成功后，你在这个窗口运行任何审计工具或 Cloud Code 应该就都能跑通了。

---
*从 Gemini 导出，2026-05*
