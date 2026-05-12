---
created: 2026-05-10
updated: 2026-05-10
description: MyCodeProjects 中央控制台 — MCP 入口 / 系统索引 / 会话锚点
type: dashboard
---

# 🎛 甄查工作站 · 中央控制台

> MCP 枢纽。Claude 启动时读取此文件，自动加载关联系统上下文。

---

## 📂 项目索引

| # | 目录 | 职责 | 快速命令 |
|---|------|------|----------|
| 01 | [规则引擎](01-规则引擎/) | 审计规则 / Calibration / 弹幕检测 | `python 01-规则引擎/danmaku_auditor.py` |
| 02 | [审计工具](02-审计工具/) | 监控引擎 / 报告生成 / 坐标验证 | `python 02-审计工具/start_audit.py` |
| 03 | [规则甄查系统](03-规则甄查系统/) | 规则甄查 v2.0 / MCP 审计 / 规则引擎 | `cd 03-规则甄查系统 && python core/audit_core.py` |
| 04 | [宝妈直播诊断系统](04-宝妈直播诊断系统/) | 苏苏在浙里 / 清晨烟火小厨 / 宝妈直播诊断 | — |
| 05 | [参考案例](05-参考案例/) | 凡姐案例 / 小桃案例 / 审计参考数据 | — |
| 06 | [存档中心](06-存档中心/) | 旧版工具 / 子项目 / logs / temp_frames | — |
| 07 | [工业私有云系统](07-工业私有云系统/) | 石化盈科 / 天津水利 / 工业私有云方案 | — |
| 08 | [RFID专用设备](08-RFID专用设备/) | RFID 读写器 / 标签 / 专用设备方案 | — |

---

## 🧠 MCP 链接

### Obsidian Vault
```
Vault: E:/Obsidian/
API:   http://127.0.0.1:27123
Key:   (配置于 obsidian_api_reference.md)
```

### MCP 服务器配置
- 项目级: `03-规则甄查系统/core/obsidian_mcp_server.py`

---

## 🗨 Claude 历史会话

| 会话 | 日期 | 链接 |
|------|------|------|
| _（在此粘贴 Claude 聊天链接）_ | — | — |

---

## ⚡ 快速启动

```bash
# 完整双向导航审计
cd 03-规则甄查系统
python core/audit_core.py "待审计文案"

# MCP 审计服务器 (供 Claude Desktop)
python core/mcp_audit_server.py

# 红绿灯双向雷达扫描
python monitoring/v_radar_scanner.py

# 启动直播监控
cd 02-审计工具 && python start_audit.py
```

---

## 🔄 自检参考

- `06-存档中心/claude_auto_report_*.json` — 上次整理报告
- `06-存档中心/_claude_log_*.txt` — 操作日志
