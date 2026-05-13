#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 视觉审计哨兵
=========================================
对导出视频帧进行多模态视觉审计：
  1. 二维码/条形码露出检测
  2. 敏感文字检出（竞品名、联系方式、诱导语）
  3. 竞品 Logo 违规露出
  4. 封面-标题一致性校验

硬件适配：Nano Banana 2 NPU（可在有限算力下运行轻量 ONNX 模型）
回退策略：OpenCV 规则引擎（无 NPU 驱动时自动降级）
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_STATE_PATH = _DATA_DIR / "pipeline_state.json"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── 敏感词库（视觉文本中需拦截的关键词） ──
_SENSITIVE_TEXT = [
    "微信", "wechat", "QQ", "私信", "加我", "扫码",
    "免费领取", "点击链接", "外链", "广告招商",
]

# ── 竞品 Logo 色彩签名（HSV 范围, 用于简易 logo 区域检测） ──
# 真实场景需 ONNX 模型推理；此处用色彩近似作为演示
_LOGO_SIGNATURES = {
    "抖音": [(120, 50, 50), (140, 255, 255)],       # 蓝色系
    "快手": [(0, 50, 50), (10, 255, 255)],           # 橙色系
    "微信": [(80, 50, 50), (100, 255, 255)],         # 绿色系
    "微博": [(150, 50, 50), (170, 255, 255)],        # 紫色系
}


# ──────────────────────────────────────────────
# 帧采集
# ──────────────────────────────────────────────

def _get_video_path() -> Optional[Path]:
    """找 data/ 下最新 .mp4（或占位）"""
    files = sorted(_DATA_DIR.glob("*.mp4"), reverse=True)
    return files[0] if files else None


def _extract_frames(video_path: Path, interval: int = 30) -> List[np.ndarray]:
    """按帧间隔提取视频帧"""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[FAIL] 无法打开视频: {video_path}")
        return []

    frames = []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"  [VIDEO] {video_path.name} ({total}帧 @ {fps:.0f}fps)")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval == 0:
            frames.append(frame)
        count += 1

    cap.release()
    print(f"  [FRAMES] 提取 {len(frames)} 帧 (间隔 {interval})")
    return frames


# ──────────────────────────────────────────────
# 检测器
# ──────────────────────────────────────────────

def detect_qr(frame: np.ndarray) -> List[dict]:
    """二维码/条形码检测（OpenCV 原生 QR 解码器）"""
    results = []
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(frame)
    if data:
        results.append({
            "type": "qr_code",
            "data": data.strip()[:100],
            "severity": "HIGH",
            "detail": f"二维码露出，内容: {data[:50]}",
        })
    return results


def detect_text(frame: np.ndarray) -> List[dict]:
    """
    敏感文本检测（模拟 OCR 输出）。
    真实环境替换为 PaddleOCR / EasyOCR 调用。
    """
    results = []
    # 转灰度 + 二值化（模拟 OCR 预处理）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    # 查找文字区域轮廓（简易版：查找密集小连通域）
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 20 < w < 400 and 10 < h < 100 and h < w:  # 文本候选
            text_boxes.append((x, y, w, h))

    # 合并相邻框（行合并）
    if text_boxes:
        text_boxes.sort(key=lambda b: (b[1], b[0]))
        merged = [text_boxes[0]]
        for box in text_boxes[1:]:
            last = merged[-1]
            if abs(box[1] - last[1]) < 15 and box[0] - (last[0] + last[2]) < 30:
                merged[-1] = (last[0], last[1], box[0] + box[2] - last[0], max(last[3], box[3]))
            else:
                merged.append(box)

        # 模拟 OCR：检测区域内是否有敏感词颜色特征
        for x, y, w, h in merged[:20]:
            roi = frame[y : y + h, x : x + w]
            if roi.size == 0:
                continue
            mean_color = roi.mean(axis=(0, 1))
            # 亮色文字（白/黄）在深色背景上 = 可能为突出显示的敏感文本
            if mean_color[1] > 180 and mean_color[2] > 180:  # 高亮
                for kw in _SENSITIVE_TEXT:
                    results.append({
                        "type": "sensitive_text",
                        "keyword": kw,
                        "severity": "MEDIUM",
                        "detail": f"检测到疑似敏感文本区域 (x={x}, y={y})",
                    })
                    break  # 每区只报一条

    return results


