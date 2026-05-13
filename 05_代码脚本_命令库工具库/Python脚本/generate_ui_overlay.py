"""
generate_ui_overlay.py — UI遮挡校准参考图
生成带 DY/WCH 遮罩的半透明参考图, 供运营人员对比产品位置
"""
import cv2, numpy as np
from pathlib import Path

W, H = 1080, 1920  # 9:16 竖屏直播标准
OUT = Path("case_assets/Calibration")
OUT.mkdir(parents=True, exist_ok=True)

# 创建RGB背景
img = np.ones((H, W, 3), dtype=np.uint8) * 240

# ── 遮罩定义（相对坐标 → 像素） ──────────────────────

overlay = img.copy()

# DY_Mask 底部30%评论区
dy_bottom = np.zeros((H, W), dtype=np.uint8)
dy_bottom[int(H*0.70):H, :] = 1
# DY_Mask 右侧20%
dy_right = np.zeros((H, W), dtype=np.uint8)
dy_right[:, int(W*0.80):W] = 1
dy_mask = np.maximum(dy_bottom, dy_right)
overlay[dy_mask == 1] = (50, 50, 200)  # 红色调

# WCH_Mask 右下方40%
wch_mask = np.zeros((H, W), dtype=np.uint8)
wch_mask[int(H*0.60):H, int(W*0.60):W] = 1
# 排除已在 DY 中的像素（避免颜色冲突）
wch_only = wch_mask & (dy_mask == 0)
overlay[wch_only == 1] = (200, 100, 50)  # 橙色调

# Ultimate_Safe_Zone = 不在任何mask中的区域 → 绿色
safe = np.ones((H, W), dtype=np.uint8)
safe[dy_mask == 1] = 0
safe[wch_mask == 1] = 0
overlay[safe == 1] = (50, 200, 50)  # 绿色

# ── 混合半透明 ──────────────────────────────────
alpha = 0.35
result = cv2.addWeighted(img, 1 - alpha, overlay, alpha, 0)

# ── 标注文字 ────────────────────────────────────
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(result, "DY Mask (评论区+右侧栏)", (30, 60), font, 0.7, (0, 0, 180), 2)
cv2.putText(result, "WCH Mask (右下礼物区)", (30, 100), font, 0.7, (180, 80, 0), 2)
cv2.putText(result, "Ultimate Safe Zone", (30, 140), font, 0.7, (0, 140, 0), 2)
cv2.putText(result, "产品视觉重心应落在绿色区域", (30, 180), font, 0.6, (80, 80, 80), 1)

# 虚线标记safe中心
cv2.rectangle(result, (int(W*0.25), int(H*0.25)), (int(W*0.60), int(H*0.55)), (0, 200, 0), 2)

path = str(OUT / "UI_Overlay_Reference.png")
cv2.imwrite(path, result)
print(f"Calibration reference saved: {path}")
print(f"  DY_Mask: 底部30%评论区 + 右侧20%头像栏")
print(f"  WCH_Mask: 右下40%点赞/礼物弹窗")
print(f"  Safe_Zone: 画面中心偏上 25%-55% y, 20%-60% x")
