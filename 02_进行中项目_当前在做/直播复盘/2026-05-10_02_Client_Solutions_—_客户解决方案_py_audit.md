---
type: concept_map
category: client_solutions
---

# 02_Client_Solutions — 客户解决方案

可直接交付给客户的产品级模块。

## 交付清单

| 模块 | 解决什么问题 | 目标客户 | 定价建议 |
|------|-------------|----------|----------|
| `core/brand_audit_engine.py` | 品牌词合规审计（避免品牌侵权） | 品牌方、广告公司 | 按次/包月 |
| `rules_engine/batch_audit_pro.py` | 批量文案风险扫描 | 内容工厂、MCN | 按条数 |
| `monitoring/vision_guard.py` | 视频帧视觉内容检测 | 电商直播、短视频团队 | 按视频 |
| `analysis/deep_insight_agent.py` | 行业深度洞察报告 | 市场部、战略团队 | 按报告 |
| `analysis/matrix_distiller.py` | 多平台内容变调适配 | 全域运营团队 | 包月 |
| `analysis/matrix_publisher.py` | 矩阵账号分发 | MCN、多账号运营 | 按账号 |
| `feedback/feedback_listener.py` | 发布后效果追踪 & 策略优化 | 数据驱动运营 | 包月 |

## 工作流

```
brand_audit_engine / batch_audit_pro → 风险筛查
         ↓
deep_insight_agent → 行业洞察
         ↓
matrix_distiller → 多端变调
         ↓
matrix_publisher → 分发
         ↓
feedback_listener → 效果追踪 → 优化循环
```

## 关联

- 依赖 `core/audit_core.py` 作为底层引擎
- 产出可二次加工为 `01_Content_Seeds` 内容素材
