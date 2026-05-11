---
title: 我现在是在Power sailor里边来执行，Cloud code对接DC的大模型，那你告诉我应该在哪里改，而且我希望是用程序自动改，而不是我去一下一项去找。 尽全力减少人工操干预。
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## 我现在是在Power sailor里边来执行，Cloud code对接DC的大模型，那你告诉我应该在哪里改，而且我希望是用程序自动改，而不是我去一下一项去找。 尽全力减少人工操干预。

## 我现在是在Power sailor里边来执行，Cloud code对接DC的大模型，那你告诉我应该在哪里改，而且我希望是用程序自动改，而不是我去一下一项去找。 尽全力减少人工操干预。

既然你希望在 PowerShell 环境下通过程序化方式自动完成修改，尽可能减少人工干预，你可以使用脚本直接修改环境变量和 VS Code 的配置文件。
你可以直接在 PowerShell 中复制并运行以下脚本，它会自动完成网络环境和 Base URL 的配置。
1. 自动配置 PowerShell 会话环境
这个脚本会自动设置当前终端的代理，并配置 Node.js（Cloud Code 的运行环境）忽略证书校验，从而解决之前出现的 SSL 握手问题。
# 1. 设置代理环境变量（请确保端口与你代理软件一致，默认7890）
$proxyAddr = "http://127.0.0.1:7890"
$env:HTTP_PROXY  = $proxyAddr
$env:HTTPS_PROXY = $proxyAddr

# 2. 强制 Node.js 忽略 SSL 证书校验（解决第三方中转站的握手问题）
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

# 3. 验证是否生效
Write-Host "当前代理已设置为: $env:HTTP_PROXY" -ForegroundColor Green
curl.exe -I https://www.google.com

2. 自动化修改 VS Code 配置文件 (Base URL)
Cloud Code 和 Cline 的设置通常存储在 settings.json 中。你可以运行以下 PowerShell 脚本来自动将 Base URL 注入到配置文件中，而不需要打开 UI 界面寻找。
# 定义你的中转站域名
$myBaseURL = "https://你的中转域名.com/v1"

# 定位 VS Code 配置文件路径
$settingsPath = "$env:APPDATA\Code\User\settings.json"

if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath | ConvertFrom-Json
    
    # 自动添加或修改 Claude 的 Base URL 配置
    # 针对不同插件的常见 key 进行批量覆盖
    $settings.'cline.anthropicBaseUrl' = $myBaseURL
    $settings.'anthropic.baseUrl' = $myBaseURL
    
    # 将修改后的配置写回文件
    $settings | ConvertTo-Json -Depth 100 | Out-File $settingsPath -Encoding utf8
    Write-Host "VS Code 配置文件已自动更新 Base URL 为: $myBaseURL" -ForegroundColor Cyan
} else {
    Write-Warning "未找到 VS Code 配置文件，请确认是否安装了 VS Code。"
}

3. 程序化验证最终链路
运行此脚本，程序会自动测试你的中转站是否能正常响应。如果返回 200，说明你的 AI 审计工具（如 audit_tool.py）可以立即开始工作。
# 请替换为你真实的 API Key
$apiKey = "你的_API_KEY"

$testPayload = @{
    model = "claude-3-5-sonnet-20240620"
    max_tokens = 10
    messages = @(@{ role = "user"; content = "connection test" })
} | ConvertTo-Json

Invoke-RestMethod -Uri "$myBaseURL/messages" `
    -Method Post `
    -Headers @{ "x-api-key" = $apiKey; "anthropic-version" = "2023-06-01"; "Content-Type" = "application/json" } `
    -Body $testPayload `
    -SkipCertificateCheck # 相当于 curl 的 -k

为什么这样做符合你的“极简”要求？

无需查找界面：直接修改底层 settings.json 文件。
一键修复握手：通过 NODE_TLS_REJECT_UNAUTHORIZED 环境变量直接打通中转站的 SSL 阻碍。
物理底座对齐：脚本执行后，你的 PowerShell 环境将处于“审计就绪”状态，直接运行你的 Python 审计工具即可。

注意：在执行脚本前，请将 $myBaseURL 和 $apiKey 替换为你中转站提供的实际信息。完成后，重启一次 VS Code 即可生效。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
