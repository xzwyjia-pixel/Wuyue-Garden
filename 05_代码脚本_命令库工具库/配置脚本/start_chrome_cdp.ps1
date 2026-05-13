# 启动 Chrome with CDP (供 gemini_extract.py 连接)
$CHROME = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$USER_DATA = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$CDP_PORT = 9229

Write-Host "启动 Chrome (CDP port $CDP_PORT)..." -ForegroundColor Cyan
Write-Host "请登录 gemini.google.com 后, 在另一个终端运行 python gemini_extract.py" -ForegroundColor Yellow

Start-Process -FilePath $CHROME -ArgumentList @(
    "--remote-debugging-port=$CDP_PORT",
    "--user-data-dir=$USER_DATA",
    "--start-maximized",
    "https://gemini.google.com/app"
)
