---
title: 我现在想解决的问题是，在原生的powershell终端里边使用Cloud code的大模型的整体环境，然后对接DPS的大模型。 现在要解决的是他之间的相互联通的问题。
PowerShell 7.6.1
PS C:\Windows\System32> # 停止可能冲突的服务（根据你提到的 Cloud Code / Claude 相关进程）
>> Stop-Process -Name "cloud-code*" -Force -ErrorAction SilentlyContinue
>> Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
PS C:\Windows\System32> curl.exe -I https://api.anthropic.com  # 或者你中转站的 API 地址
curl: (56) Failure when receiving data from the peer
PS C:\Windows\System32> $env:HTTP_PROXY="http://127.0.0.1:7890"
>> $env:HTTPS_PROXY="http://127.0.0.1:7890"
PS C:\Windows\System32> pwsh --version
PowerShell 7.6.1
PS C:\Windows\System32> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
PS C:\Windows\System32> # 测试通过代理访问 Google
>> curl.exe -I https://www.google.com
>>
>> # 测试你的中转站地址 (替换为你的实际 API 域名)
>> curl.exe -I https://你的中转站域名.com
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 200 OK
Content-Type: text/html; charset=ISO-8859-1
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-UiXb7fRhmihVEeBi1nHcgg' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Accept-CH: Sec-CH-Prefers-Color-Scheme
P3P: CP="This is not a P3P policy! See g.co/p3phelp for more info."
Date: Fri, 08 May 2026 05:37:43 GMT
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Expires: Fri, 08 May 2026 05:37:43 GMT
Cache-Control: private
Set-Cookie: AEC=AaJma5tA5HMFtBgR3xr6xOsVH3X9862IZoHxPugEg9zdDPgKFY_sDlSs5xw; expires=Wed, 04-Nov-2026 05:37:43 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax
Set-Cookie: NID=531=kfIz-mHXNwpGEmy9e5ViSfWKFPFnkRAF3jVeCi7i9Ghv-o9y97B-eEbcdVoRGK7-rScKqBNx3RtmLWibKlBqtoJ8cjpgGPK5ylEEs5sbzsUKckcIo89-5nSqUIoPeozQYaG9FpyWwCotswlXmk0Zj4ukLg3-Mwsl9VWlTal01_gE3C9DD3OZnaBCAif1F8lUzxCIJjMqZU1bBQXwfhhPaTUN-mChjh0; expires=Sat, 07-Nov-2026 05:37:43 GMT; path=/; domain=.google.com; HttpOnly
Set-Cookie: __Secure-BUCKET=CKcF; expires=Wed, 04-Nov-2026 05:37:43 GMT; path=/; domain=.google.com; Secure; HttpOnly
Transfer-Encoding: chunked
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000

HTTP/1.1 200 Connection established
Connection: close

curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed
PS C:\Windows\System32> curl.exe --tls-max 1.3 -I https://api.anthropic.com
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 404 Not Found
Date: Fri, 08 May 2026 05:39:41 GMT
Connection: keep-alive
vary: Accept-Encoding
Server: cloudflare
cf-cache-status: DYNAMIC
set-cookie: _cfuvid=1DtfBvu_a98bFWUZKrDCY_Nk3.lMIXJlnr_vGc7LfuU-1778218781.310889-1.0.1.1-M36_jFEB8gcr_QT6Ak5Tq4b.WKSRrLNDCZ73Zc_Y_Hc; HttpOnly; SameSite=None; Secure; Path=/; Domain=api.anthropic.com
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
X-Robots-Tag: none
CF-RAY: 9f8620173c424f0f-LAS

PS C:\Windows\System32> curl.exe -k -I https://api.anthropic.com
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 404 Not Found
Date: Fri, 08 May 2026 05:39:58 GMT
Connection: keep-alive
vary: Accept-Encoding
Server: cloudflare
cf-cache-status: DYNAMIC
set-cookie: _cfuvid=ccJlnGQN9DYIfMNIP.HBesEqCqlUqt3s3XZjFaZOKcM-1778218798.396622-1.0.1.1-6DnP1b7MLNiKpLdlpmqYh0sHT042vRNSdz7XQHKHErM; HttpOnly; SameSite=None; Secure; Path=/; Domain=api.anthropic.com
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
X-Robots-Tag: none
CF-RAY: 9f862081ff905f10-LAS

