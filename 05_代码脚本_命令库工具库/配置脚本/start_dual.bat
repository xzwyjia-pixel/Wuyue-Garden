@echo off
title 清晨烟火小厨 · 全维度监控 v3.0
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d E:\MyCodeProjects\02-审计工具

echo ========================================
echo   清晨烟火小厨 · 全维度监控 v3.0
echo   7类实时监控 + 直播后自动复盘
echo ========================================
echo.

:: 1) 音频捕获
echo [1/6] 音频捕获 v2 (VAD+AGC+16kHz)...
start /B python audio_capture.py --chunk 15 --vad 0.003 --agc 0.15
timeout /t 2 >nul

:: 2) Whisper STT (CUDA)
echo [2/6] Whisper语音转文字 (CUDA加速)...
start /B python whisper_stt.py
timeout /t 2 >nul

:: 3) 双平台监控 (OCR+人脸+Triage)
echo [3/6] 双平台屏幕监控(视频号+抖音)...
start /B python monitor_dual.py --auto

:: 4) V3监控集成 (情感+合规+平台同步)
echo [4/6] V3监控集成引擎...
start /B python monitor_v3.py

:: 5) 技术环境监控
echo [5/6] 技术环境监控(CPU/GPU/网络)...
start /B python system_monitor.py

:: 6) 流健康检测
echo [6/6] 直播流健康检测(黑屏/冻结/音频异常)...
start /B python stream_health.py

echo.
echo ========================================
echo  全部启动完成!
echo.
echo  覆盖监控类别:
echo    1. 基础状态   2. 流量人气
echo    3. 弹幕互动   4. 商品转化
echo    5. 合规内容   6. 平台一致性
echo    7. 技术环境
echo.
echo  直播结束后:
echo    python post_stream_report.py
echo.
echo  停止方法: taskkill /f /im python.exe
echo ========================================
pause
