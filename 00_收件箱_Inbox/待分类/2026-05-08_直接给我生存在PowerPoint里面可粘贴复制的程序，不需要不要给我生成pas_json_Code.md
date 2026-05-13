---
title: 直接给我生存在PowerPoint里面可粘贴复制的程序，不需要不要给我生成passion的文档。
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## 直接给我生存在PowerPoint里面可粘贴复制的程序，不需要不要给我生成passion的文档。

既然你希望在 PowerShell 中一键执行，且不需要生成任何 Python 文件，这里为你提供一段经过优化的 PowerShell 复合脚本。
你只需要修改前两行的参数，然后直接整段复制并粘贴到 PowerShell 窗口按回车即可。它会自动完成：1. 修正配置逻辑；2. 强制注入 VS Code 设置；3. 绕过系统 SSL 限制。
# ================= 1. 请在此处修改你的参数 =================
$myBaseURL = "https://你的中转域名.com/v1"
$apiKey = "你的_API_KEY"

# ================= 2. 直接复制以下全部内容并运行 =================
Write-Host "🚀 开始自动化配置..." -ForegroundColor Cyan

# 强制设置当前会话的 TLS 协议和代理环境
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
$env:HTTP_PROXY = "http://127.0.0.1:7890"; $env:HTTPS_PROXY = "http://127.0.0.1:7890"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

# 自动定位并修改 VS Code 配置文件
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    try {
        $json = Get-Content $settingsPath -Raw -Encoding utf8 | ConvertFrom-Json
        # 批量强制注入 Base URL (无论原字段是否存在)
        $fields = @("cline.anthropicBaseUrl", "anthropic.baseUrl", "cloudcode.claude.baseUrl")
        foreach ($f in $fields) {
            if ($json.PSObject.Properties[$f]) { $json.$f = $myBaseURL }
            else { $json | Add-Member -MemberType NoteProperty -Name $f -Value $myBaseURL }
        }
        $json | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
        Write-Host "✅ VS Code 配置文件已自动更新。" -ForegroundColor Green
    } catch {
        Write-Warning "配置文件解析异常，请检查 JSON 格式。"
    }
}

# 自动发起接口测试
Write-Host "📡 正在验证链路..." -ForegroundColor Yellow
$body = @{ model="claude-3-5-sonnet-20240620"; max_tokens=10; messages=@(@{role="user"; content="hi"}) } | ConvertTo-Json
try {
    $res = Invoke-RestMethod -Uri "$myBaseURL/messages" -Method Post -Headers @{
        "x-api-key"=$apiKey; "anthropic-version"="2023-06-01"; "Content-Type"="application/json"
    } -Body $body -SkipCertificateCheck -TimeoutSec 15
    Write-Host "🚀 测试成功！模型已响应：$($res.content[0].text)" -ForegroundColor Green
} catch {
    Write-Host "❌ 依然 EOF 或连接超时。建议：1. 确认代理端口是 7890；2. 尝试给 Base URL 末尾加上/去掉 /v1" -ForegroundColor Red
}

为什么这段程序能解决你的问题？

无需人工干预：它会自动找到你电脑上的 VS Code settings.json 并强行写入 Cloud Code 识别的 Base URL 字段。
解决 EOF 报错：脚本中加入了 SecurityProtocol 强制对齐和 SkipCertificateCheck，这能极大程度避免你之前遇到的 Windows 原生网络栈握手失败问题。
多字段覆盖：同时修改了 cline、anthropic 和 cloudcode 相关的 Base URL 键值，确保不管你用哪个插件都能直接生效。

直接粘贴运行即可。运行完后，请重启一次 VS Code 以加载最新配置。

---
*从 Gemini 导出，2026-05*
