# 提权启动 cleanup_360.ps1
$script = "E:\MyCodeProjects\cleanup_360.ps1"
$cmd = "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
Start-Process powershell -Verb RunAs -ArgumentList $cmd -Wait
Write-Host "清理脚本已在提权窗口中执行。关闭此窗口。" -ForegroundColor Cyan
Read-Host "按 Enter 退出"
