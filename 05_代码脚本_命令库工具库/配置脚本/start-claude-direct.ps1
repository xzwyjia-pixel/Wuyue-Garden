# 规则甄查 · DeepSeek 官方直连启动器
# ThinkPad P15V - E:\MyCodeProjects
# 编码: UTF-8

$env:ANTHROPIC_BASE_URL             = "https://api.deepseek.com/anthropic"
$env:ANTHROPIC_API_KEY              = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
$env:CLAUDE_CODE_MAX_CONTEXT_TOKENS = "32768"

Write-Host ">>> 正在尝试直连 DeepSeek 官网 - 高性能模式" -ForegroundColor Green

npx @anthropic-ai/claude-code
