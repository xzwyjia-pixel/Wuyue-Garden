"""
stream_health.py — 直播流健康检测 (黑屏/冻结/无声/爆音)
每10s检测, 写入 stream_health.jsonl
依赖: mss, opencv-python, numpy
"""
import json, time, os, sys, argparse
from pathlib import Path
from datetime import datetime
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
args = parser.parse_args()
TARGET = Path(args.target)
POLL_SECONDS = 10
OUT_FILE = TARGET / "stream_health.jsonl"

import mss
import cv2

sys.stdout.reconfigure(encoding="utf-8")

# Regions to monitor (双平台视频区域)
REGIONS = {
    "video_su": {"top": 478, "left": 0, "width": 640, "height": 360},   # 视频号
    "video_dy": {"top": 50, "left": 960, "width": 540, "height": 600},  # 抖音
}

last_frames = {}
last_audio_rms = {}
black_threshold = 5      # avg brightness < 5 = black screen
freeze_threshold = 0.98  # frame diff similarity > 98% across 3 checks = frozen
mute_threshold = 0.001   # audio RMS below = silent
clip_threshold = 0.98    # audio RMS above 0.98 = clipping/distortion
consecutive_freeze = {}  # track freeze duration
consecutive_black = {}
freeze_frames_needed = 3  # 3 consecutive checks = confirmed freeze (30s)

print(f"[stream] 直播流健康检测启动, 每{POLL_SECONDS}s巡检")

with mss.mss() as sct:
    while True:
        now = time.time()
        ts = datetime.now().strftime("%H:%M:%S")
        events = {"time": ts, "timestamp": now, "anomalies": []}

        for name, region in REGIONS.items():
            try:
                img = sct.grab(region)
                arr = np.array(img)
                gray = cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
            except Exception:
                continue

            avg_brightness = gray.mean()

            # Black screen detection
            if avg_brightness < black_threshold:
                consecutive_black[name] = consecutive_black.get(name, 0) + 1
                if consecutive_black[name] >= 2:
                    events["anomalies"].append(f"{name}:黑屏({int(avg_brightness)}/{consecutive_black[name]}次)")
            else:
                consecutive_black[name] = 0

            # Freeze detection via frame diff
            if name in last_frames:
                diff = cv2.absdiff(gray, last_frames[name])
                similarity = 1.0 - (diff.mean() / 255.0)
                if similarity > freeze_threshold:
                    consecutive_freeze[name] = consecutive_freeze.get(name, 0) + 1
                    if consecutive_freeze[name] >= freeze_frames_needed:
                        duration = consecutive_freeze[name] * POLL_SECONDS
                        events["anomalies"].append(f"{name}:画面冻结({duration}s)")
                else:
                    if consecutive_freeze.get(name, 0) >= freeze_frames_needed:
                        duration = consecutive_freeze[name] * POLL_SECONDS
                        events["anomalies"].append(f"{name}:冻结恢复(持续{duration}s)")
                    consecutive_freeze[name] = 0
                events[f"{name}_similarity"] = round(similarity, 3)
            else:
                consecutive_freeze[name] = 0

            last_frames[name] = gray
            events[f"{name}_brightness"] = round(float(avg_brightness), 1)

        # Audio anomaly from latest audio chunk
        audio_dir = TARGET / "audio"
        if audio_dir.is_dir():
            wavs = sorted(audio_dir.glob("*.wav"))
            if wavs:
                latest = wavs[-1]
                try:
                    import wave
                    with wave.open(str(latest), "rb") as wf:
                        frames = wf.readframes(min(wf.getnframes(), 4800))  # first 0.1s
                    if frames and len(frames) > 44:
                        audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)
                        rms = np.sqrt(np.mean(audio_data ** 2)) / 32768.0
                        events["audio_rms"] = round(float(rms), 4)
                        # Audio clipping
                        peaks = np.abs(audio_data).max() / 32768.0
                        events["audio_peak"] = round(float(peaks), 4)
                        if peaks > clip_threshold:
                            events["anomalies"].append(f"音频爆音(peak={peaks:.2f})")
                        elif rms < mute_threshold:
                            if last_audio_rms.get("last_rms", 1) > mute_threshold * 10:
                                events["anomalies"].append(f"音频无声(rms={rms:.4f})")
                        last_audio_rms["last_rms"] = rms
                except Exception:
                    pass

        # Log
        if events["anomalies"]:
            for a in events["anomalies"]:
                print(f"[stream] [{ts}] ⚠ {a}")

        with open(OUT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(events, ensure_ascii=False) + "\n")

        time.sleep(POLL_SECONDS)