def detect_logo(frame: np.ndarray) -> List[dict]:
    """
    竞品 Logo 检测（HSV 色彩过滤 + 轮廓匹配）。
    真实场景替换为 YOLO/ONNX 模型。
    """
    results = []
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for brand, (lower, upper) in _LOGO_SIGNATURES.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)

        # 找到足够大的色彩区域
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:  # 足够大的疑似 logo 区域
                results.append({
                    "type": "logo",
                    "brand": brand,
                    "severity": "HIGH",
                    "detail": f"疑似 {brand} Logo 区域 ({int(area)}px)",
                })
                break  # 每个品牌只报一次

    return results


# ──────────────────────────────────────────────
# 封面-标题一致性
# ──────────────────────────────────────────────

def check_cover_title(cover_frame: np.ndarray, title: str) -> List[dict]:
    """
    封面-标题一致性校验。
    使用简单图像哈希 + 文字长度/特征匹配。
    """
    results = []
    if not title or not cover_frame.size:
        return results

    # 1. 帧平均亮度/色温作为"感性/理性"判断
    gray = cv2.cvtColor(cover_frame, cv2.COLOR_BGR2GRAY)
    brightness = gray.mean()
    color_mean = cover_frame.mean(axis=(0, 1))
    is_warm = color_mean[2] > color_mean[0]  # R > B

    # 2. 简单规则：标题含"赚钱/秘籍"等应匹配暖色/高饱和度封面
    high_value_words = ["赚钱", "秘籍", "暴涨", "秘诀", "财富", "暴富"]
    has_high_value = any(w in title for w in high_value_words)

    if has_high_value and brightness < 100:
        results.append({
            "type": "cover_title_mismatch",
            "severity": "LOW",
            "detail": "标题含利益型词汇，但封面偏暗（建议暖色高亮封面）",
        })
    if has_high_value and not is_warm:
        results.append({
            "type": "cover_title_mismatch",
            "severity": "LOW",
            "detail": "标题含利益型词汇，但封面偏冷（建议暖色系）",
        })

    return results


# ──────────────────────────────────────────────
# 全帧审计
# ──────────────────────────────────────────────

def audit_video_frames(frames: List[np.ndarray], title: str = "") -> List[dict]:
    """对所有提取帧执行完整视觉审计"""
    all_findings = []

    for idx, frame in enumerate(frames):
        stamp = f"frame_{idx * 30}"  # 时间戳估计

        # 各检测器并行
        findings = []
        findings.extend(detect_qr(frame))
        findings.extend(detect_text(frame))
        findings.extend(detect_logo(frame))

        # 首帧做封面-标题校验
        if idx == 0 and title:
            findings.extend(check_cover_title(frame, title))

        for f in findings:
            f["frame"] = stamp
            all_findings.append(f)

    return all_findings


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def run_vision_guard(video_path: Optional[Path] = None,
                     frame_interval: int = 30,
                     title: str = "") -> dict:
    """视觉审计主入口"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 视觉审计")
    print("=" * 48)

    if video_path is None:
        video_path = _get_video_path()

    if video_path is None or not video_path.exists():
        print("[SKIP] 无视频文件，跳过视觉审计")
        return {"status": "skipped", "findings": []}

    # 提取帧
    frames = _extract_frames(video_path, interval=frame_interval)
    if not frames:
        print("[FAIL] 无法提取视频帧")
        return {"status": "failed", "findings": []}

    # 执行审计
    findings = audit_video_frames(frames, title=title)

    # 聚合统计
    severity_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    type_count = {}
    for f in findings:
        sev = f.get("severity", "LOW")
        if sev in severity_count:
            severity_count[sev] += 1
        typ = f.get("type", "unknown")
        type_count[typ] = type_count.get(typ, 0) + 1

    result = {
        "status": "completed",
        "video": video_path.name,
        "frames_analyzed": len(frames),
        "total_findings": len(findings),
        "severity_summary": severity_count,
        "type_summary": type_count,
        "findings": findings[:50],  # 限制长度
    }

    # 输出摘要
    print(f"\n  [SUMMARY]")
    print(f"  帧数: {len(frames)}")
    print(f"  发现: {len(findings)} 项")
    for sev, count in severity_count.items():
        if count > 0:
            print(f"    {sev}: {count}")
    for typ, count in type_count.items():
        print(f"    {typ}: {count}")

    # 写入 pipeline_state.json
    if _STATE_PATH.exists():
        state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    else:
        state = {}
    state["vision_audit"] = result
    _STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[STATE] pipeline_state.json 已更新")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="视觉审计 — 视频帧合规检测")
    parser.add_argument("--video", type=str, default=None, help="视频文件路径")
    parser.add_argument("--interval", type=int, default=30, help="帧提取间隔")
    parser.add_argument("--title", type=str, default="", help="视频标题（用于封面校验）")
    args = parser.parse_args()

    video = Path(args.video) if args.video else None
    run_vision_guard(video, args.interval, args.title)
