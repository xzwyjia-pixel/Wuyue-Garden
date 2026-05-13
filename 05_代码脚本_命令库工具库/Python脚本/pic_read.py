"""
pic_read.py — 图片内容读取工具
用 PIL + EasyOCR 描述图片内容，替代 Read tool 的图片查看功能
"""
import sys, json, os
from pathlib import Path
from PIL import Image


def describe_image(path):
    """Basic image description without OCR (fast)"""
    img = Image.open(path)
    w, h = img.size
    mode = img.mode
    size_kb = os.path.getsize(path) / 1024

    desc = {
        "file": path,
        "format": img.format,
        "size": f"{w}x{h}",
        "mode": mode,
        "kb": f"{size_kb:.0f} KB",
    }

    # Color analysis
    if mode == "RGB":
        pixels = list(img.getdata())
        r_total = sum(p[0] for p in pixels)
        g_total = sum(p[1] for p in pixels)
        b_total = sum(p[2] for p in pixels)
        n = len(pixels)
        desc["avg_color"] = (round(r_total / n), round(g_total / n), round(b_total / n))

        # Brightness estimate
        brightness = (0.299 * r_total + 0.587 * g_total + 0.114 * b_total) / n
        desc["brightness"] = round(brightness, 1)

        # Dark/bright ratio
        dark = sum(1 for p in pixels if sum(p) / 3 < 50) / n * 100
        bright = sum(1 for p in pixels if sum(p) / 3 > 200) / n * 100
        desc["dark_area"] = f"{dark:.0f}%"
        desc["bright_area"] = f"{bright:.0f}%"

    return desc


def ocr_image(path, lang=None):
    """Full OCR with EasyOCR"""
    if lang is None:
        lang = ["ch_sim", "en"]

    try:
        import easyocr
        reader = easyocr.Reader(lang, gpu=False)
        results = reader.readtext(path)
        texts = []
        for bbox, text, conf in results:
            texts.append({
                "text": text,
                "confidence": round(conf, 3),
                "bbox": [[round(v) for v in pt] for pt in bbox],
            })
        return texts
    except ImportError:
        return [{"text": "[EasyOCR not installed]", "confidence": 0}]
    except Exception as e:
        return [{"text": f"[OCR error: {e}]", "confidence": 0}]


def ocr_fast(path):
    """Quick OCR - just extract text blocks"""
    texts = ocr_image(path)
    return [t["text"] for t in texts if t["confidence"] > 0.3]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python pic_read.py <图片路径> [--ocr]")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    desc = describe_image(path)
    print(f"\n=== {path} ===")
    print(f"格式: {desc['format']} | 尺寸: {desc['size']} | {desc['kb']}")
    if "avg_color" in desc:
        print(f"平均色: RGB{desc['avg_color']} | 亮度: {desc['brightness']}")
        print(f"暗部: {desc['dark_area']} | 亮部: {desc['bright_area']}")

    if "--ocr" in sys.argv:
        print(f"\n--- OCR 文字识别 ---")
        texts = ocr_image(path)
        for t in texts:
            conf = t["confidence"]
            if conf > 0.3:
                print(f"  [{conf:.0%}] {t['text']}")
