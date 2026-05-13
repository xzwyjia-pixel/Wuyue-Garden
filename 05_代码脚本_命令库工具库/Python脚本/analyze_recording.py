"""
analyze_recording.py — Deep re-analysis of recorded livestream video
Extracts ~176 frames (30s intervals), runs full visual pipeline + new analysis
"""
import cv2
import numpy as np
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

VIDEO_PATH = r"E:\Program Files (x86)\Videos\直播录制\2026-05-11 07-06-22.mp4"
OUT_DIR = Path(r"E:\MyCodeProjects\04-宝妈直播诊断系统\苏苏在浙里")
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

SAMPLE_INTERVAL = 30  # seconds
face_cascade = cv2.CascadeClassifier(HAAR_PATH)

def triage_frame(rgb):
    """Full visual analysis on one frame"""
    gray = np.mean(rgb, axis=2).astype(np.uint8)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]

    hf, wf = rgb.shape[:2]

    # Global metrics
    brightness = float(np.mean(v))
    contrast = float(np.std(gray))
    warm = float(((h < 25) | (h > 160)).mean())
    green = float(((h > 35) & (h < 85)).mean())
    detail = float(cv2.Laplacian(gray, cv2.CV_64F).std())

    # Color entropy
    hist = cv2.calcHist([h.astype(np.uint8)], [0], None, [180], [0, 180])
    hist_norm = hist / hist.sum()
    entropy = float(-np.sum(hist_norm * np.log2(hist_norm + 1e-10)))

    # Food region (bottom center)
    food = hsv[int(hf*0.70):int(hf*0.95), int(wf*0.20):int(wf*0.80)]
    food_sat = float(food[:,:,1].mean()) if food.size > 0 else 0

    # Food detail (texture complexity in food region)
    food_gray = gray[int(hf*0.70):int(hf*0.95), int(wf*0.20):int(wf*0.80)]
    food_detail = float(cv2.Laplacian(food_gray, cv2.CV_64F).std()) if food_gray.size > 0 else 0

    # === REGION ANALYSIS ===
    left = v[:, :wf//3]
    center = v[:, wf//3:2*wf//3]
    right = v[:, 2*wf//3:]

    left_brightness = float(left.mean())
    center_brightness = float(center.mean())
    right_brightness = float(right.mean())

    # Top-left dark corner
    tl = v[:hf//4, :wf//4]
    tl_brightness = float(tl.mean()) if tl.size > 0 else 0

    # === IMPROVED SCORING (fixed from live version) ===
    score_a = 0
    if brightness > 60: score_a += 10
    if contrast > 35: score_a += 15
    if warm > 0.15: score_a += 15
    elif warm > 0.10: score_a += 8
    if green < 0.40: score_a += 10
    if detail > 30: score_a += 15
    if entropy > 4.5: score_a += 10
    elif entropy > 3.0: score_a += 5
    if food_sat > 50: score_a += 15
    elif food_sat > 30: score_a += 8
    elif food_sat > 20: score_a += 3
    score_a = min(score_a, 85)

    score_s = 0
    if contrast <= 35: score_s += 10
    if warm <= 0.15: score_s += 10
    if green > 0.40: score_s += 15
    if detail <= 30: score_s += 10
    if entropy <= 4.5: score_s += 10
    score_s = min(score_s, 100)

    # === FACE DETECTION ===
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    face_count = len(faces)
    face_brightness = []
    face_area_pct = 0
    for (fx, fy, fw, fh) in faces:
        face_roi = v[fy:fy+fh, fx:fx+fw]
        face_brightness.append(float(face_roi.mean()))
        face_area_pct += (fw * fh) / (hf * wf)

    avg_face_brightness = float(np.mean(face_brightness)) if face_brightness else 0

    # Face left/right asymmetry
    face_lr_asymmetry = 0
    if len(faces) == 1:
        f = faces[0]
        fx, fy, fw, fh = f
        left_half = v[fy:fy+fh, fx:fx+fw//2]
        right_half = v[fy:fy+fh, fx+fw//2:fx+fw]
        if left_half.size > 0 and right_half.size > 0:
            face_lr_asymmetry = float(right_half.mean() - left_half.mean())

    return {
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "warm_ratio": round(warm, 4),
        "green_ratio": round(green, 4),
        "detail": round(detail, 1),
        "color_entropy": round(entropy, 2),
        "food_saturation": round(food_sat, 1),
        "food_detail": round(food_detail, 1),
        "score_authentic": score_a,
        "score_staged": score_s,
        "diff": score_a - score_s,
        "region_brightness": {
            "left": round(left_brightness, 1),
            "center": round(center_brightness, 1),
            "right": round(right_brightness, 1),
            "top_left": round(tl_brightness, 1),
            "left_right_diff": round(right_brightness - left_brightness, 1),
        },
        "face": {
            "count": face_count,
            "avg_brightness": round(avg_face_brightness, 1),
            "area_pct": round(face_area_pct * 100, 1),
            "lr_asymmetry": round(face_lr_asymmetry, 1),
        }
    }

def analyze_motion(frames_ts):
    """Motion analysis between consecutive frames"""
    motions = []
    for i in range(1, len(frames_ts)):
        prev = frames_ts[i-1]["gray"]
        curr = frames_ts[i]["gray"]
        diff = cv2.absdiff(prev, curr)
        motion = float(diff.mean())
        motions.append({
            "time": frames_ts[i]["time_str"],
            "motion_score": round(motion, 2),
        })
    return motions

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_sec = total_frames / fps

    print(f"Video: {total_frames}f @ {fps}fps = {total_sec/60:.1f}min")

    step_frames = int(fps * SAMPLE_INTERVAL)
    samples = []
    frames_ts = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step_frames == 0:
            ts_sec = frame_idx / fps
            ts_min = int(ts_sec // 60)
            ts_sec_remain = int(ts_sec % 60)
            time_str = f"{ts_min:02d}:{ts_sec_remain:02d}"

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            result = triage_frame(rgb)
            result["timestamp_sec"] = round(ts_sec, 1)
            result["time_str"] = time_str

            samples.append(result)
            frames_ts.append({"gray": gray, "time_str": time_str, "ts_sec": ts_sec})

            # Progress
            pct = frame_idx / total_frames * 100
            faces = result["face"]["count"]
            sys.stdout.write(f"\r  [{pct:5.1f}%] t={time_str} b={result['brightness']} w={result['warm_ratio']*100:.1f}% f_sat={result['food_saturation']} faces={faces}    ")
            sys.stdout.flush()

        frame_idx += 1

    cap.release()
    print(f"\n\nSampled {len(samples)} frames @ every {SAMPLE_INTERVAL}s")

    # Motion analysis
    motions = analyze_motion(frames_ts)

    # === AGGREGATE STATS ===
    b_vals = [s["brightness"] for s in samples]
    w_vals = [s["warm_ratio"] for s in samples]
    f_vals = [s["food_saturation"] for s in samples]
    e_vals = [s["color_entropy"] for s in samples]
    d_vals = [s["detail"] for s in samples]
    fb_vals = [s["face"]["avg_brightness"] for s in samples if s["face"]["count"] > 0]

    non_anomaly = [s for s in samples if s["brightness"] < 100]
    anom = [s for s in samples if s["brightness"] >= 100]

    report = {
        "video": {
            "path": VIDEO_PATH,
            "duration_min": round(total_sec / 60, 1),
            "resolution": "1280x720",
            "fps": fps,
            "samples": len(samples),
            "sample_interval_sec": SAMPLE_INTERVAL,
        },
        "summary": {
            "brightness_avg": round(float(np.mean(b_vals)), 1),
            "brightness_min": round(float(np.min(b_vals)), 1),
            "brightness_max": round(float(np.max(b_vals)), 1),
            "brightness_std": round(float(np.std(b_vals)), 1),
            "warm_ratio_avg": round(float(np.mean(w_vals)) * 100, 1),
            "warm_ratio_min": round(float(np.min(w_vals)) * 100, 1),
            "warm_ratio_max": round(float(np.max(w_vals)) * 100, 1),
            "food_sat_avg": round(float(np.mean(f_vals)), 1),
            "food_sat_min": round(float(np.min(f_vals)), 1),
            "food_sat_max": round(float(np.max(f_vals)), 1),
            "color_entropy_avg": round(float(np.mean(e_vals)), 2),
            "detail_avg": round(float(np.mean(d_vals)), 1),
            "face_brightness_avg": round(float(np.mean(fb_vals)), 1) if fb_vals else 0,
            "face_detection_rate": round(len(fb_vals) / len(samples) * 100, 1),
            "authentic_score_avg": round(float(np.mean([s["score_authentic"] for s in non_anomaly])), 1) if non_anomaly else 0,
        },
        "region_analysis": {
            "left_brightness_avg": round(float(np.mean([s["region_brightness"]["left"] for s in non_anomaly])), 1),
            "center_brightness_avg": round(float(np.mean([s["region_brightness"]["center"] for s in non_anomaly])), 1),
            "right_brightness_avg": round(float(np.mean([s["region_brightness"]["right"] for s in non_anomaly])), 1),
            "left_right_diff_avg": round(float(np.mean([s["region_brightness"]["left_right_diff"] for s in non_anomaly])), 1),
            "top_left_corner_avg": round(float(np.mean([s["region_brightness"]["top_left"] for s in non_anomaly])), 1),
        },
        "face_analysis": {
            "detection_rate_pct": round(len(fb_vals) / len(samples) * 100, 1),
            "avg_brightness": round(float(np.mean(fb_vals)), 1) if fb_vals else 0,
            "asymmetry_avg": round(float(np.mean([s["face"]["lr_asymmetry"] for s in samples if s["face"]["count"] > 0])), 1),
            "avg_area_pct": round(float(np.mean([s["face"]["area_pct"] for s in samples if s["face"]["count"] > 0])), 1),
        },
        "anomaly_events": [
            {
                "time": s["time_str"],
                "brightness": s["brightness"],
                "warm_ratio": s["warm_ratio"],
                "detail": s["detail"],
            }
            for s in anom
        ],
        "motion": {
            "avg_motion_score": round(float(np.mean([m["motion_score"] for m in motions])), 2),
            "max_motion": round(float(np.max([m["motion_score"] for m in motions])), 2),
        },
        "samples": samples,
        "motion_data": motions,
    }

    out_path = OUT_DIR / "video_analysis_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nReport saved: {out_path}")
    print(f"\n=== QUICK STATS ===")
    print(f"Avg brightness: {report['summary']['brightness_avg']}/255")
    print(f"Avg warm ratio: {report['summary']['warm_ratio_avg']}%")
    print(f"Avg food sat:   {report['summary']['food_sat_avg']}/255")
    print(f"Color entropy:  {report['summary']['color_entropy_avg']}")
    print(f"Face detect:    {report['face_analysis']['detection_rate_pct']}% of frames")
    print(f"Left region:    {report['region_analysis']['left_brightness_avg']}")
    print(f"Center region:  {report['region_analysis']['center_brightness_avg']}")
    print(f"Right region:   {report['region_analysis']['right_brightness_avg']}")
    print(f"Left-Right diff:{report['region_analysis']['left_right_diff_avg']}")
    print(f"Anomalies:      {len(anom)} frames (brightness > 100)")

    return report

if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"\nElapsed: {time.time()-t0:.0f}s")
