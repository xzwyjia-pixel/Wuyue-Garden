param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status,
    [switch]$Stop
)

$BASE = "E:\MyCodeProjects"
$AUDIO_LOG = "$BASE\06-存档中心\logs\audio.log"
$STT_LOG = "$BASE\06-存档中心\logs\stt.log"
$MONITOR_LOG = "$BASE\06-存档中心\logs\monitor.log"
$PID_FILE = "$BASE\06-存档中心\logs\susu_pids.json"
$AUDIO_DIR = "$BASE\04-宝妈直播诊断系统\苏苏在浙里\audio"
$TASK_NAME = "SuSuLiveMonitor"

function Write-Status {
    param([string]$Msg, [string]$Color="White")
    $t = Get-Date -Format "HH:mm:ss"
    Write-Host "[$t] $Msg" -ForegroundColor $Color
}

function Save-Pids {
    param($Pids)
    $Pids | ConvertTo-Json | Set-Content $PID_FILE -Encoding utf8
}

function Load-Pids {
    if (Test-Path $PID_FILE) {
        return Get-Content $PID_FILE -Raw | ConvertFrom-Json
    }
    return @{}
}

function Start-MonitorStack {
    Write-Status "===== 苏苏在浙里 监控系统启动 =====" -Color Cyan

    # 1. 音频采集 (后台, 无窗口)
    Write-Status "[1/3] 启动音频采集..." -Color Yellow
    $audio = Start-Process powershell -ArgumentList @"
        -NoProfile -WindowStyle Hidden -Command "
            try {
                cd '$BASE\审计工具'
                python audio_capture.py --target '$BASE\04-宝妈直播诊断系统\苏苏在浙里'
            } catch {
                'audio crash: ' + `$_ | Out-File '$AUDIO_LOG' -Append
            }
        "
"@ -PassThru -WindowStyle Hidden
    Write-Status "  音频PID: $($audio.Id)" -Color Green

    # 2. STT 转写 (后台, 无窗口)
    Write-Status "[2/3] 启动语音转写..." -Color Yellow
    $stt = Start-Process powershell -ArgumentList @"
        -NoProfile -WindowStyle Hidden -Command "
            try {
                cd '$BASE\审计工具'
                python whisper_stt.py --target '$BASE\04-宝妈直播诊断系统\苏苏在浙里'
            } catch {
                'stt crash: ' + `$_ | Out-File '$STT_LOG' -Append
            }
        "
"@ -PassThru -WindowStyle Hidden
    Write-Status "  STT PID: $($stt.Id)" -Color Green

    # 3. 画面监控 (前台, 可见窗口)
    Write-Status "[3/3] 启动画面监控..." -Color Yellow
    $monitor = Start-Process powershell -ArgumentList @"
        -NoExit -Command "
            cd '$BASE\审计工具'
            python monitor_susu_pro.py
        "
"@ -PassThru
    Write-Status "  监控PID: $($monitor.Id)" -Color Green

    # 保存 PID
    $pids = @{
        audio = $audio.Id
        stt = $stt.Id
        monitor = $monitor.Id
        started = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    }
    Save-Pids $pids

    Write-Status "===== 全链路已启动 =====" -Color Cyan
    Write-Status "  音频日志: $AUDIO_LOG"
    Write-Status "  STT日志:  $STT_LOG"
    Write-Status "  监控日志: $MONITOR_LOG"
    Write-Status "  音频文件: $AUDIO_DIR"
    return $pids
}

function Stop-MonitorStack {
    Write-Status "===== 停止监控系统 =====" -Color Red
    $pids = Load-Pids
    if (-not $pids) {
        Write-Status "  无运行记录" -Color Yellow
        return
    }
    $stopped = @()
    foreach ($name in @('monitor', 'audio', 'stt')) {
        $pid = $pids.$name
        if ($pid) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Status "  已停止 $name (PID:$pid)" -Color Red
                $stopped += $name
            } catch {
                Write-Status "  $name (PID:$pid) 不在运行" -Color Yellow
            }
        }
    }
    # 清理残留 Python 进程 (以防有孤儿进程)
    Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -match "monitor_susu|audio_capture|whisper_stt"
    } | Stop-Process -Force -ErrorAction SilentlyContinue

    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    Write-Status "  已清理 PID 文件" -Color Yellow
    Write-Status "===== 已全部停止 =====" -Color Red
}

function Get-MonitorStatus {
    Write-Status "===== 监控系统状态 =====" -Color Cyan
    $pids = Load-Pids
    if (-not $pids) {
        Write-Status "  状态: 未运行" -Color Yellow
        return
    }
    Write-Status "  启动时间: $($pids.started)" -Color White

    foreach ($name in @('monitor', 'audio', 'stt')) {
        $pid = $pids.$name
        $running = $false
        if ($pid) {
            try {
                $proc = Get-Process -Id $pid -ErrorAction Stop
                $running = $true
                Write-Status "  [$name] PID:$pid $(Get-Date $proc.StartTime -Format 'HH:mm:ss') → 运行中" -Color Green
            } catch {
                Write-Status "  [$name] PID:$pid → 已停止" -Color Red
            }
        }
    }

    # 音频文件统计
    if (Test-Path $AUDIO_DIR) {
        $count = (Get-ChildItem $AUDIO_DIR -Filter "*.wav" | Measure-Object).Count
        $size = (Get-ChildItem $AUDIO_DIR -Filter "*.wav" | Measure-Object Length -Sum).Sum / 1MB
        Write-Status "  音频文件: ${count}个 (${size:n1}MB)" -Color Gray
    }
}

function Install-AutoStart {
    Write-Status "===== 注册开机自启动 =====" -Color Cyan

    $scriptPath = "$BASE\审计工具\start_susu_monitor.ps1"
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    try {
        Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Principal $principal -Force
        Write-Status "  开机自启动已注册: $TASK_NAME" -Color Green
        Write-Status "  每次开机自动启动全链路监控" -Color Green
    } catch {
        Write-Status "  注册失败: $_" -Color Red
        Write-Status "  尝试备用方案 (Startup 文件夹)..." -Color Yellow

        $shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\SuSuMonitor.lnk"
        $wshell = New-Object -ComObject WScript.Shell
        $shortcut = $wshell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-NoProfile -WindowStyle Hidden -File `"$scriptPath`""
        $shortcut.Save()
        Write-Status "  Startup 快捷方式已创建" -Color Green
    }
}

function Uninstall-AutoStart {
    Write-Status "===== 移除开机自启动 =====" -Color Cyan
    try {
        Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false -ErrorAction SilentlyContinue
        Write-Status "  计划任务已移除" -Color Yellow
    } catch { }
    $shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\SuSuMonitor.lnk"
    Remove-Item $shortcutPath -Force -ErrorAction SilentlyContinue
    Write-Status "  Startup 快捷方式已移除" -Color Yellow
    Write-Status "===== 已完成 =====" -Color Cyan
}

# ─── 主入口 ───

if ($Install) {
    Install-AutoStart
    Start-MonitorStack
} elseif ($Uninstall) {
    Stop-MonitorStack
    Uninstall-AutoStart
} elseif ($Status) {
    Get-MonitorStatus
} elseif ($Stop) {
    Stop-MonitorStack
} else {
    # 默认: 启动全链路
    Start-MonitorStack
}
