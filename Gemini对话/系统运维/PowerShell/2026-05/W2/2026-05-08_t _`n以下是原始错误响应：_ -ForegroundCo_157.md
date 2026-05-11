---
title: t "`n以下是原始错误响应：" -ForegroundColor Gray
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## t "`n以下是原始错误响应：" -ForegroundColor Gray

## t "`n以下是原始错误响应：" -ForegroundColor Gray
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
PS C:\Windows\System32> # 1. 注入新 Key
>> $newKey = "sk-3e3869623f234533921586e27ce4ec91"
>> $env:DEEPSEEK_API_KEY = $newKey
>> $env:OPENAI_API_KEY = $newKey
>> $env:OPENAI_BASE_URL = "https://api.deepseek.com/v1"
>>
>> Write-Host "📡 正在通过单行命令验证新 Key..." -ForegroundColor Yellow
>>
>> # 2. 使用数组打包参数，这是 PowerShell 调用外部 exe 最稳健的方式
>> $curlArgs = @(
>>     "-k", "-s", "-o", "/dev/null",
>>     "-w", "%{http_code}",
>>     "-X", "POST", "https://api.deepseek.com/chat/completions",
>>     "-H", "Authorization: Bearer $newKey",
>>     "-H", "Content-Type: application/json",
>>     "-d", '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"stream":false}',
>>     "-x", "http://127.0.0.1:7890"
>> )
>>
>> $statusCode = & curl.exe @curlArgs
>>
>> # 3. 判断结果
>> if ($statusCode -eq "200") {
>>     Write-Host "`n🚀 验证成功！新 Key 已激活且链路畅通。" -ForegroundColor Green
>>     Write-Host "环境变量已在当前窗口生效。" -ForegroundColor White
>> } else {
>>     Write-Host "`n❌ 验证失败。状态码: $statusCode" -ForegroundColor Red
>>     Write-Host "💡 提示：如果状态码是 401，请检查 Key 是否复制完整；如果是 000，请检查代理端口 7890 是否正常。" -ForegroundColor Yellow
>> }
📡 正在通过单行命令验证新 Key...

❌ 验证失败。状态码: 000
💡 提示：如果状态码是 401，请检查 Key 是否复制完整；如果是 000，请检查代理端口 7890 是否正常。
PS C:\Windows\System32>

状态码 000 意味着 curl 根本没有发出请求，或者在握手之前就被拦截了。既然你之前测试官方链路成功过，现在报错 000 最直接的原因通常有两个：

代理端口（7890）未开启或挂了：Clash/V2Ray 等软件可能崩溃了或关闭了系统代理。
环境变量冲突：由于你之前尝试过多种 ANTHROPIC 和 OPENAI 的变量注入，当前 PowerShell 会话可能存在逻辑混乱。

我们直接用**“最土但最暴力”**的方式排查。请依次执行以下操作：
1. 确认代理存活
请直接在终端输入并回车：
Test-NetConnection -ComputerName 127.0.0.1 -Port 7890


如果是 False：说明你的代理软件没开，或者端口不是 7890。请检查 Clash/代理软件。
如果是 True：请继续下一步。


2. 彻底清除干扰，重建链路
我们将不依赖之前设置的环境变量，直接运行一个全路径测试。请将下方代码一次性复制运行：
# 1. 强制清理环境变量干扰（仅限当前窗口）
$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"

# 2. 重新定义参数
$apiKey = "sk-3e3869623f234533921586e27ce4ec91"
$url = "https://api.deepseek.com/chat/completions"

Write-Host "📡 正在尝试跳过变量直接探测..." -ForegroundColor Yellow

# 3. 极简测试命令
$res = & curl.exe -k -v -X POST $url `
    -H "Authorization: Bearer $apiKey" `
    -H "Content-Type: application/json" `
    -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}' `
    -x "http://127.0.0.1:7890" 2>&1

# 4. 分析返回
if ($res -like "*choices*") {
    Write-Host "`n🚀 连通成功！Key 和代理都没问题。" -ForegroundColor Green
} elseif ($res -like "*401*") {
    Write-Host "`n❌ 鉴权失败 (401)。请检查 DeepSeek 后台新 Key 是否已生效。" -ForegroundColor Red
} else {
    Write-Host "`n❌ 仍然失败。请查看下方的详细日志分析原因：" -ForegroundColor Red
    $res | Select-Object -First 20 | Write-Host
}


3. 如果还是 000 且详细日志里有 "Could not resolve host"
这通常是 DNS 解析在代理层面出了问题。尝试在你的代理软件（如 Clash）中：

切换一个节点。
确保开启了 TUN 模式 或 System Proxy。
检查是否有红色报错日志（通常会提示 Connection refused）。

补充建议：
如果你正在公司网络环境下，可能存在更严格的防火墙。既然你已经把 Key 写入了系统用户变量，建议重启一次 PowerShell，让之前的变量清理干净，直接运行上面的“极简测试命令”。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