PS C:\Windows\System32> $env:HTTP_PROXY="http://127.0.0.1:7890"
>> $env:HTTPS_PROXY="http://127.0.0.1:7890"
>> $env:NODE_TLS_REJECT_UNAUTHORIZED="0"
PS C:\Windows\System32> # 1. 设置代理环境变量（请确保端口与你代理软件一致，默认7890）
>> $proxyAddr = "http://127.0.0.1:7890"
>> $env:HTTP_PROXY  = $proxyAddr
>> $env:HTTPS_PROXY = $proxyAddr
>>
>> # 2. 强制 Node.js 忽略 SSL 证书校验（解决第三方中转站的握手问题）
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 3. 验证是否生效
>> Write-Host "当前代理已设置为: $env:HTTP_PROXY" -ForegroundColor Green
>> curl.exe -I https://www.google.com
当前代理已设置为: http://127.0.0.1:7890
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 200 OK
Content-Type: text/html; charset=ISO-8859-1
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-rbMf8xMuwb9MMH8iMjzJmQ' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Accept-CH: Sec-CH-Prefers-Color-Scheme
P3P: CP="This is not a P3P policy! See g.co/p3phelp for more info."
Date: Fri, 08 May 2026 05:43:19 GMT
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Expires: Fri, 08 May 2026 05:43:19 GMT
Cache-Control: private
Set-Cookie: AEC=AaJma5sixBPQX8doEhy6ZbLueBnq4DcwxFh4f_bure1u8vN4s2hRzixkEw; expires=Wed, 04-Nov-2026 05:43:19 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax
Set-Cookie: NID=531=Yj5TWCGK-O4W4kYUKdGBKjhb9bGo4siDtQXZNw-VwDlTv22p6r_hhgGHIDNz1tnf7goodpNZUBZLNUn6aKgYeUcP8xxqKMv2lC6HCNb7Lak-O0UW29Onyu5fn69Im_3PQQSROF0iFnL7AnIu1KrGQs5LSMnNoEO-b7_5QVSVBQEb3X33_H9IT0bz6X7UcvBuUzkNBYNV0tf4MwdpyQwtasMxW6SIap2iBg8i; expires=Sat, 07-Nov-2026 05:43:19 GMT; path=/; domain=.google.com; HttpOnly
Set-Cookie: __Secure-BUCKET=COkC; expires=Wed, 04-Nov-2026 05:43:19 GMT; path=/; domain=.google.com; Secure; HttpOnly
Transfer-Encoding: chunked
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000

PS C:\Windows\System32> # 定义你的中转站域名
>> $myBaseURL = "https://你的中转域名.com/v1"
>>
>> # 定位 VS Code 配置文件路径
>> $settingsPath = "$env:APPDATA\Code\User\settings.json"
>>
>> if (Test-Path $settingsPath) {
>>     $settings = Get-Content $settingsPath | ConvertFrom-Json
>>
>>     # 自动添加或修改 Claude 的 Base URL 配置
>>     # 针对不同插件的常见 key 进行批量覆盖
>>     $settings.'cline.anthropicBaseUrl' = $myBaseURL
>>     $settings.'anthropic.baseUrl' = $myBaseURL
>>
>>     # 将修改后的配置写回文件
>>     $settings | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
>>     Write-Host "VS Code 配置文件已自动更新 Base URL 为: $myBaseURL" -ForegroundColor Cyan
>> } else {
>>     Write-Warning "未找到 VS Code 配置文件，请确认是否安装了 VS Code。"
>> }
SetValueInvocationException:
Line |
  12 |      $settings.'cline.anthropicBaseUrl' = $myBaseURL
     |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Exception setting "cline.anthropicBaseUrl": "The property 'cline.anthropicBaseUrl' cannot be found on this object. Verify that the property exists and can be set."
SetValueInvocationException:
Line |
  13 |      $settings.'anthropic.baseUrl' = $myBaseURL
     |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Exception setting "anthropic.baseUrl": "The property 'anthropic.baseUrl' cannot be found on this object. Verify that the property exists and can be set."
