---
title: 2026-05-08_ComputerName _ 127.0.0.1 Remot_154
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: Python
old_category: 系统运维
tags: [gemini, 技术开发, Python]
---

## 2026-05-08_ComputerName _ 127.0.0.1 Remot_154

## 
ComputerName     : 127.0.0.1
RemoteAddress    : 127.0.0.1
RemotePort       : 7890
InterfaceAlias   : Loopback Pseudo-Interface 1
SourceAddress    : 127.0.0.1
TcpTestSucceeded : True

PS C:\Windows\System32> # 1. 强制清理环境变量干扰
>> $env:HTTP_PROXY = "http://127.0.0.1:7890"
>> $env:HTTPS_PROXY = "http://127.0.0.1:7890"
>> $env:ALL_PROXY = "http://127.0.0.1:7890"
>> $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
>>
>> # 2. 重新定义参数
>> $apiKey = "sk-3e3869623f234533921586e27ce4ec91"
>> $url = "https://api.deepseek.com/chat/completions"
>>
>> Write-Host "📡 正在尝试暴力测试 (强制无缓存 + 详细日志)..." -ForegroundColor Yellow
>>
>> # 3. 使用全路径参数，禁用所有默认配置
>> $curlArgs = @(
>>     "-v", "-k",
>>     "--proxy-ntlm", # 尝试兼容某些 Windows 代理环境
>>     "-X", "POST", $url,
>>     "-H", "Authorization: Bearer $apiKey",
>>     "-H", "Content-Type: application/json",
>>     "-d", '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}',
>>     "-x", "http://127.0.0.1:7890"
>> )
>>
>> & curl.exe @curlArgs
📡 正在尝试暴力测试 (强制无缓存 + 详细日志)...
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying 127.0.0.1:7890...
* Connected to 127.0.0.1 (127.0.0.1) port 7890
* CONNECT tunnel: HTTP/1.1 negotiated
* allocate connect buffer
* Establish HTTP proxy tunnel to api.deepseek.com:443
> CONNECT api.deepseek.com:443 HTTP/1.1
> Host: api.deepseek.com:443
> User-Agent: curl/8.9.1
> Proxy-Connection: Keep-Alive
>
< HTTP/1.1 200 Connection established
< Connection: close
<
* CONNECT phase completed
* CONNECT tunnel established, response 200
* schannel: disabled automatic use of client certificate
* ALPN: curl offers http/1.1
* ALPN: server accepted http/1.1
* using HTTP/1.x
> POST /chat/completions HTTP/1.1
> Host: api.deepseek.com
> User-Agent: curl/8.9.1
> Accept: */*
> Authorization: Bearer sk-3e3869623f234533921586e27ce4ec91
> Content-Type: application/json
> Content-Length: 69
>
* upload completely sent off: 69 bytes
* schannel: remote party requests renegotiation
* schannel: renegotiating SSL/TLS connection
* schannel: SSL/TLS connection renegotiated
< HTTP/1.1 200 OK
< Content-Type: application/json
< Transfer-Encoding: chunked
< Connection: keep-alive
< Date: Fri, 08 May 2026 06:07:05 GMT
< X-Content-Type-Options: nosniff
< Server: elb
< vary: origin, access-control-request-method, access-control-request-headers
< access-control-allow-credentials: true
< x-ds-trace-id: 82e36a191ff4946e8beebac506d88d7f
< Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
< X-Cache: Miss from cloudfront
< Via: 1.1 613f020bf9a86452b5dc81f66daf97be.cloudfront.net (CloudFront)
< X-Amz-Cf-Pop: SLC52-P1
< X-Amz-Cf-Id: ESbEzHu8LwzrUMaojWXchwSAd4v7Zr5gdmQfWya8GS9HxraOaIcjmw==
<
{"id":"1eeab5b3-7567-4dc6-9d19-dadf8b9d3da5","object":"chat.completion","created":1778220425,"model":"deepseek-v4-flash","choices":[{"index":0,"message":{"role":"assistant","content":"Hello! How can I help you today?"},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":5,"completion_tokens":9,"total_tokens":14,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":5},"system_fingerprint":"fp_058df29938_prod0820_fp8_kvcache_20260402"}* Connection #0 to host 127.0.0.1 left intact
PS C:\Windows\System32> # 确认变量存在
>> echo $env:DEEPSEEK_API_KEY
>> # 运行你的审计脚本
>> python audit_tool.py
sk-3e3869623f234533921586e27ce4ec91
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'C:\\Windows\\System32\\audit_tool.py': [Errno 2] No such file or directory
PS C:\Windows\System32> # 将下面的 sk-xxxx 替换为你新申请的 Key
>>
>> $newKey = "sk-0125d***********************8945"
>>
>>
>>
>> # 永久写入用户环境变量
>>
>> [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", $newKey, "User")
>>
>> [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $newKey, "User")
>>
>> [Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "https://api.deepseek.com/v1", "User")
>>
>>
>>
>> Write-Host "✅ 永久环境变量已更新！请重启 PowerShell 窗口以生效。" -ForegroundColor Green
✅ 永久环境变量已更新！请重启 PowerShell 窗口以生效。
PS C:\Windows\System32>

既然你已经成功将新的 API Key 写入了系统环境变量，现在的关键是解决刚才 Python 运行时的“找不到文件”错误，并正式启动你的审计工具。
1. 解决脚本路径问题
刚才报错 No such file or directory 是因为你当前处于 C:\Windows\System32 目录下，而你的 audit_tool.py 显然不在这个系统目录里。
你需要切换到脚本所在的实际文件夹：
假设你的脚本在 E:\RulesInvestigation（请根据实际情况修改）：
# 1. 切换盘符（如果是 E 盘）
E:
# 2. 进入项目目录
cd "\Your\Project\Path\RulesInvestigation" 
# 3. 运行审计脚本
python audit_tool.py


2. 激活新 Key 的“最终仪式”
由于你刚才使用的是 SetEnvironmentVariable ... "User"，当前已经打开的 PowerShell 窗口是感知不到新 Key 的。
为了确保万无一失，请按以下步骤操作：

关闭当前所有的 PowerShell 窗口。
重新打开一个新的 PowerShell 窗口。
输入以下命令确认新 Key 已经生效：
$env:DEEPSEEK_API_KEY

如果输出的是你新申请的那串 sk-0125...，说明永久配置成功！


3. 给“规则甄查”工具的配置建议
由于你的项目涉及 Model Context Protocol (MCP) 和 Ollama，在开发 audit_tool.py 时，建议在代码头部加入简单的代理检测逻辑，以防后续代理软件突然关闭导致审计中断：
import os
import requests

# 自动从环境变量读取，无需硬编码
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

# 建议在审计开始前增加一个简单的连通性自检
def check_connectivity():
    proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
    try:
        # 仅测试握手
        requests.get("https://api.deepseek.com", proxies=proxies, timeout=5)
        print("✅ 工业级私有云链路已就绪")
    except:
        print("⚠️ 警告：代理链路异常，请检查 7890 端口")

if __name__ == "__main__":
    check_connectivity()
    # 开始你的 Rules Investigation 逻辑...

接下来要做什么？
现在环境已经彻底“静奢”且稳固了。你可以直接去处理你的短视频规则审计逻辑。如果你在编写 Python 脚本处理 VLink 私有云 接口或者 MCP 协议 对接时遇到具体的代码问题，直接发给我，我们继续。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / Python · 2026-05-08*
