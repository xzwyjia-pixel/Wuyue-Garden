# 规则甄查 · 中转通道启动器 (GPTSAPI)
# ThinkPad P15V - E:\MyCodeProjects
# 编码: UTF-8

$env:ANTHROPIC_BASE_URL = "https://api.gptsapi.net"
$env:ANTHROPIC_API_KEY  = "sk-jAZ97d2057c7917ab9120742bebaab9d2768b612210zBdxl"

Write-Host ">>> 中转站 (GPTSAPI) - 稳定保底模式" -ForegroundColor Yellow

npx @anthropic-ai/claude-code