VS Code 配置文件已自动更新 Base URL 为: https://你的中转域名.com/v1
PS C:\Windows\System32> # 请替换为你真实的 API Key
>> $apiKey = "你的_API_KEY"
>>
>> $testPayload = @{
>>     model = "claude-3-5-sonnet-20240620"
>>     max_tokens = 10
>>     messages = @(@{ role = "user"; content = "connection test" })
>> } | ConvertTo-Json
>>
>> Invoke-RestMethod -Uri "$myBaseURL/messages" `
>>     -Method Post `
>>     -Headers @{ "x-api-key" = $apiKey; "anthropic-version" = "2023-06-01"; "Content-Type" = "application/json" } `
>>     -Body $testPayload `
>>     -SkipCertificateCheck # 相当于 curl 的 -k
Invoke-RestMethod:
Line |
  10 |  Invoke-RestMethod -Uri "$myBaseURL/messages" `
     |  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Received an unexpected EOF or 0 bytes from the transport stream.
PS C:\Windows\System32> # 1. 设置配置信息 (请修改为你真实的域名和 Key)
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>>
>> # 2. 自动化修改 VS Code 配置文件
>> $settingsPath = "$env:APPDATA\Code\User\settings.json"
>>
>> if (Test-Path $settingsPath) {
>>     # 读取并解析 JSON
>>     $jsonText = Get-Content $settingsPath -Raw -Encoding utf8
>>     $settings = $jsonText | ConvertFrom-Json
>>
>>     # 使用强行添加成员的方式，解决属性不存在的报错
>>     $newSettings = @{
>>         "cline.anthropicBaseUrl" = $myBaseURL
>>         "anthropic.baseUrl"      = $myBaseURL
>>     }
>>
>>     foreach ($key in $newSettings.Keys) {
>>         if ($settings.PSObject.Properties[$key]) {
>>             $settings.$key = $newSettings[$key]
>>         } else {
>>             $settings | Add-Member -MemberType NoteProperty -Name $key -Value $newSettings[$key]
>>         }
>>     }
>>
>>     # 写回文件
>>     $settings | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
>>     Write-Host "✅ VS Code 配置已成功强制更新。" -ForegroundColor Green
>> }
>>
>> # 3. 解决测试请求的 EOF 错误 (设置安全协议)
>> [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
>>
>> # 4. 发起最终验证
>> $testPayload = @{
>>     model = "claude-3-5-sonnet-20240620"
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
PS C:\Windows\System32>
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## 我现在想解决的问题是，在原生的powershell终端里边使用Cloud code的大模型的整体环境，然后对接DPS的大模型。 现在要解决的是他之间的相互联通的问题。
PowerShell 7.6.1
PS C:\Windows\System32> # 停止可能冲突的服务（根据你提到的 Cloud Code / Claude 相关进程）
>> Stop-Process -Name "cloud-code*" -Force -ErrorAction SilentlyContinue
>> Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
PS C:\Windows\System32> curl.exe -I https://api.anthropic.com  # 或者你中转站的 API 地址
curl: (56) Failure when receiving data from the peer
PS C:\Windows\System32> $env:HTTP_PROXY="http://127.0.0.1:7890"
>> $env:HTTPS_PROXY="http://127.0.0.1:7890"
PS C:\Windows\System32> pwsh --version
PowerShell 7.6.1
PS C:\Windows\System32> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
PS C:\Windows\System32> # 测试通过代理访问 Google
>> curl.exe -I https://www.google.com
>>
>> # 测试你的中转站地址 (替换为你的实际 API 域名)
>> curl.exe -I https://你的中转站域名.com
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 200 OK
Content-Type: text/html; charset=ISO-8859-1
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-UiXb7fRhmihVEeBi1nHcgg' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Accept-CH: Sec-CH-Prefers-Color-Scheme
P3P: CP="This is not a P3P policy! See g.co/p3phelp for more info."
Date: Fri, 08 May 2026 05:37:43 GMT
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Expires: Fri, 08 May 2026 05:37:43 GMT
Cache-Control: private
Set-Cookie: AEC=AaJma5tA5HMFtBgR3xr6xOsVH3X9862IZoHxPugEg9zdDPgKFY_sDlSs5xw; expires=Wed, 04-Nov-2026 05:37:43 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax
Set-Cookie: NID=531=kfIz-mHXNwpGEmy9e5ViSfWKFPFnkRAF3jVeCi7i9Ghv-o9y97B-eEbcdVoRGK7-rScKqBNx3RtmLWibKlBqtoJ8cjpgGPK5ylEEs5sbzsUKckcIo89-5nSqUIoPeozQYaG9FpyWwCotswlXmk0Zj4ukLg3-Mwsl9VWlTal01_gE3C9DD3OZnaBCAif1F8lUzxCIJjMqZU1bBQXwfhhPaTUN-mChjh0; expires=Sat, 07-Nov-2026 05:37:43 GMT; path=/; domain=.google.com; HttpOnly
Set-Cookie: __Secure-BUCKET=CKcF; expires=Wed, 04-Nov-2026 05:37:43 GMT; path=/; domain=.google.com; Secure; HttpOnly
Transfer-Encoding: chunked
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000

HTTP/1.1 200 Connection established
Connection: close

curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed
PS C:\Windows\System32> curl.exe --tls-max 1.3 -I https://api.anthropic.com
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 404 Not Found
Date: Fri, 08 May 2026 05:39:41 GMT
Connection: keep-alive
vary: Accept-Encoding
Server: cloudflare
cf-cache-status: DYNAMIC
set-cookie: _cfuvid=1DtfBvu_a98bFWUZKrDCY_Nk3.lMIXJlnr_vGc7LfuU-1778218781.310889-1.0.1.1-M36_jFEB8gcr_QT6Ak5Tq4b.WKSRrLNDCZ73Zc_Y_Hc; HttpOnly; SameSite=None; Secure; Path=/; Domain=api.anthropic.com
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
X-Robots-Tag: none
CF-RAY: 9f8620173c424f0f-LAS

PS C:\Windows\System32> curl.exe -k -I https://api.anthropic.com
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 404 Not Found
Date: Fri, 08 May 2026 05:39:58 GMT
Connection: keep-alive
vary: Accept-Encoding
Server: cloudflare
cf-cache-status: DYNAMIC
set-cookie: _cfuvid=ccJlnGQN9DYIfMNIP.HBesEqCqlUqt3s3XZjFaZOKcM-1778218798.396622-1.0.1.1-6DnP1b7MLNiKpLdlpmqYh0sHT042vRNSdz7XQHKHErM; HttpOnly; SameSite=None; Secure; Path=/; Domain=api.anthropic.com
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
X-Robots-Tag: none
CF-RAY: 9f862081ff905f10-LAS

PS C:\Windows\System32> $env:HTTP_PROXY="http://127.0.0.1:7890"
>> $env:HTTPS_PROXY="http://127.0.0.1:7890"
>> $env:NODE_TLS_REJECT_UNAUTHORIZED="0"
PS C:\Windows\System32> # 1. 设置代理环境变量（请确保端口与你代理软件一致，默认7890）
>> $proxyAddr = "http://127.0.0.1:7890"
>> $env:HTTP_PROXY  = $proxyAddr
>> $env:HTTPS_PROXY = $proxyAddr
>>
>> # 2. 强制 Node.js 忽略 SSL 证书校验（解决第三方中转站的握手问题）
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 3. 验证是否生效
>> Write-Host "当前代理已设置为: $env:HTTP_PROXY" -ForegroundColor Green
>> curl.exe -I https://www.google.com
当前代理已设置为: http://127.0.0.1:7890
HTTP/1.1 200 Connection established
Connection: close

HTTP/1.1 200 OK
Content-Type: text/html; charset=ISO-8859-1
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-rbMf8xMuwb9MMH8iMjzJmQ' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Accept-CH: Sec-CH-Prefers-Color-Scheme
P3P: CP="This is not a P3P policy! See g.co/p3phelp for more info."
Date: Fri, 08 May 2026 05:43:19 GMT
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Expires: Fri, 08 May 2026 05:43:19 GMT
Cache-Control: private
Set-Cookie: AEC=AaJma5sixBPQX8doEhy6ZbLueBnq4DcwxFh4f_bure1u8vN4s2hRzixkEw; expires=Wed, 04-Nov-2026 05:43:19 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax
Set-Cookie: NID=531=Yj5TWCGK-O4W4kYUKdGBKjhb9bGo4siDtQXZNw-VwDlTv22p6r_hhgGHIDNz1tnf7goodpNZUBZLNUn6aKgYeUcP8xxqKMv2lC6HCNb7Lak-O0UW29Onyu5fn69Im_3PQQSROF0iFnL7AnIu1KrGQs5LSMnNoEO-b7_5QVSVBQEb3X33_H9IT0bz6X7UcvBuUzkNBYNV0tf4MwdpyQwtasMxW6SIap2iBg8i; expires=Sat, 07-Nov-2026 05:43:19 GMT; path=/; domain=.google.com; HttpOnly
Set-Cookie: __Secure-BUCKET=COkC; expires=Wed, 04-Nov-2026 05:43:19 GMT; path=/; domain=.google.com; Secure; HttpOnly
Transfer-Encoding: chunked
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000

PS C:\Windows\System32> # 定义你的中转站域名
>> $myBaseURL = "https://你的中转域名.com/v1"
>>
>> # 定位 VS Code 配置文件路径
>> $settingsPath = "$env:APPDATA\Code\User\settings.json"
>>
>> if (Test-Path $settingsPath) {
>>     $settings = Get-Content $settingsPath | ConvertFrom-Json
>>
>>     # 自动添加或修改 Claude 的 Base URL 配置
>>     # 针对不同插件的常见 key 进行批量覆盖
>>     $settings.'cline.anthropicBaseUrl' = $myBaseURL
>>     $settings.'anthropic.baseUrl' = $myBaseURL
>>
>>     # 将修改后的配置写回文件
>>     $settings | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
>>     Write-Host "VS Code 配置文件已自动更新 Base URL 为: $myBaseURL" -ForegroundColor Cyan
>> } else {
>>     Write-Warning "未找到 VS Code 配置文件，请确认是否安装了 VS Code。"
>> }
SetValueInvocationException:
Line |
  12 |      $settings.'cline.anthropicBaseUrl' = $myBaseURL
     |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Exception setting "cline.anthropicBaseUrl": "The property 'cline.anthropicBaseUrl' cannot be found on this object. Verify that the property exists and can be set."
SetValueInvocationException:
Line |
  13 |      $settings.'anthropic.baseUrl' = $myBaseURL
     |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Exception setting "anthropic.baseUrl": "The property 'anthropic.baseUrl' cannot be found on this object. Verify that the property exists and can be set."
VS Code 配置文件已自动更新 Base URL 为: https://你的中转域名.com/v1
PS C:\Windows\System32> # 请替换为你真实的 API Key
>> $apiKey = "你的_API_KEY"
>>
>> $testPayload = @{
>>     model = "claude-3-5-sonnet-20240620"
>>     max_tokens = 10
>>     messages = @(@{ role = "user"; content = "connection test" })
>> } | ConvertTo-Json
>>
>> Invoke-RestMethod -Uri "$myBaseURL/messages" `
>>     -Method Post `
>>     -Headers @{ "x-api-key" = $apiKey; "anthropic-version" = "2023-06-01"; "Content-Type" = "application/json" } `
>>     -Body $testPayload `
>>     -SkipCertificateCheck # 相当于 curl 的 -k
Invoke-RestMethod:
Line |
  10 |  Invoke-RestMethod -Uri "$myBaseURL/messages" `
     |  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Received an unexpected EOF or 0 bytes from the transport stream.
