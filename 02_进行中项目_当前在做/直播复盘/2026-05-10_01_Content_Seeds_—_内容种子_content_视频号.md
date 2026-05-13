---
type: concept_map
category: content_seeds
---

# 01_Content_Seeds — 内容种子

可直接产出可发布内容的模块。

## 脚本 → 产出映射

| 脚本 | 产出类型 | 发布平台 |
|------|----------|----------|
| `content_pipeline/2026_policy_script.py` | 新规解读图文/脚本 | 公众号、抖音、视频号 |
| `content_pipeline/ai_refine_pro.py` | 合规改写文案 | 全平台 |
| `content_pipeline/content_exporter.py` | 剪映草稿说明 + 视频号 Excel | 视频号、剪映 |
| `data/publish_*.md` | 已发布内容存档 | 抖音/公众号/视频号 |
| `data/export_*.*` | 导出素材 | 剪映、视频号助手 |

## 工作流

```
2026_policy_script → raw script
         ↓
ai_refine_pro → compliance rewrite → re-audit → pass
         ↓
content_exporter → export formats (txt/xlsx)
         ↓
publish → data/publish_*.md (archive)
```

## 关联

- **上游**: `monitoring/trend_collector` 提供热词, `monitoring/v_radar_scanner` 提供正反案例
- **下游**: `analysis/matrix_publisher` 多端分发, `feedback/feedback_listener` 追踪效果