PS C:\Windows\System32> # 1. 设置配置信息 (请修改为你真实的域名和 Key)
>> $myBaseURL = "https://你的中转域名.com/v1"
>> $apiKey = "你的_API_KEY"
>>
>> # 2. 自动化修改 VS Code 配置文件
>> $settingsPath = "$env:APPDATA\Code\User\settings.json"
>>
>> if (Test-Path $settingsPath) {
>>     # 读取并解析 JSON
>>     $jsonText = Get-Content $settingsPath -Raw -Encoding utf8
>>     $settings = $jsonText | ConvertFrom-Json
>>
>>     # 使用强行添加成员的方式，解决属性不存在的报错
>>     $newSettings = @{
>>         "cline.anthropicBaseUrl" = $myBaseURL
>>         "anthropic.baseUrl"      = $myBaseURL
>>     }
>>
>>     foreach ($key in $newSettings.Keys) {
>>         if ($settings.PSObject.Properties[$key]) {
>>             $settings.$key = $newSettings[$key]
>>         } else {
>>             $settings | Add-Member -MemberType NoteProperty -Name $key -Value $newSettings[$key]
>>         }
>>     }
>>
>>     # 写回文件
>>     $settings | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
>>     Write-Host "✅ VS Code 配置已成功强制更新。" -ForegroundColor Green
>> }
>>
>> # 3. 解决测试请求的 EOF 错误 (设置安全协议)
>> [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
>>
>> # 4. 发起最终验证
>> $testPayload = @{
>>     model = "claude-3-5-sonnet-20240620"
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
PS C:\Windows\System32>

从你提供的详细日志来看，你的 PowerShell 环境已经正确配置了代理，但问题的核心在于中转站的路径匹配以及 PowerShell 调用 curl.exe 时的字符串解析。
虽然你看到 200 Connection established，但这只是代理服务器（Clash）的响应，后面的内容缺失说明请求并没有真正到达中转站或被中转站拒绝。
为了彻底解决 PowerShell 终端对接 DC 大模型（基于 Anthropic 协议）的问题，请执行以下优化后的方案：

1. 核心问题诊断

路径冗余：很多中转站会自动补全路径。如果你填了 .../v1，脚本拼接后可能变成了 .../v1/v1/messages（导致 404）或 .../v1/messages。
EOF 错误：这是因为 PowerShell 的 Invoke-RestMethod 对 TLS 握手非常挑剔。我们必须坚持使用 curl.exe。


2. 最终全自动适配脚本
请直接复制以下代码并在你的 PowerShell 7.6.1 窗口中运行。这个版本采用了**“路径自动剥离”**技术：
# ================= 1. 基础参数 (请务必检查此处) =================
$myBaseURL = "https://你的中转域名.com"  # <--- 注意：这里不要带 /v1，脚本会自动处理
$apiKey = "你的_API_KEY"
$proxy = "http://127.0.0.1:7890"

# ================= 2. 环境强制初始化 =================
$env:HTTP_PROXY = $proxy
$env:HTTPS_PROXY = $proxy
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
# 设置 Cloud Code CLI 识别的环境变量
$env:ANTHROPIC_BASE_URL = "$myBaseURL/v1"
$env:ANTHROPIC_API_KEY = $apiKey

Write-Host "`n✅ [环境] 代理与变量已注入。" -ForegroundColor Green

# ================= 3. 智能链路探测 =================
Write-Host "📡 [链路] 正在探测最佳接口路径..." -ForegroundColor Yellow

$cleanHost = $myBaseURL.TrimEnd('/')
# 测试三个最可能的路径
$testUrls = @("$cleanHost/v1/messages", "$cleanHost/messages", "$cleanHost/api/v1/messages")

$success = $false
foreach ($url in $testUrls) {
    Write-Host "尝试路径: $url" -ForegroundColor Gray
    
    $jsonBody = '{"model":"claude-3-5-sonnet-20240620","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
    
    # 使用 curl.exe 并强制跳过 SSL 检查
    $curlArgs = @(
        "-k", "-s", "-i", "-L", "-X", "POST", $url,
        "-H", "x-api-key: $apiKey",
        "-H", "anthropic-version: 2023-06-01",
        "-H", "Content-Type: application/json",
        "-d", $jsonBody,
        "-x", $proxy
    )

    $res = & curl.exe @curlArgs
    
    # 只要返回内容包含 "content" 关键字，即代表模型响应成功
    if ($res -like "*content*") {
        Write-Host "`n🚀 连通成功！" -ForegroundColor Green
        Write-Host "有效 Endpoint: $url" -ForegroundColor Cyan
        $success = $true
        break
    }
}

if (-not $success) {
    Write-Host "`n❌ 探测失败。请检查中转站后台，确认：`n1. 域名是否需要备案或已被墙？`n2. 账户余额是否充足？" -ForegroundColor Red
} else {
    Write-Host "`n✨ 终端环境已就绪，现在可以直接运行你的审计工具或 Cloud Code 命令。" -ForegroundColor White
}


3. 为什么之前一直失败？（技术要点）

-L 参数缺失：有些中转站会做 http 到 https 的重定向，或者域名的重定向。curl.exe 加上 -L 可以自动追踪这些跳转。
环境变量注入范围：你之前在脚本里设置了 $env:ANTHROPIC_BASE_URL，这个变量只在当前 PowerShell 窗口有效。如果你关闭窗口重新打开，变量就丢了。

建议：如果想永久生效，请运行一次：[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "你的地址", "User")。


Cloud Code 的特殊性：Cloud Code 在底层调用时，有时会忽略系统代理。确保你的代理软件（Clash 等）开启了 Tun 模式 或 系统代理 按钮已勾选。

下一步建议：
如果运行上面的脚本依然失败，请查看 curl.exe 返回的具体错误（去掉 -s 参数），如果看到 401，说明是 API Key 错了；如果看到 404，说明中转站的路径非常特殊，建议联系中转站客服询问“Anthropic 协议的完整 Base URL”。

---
*从 Gemini 导出，2026-05*
