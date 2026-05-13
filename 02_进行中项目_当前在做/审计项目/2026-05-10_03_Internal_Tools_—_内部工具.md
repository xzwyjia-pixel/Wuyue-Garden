---
type: concept_map
category: internal_tools
---

# 03_Internal_Tools — 内部工具

自动化基础设施、MCP 服务、监控管道、规则引擎。

## 分层架构

```
┌─────────────────────────────────────────────────┐
│  MCP Layer                                      │
│  core/mcp_audit_server.py   ←  供 Claude 调用   │
├─────────────────────────────────────────────────┤
│  Engine Layer                                   │
│  core/audit_core.py         ←  核心审计逻辑     │
├─────────────────────────────────────────────────┤
│  Agent Layer                                    │
│  orchestrator/herald/simulator/final_agent_run  │
├─────────────────────────────────────────────────┤
│  Monitoring Layer                               │
│  platform_sentinel / trend_collector /          │
│  v_radar_scanner / vision_guard                 │
├─────────────────────────────────────────────────┤
│  Rules Layer                                    │
│  rules_evolver / rule_cleaner / find_models     │
│  rules.json / config.yaml                       │
├─────────────────────────────────────────────────┤
│  Feedback Layer                                 │
│  feedback_auto_collector / vocal_listener       │
├─────────────────────────────────────────────────┤
│  Analysis Layer                                 │
│  logic_adapter / obsidian_sync / google_drive   │
├─────────────────────────────────────────────────┤
│  Infrastructure                                 │
│  scripts/ (deploy/startup) / tests/             │
└─────────────────────────────────────────────────┘
```

## 关键依赖

- `core/audit_core.py` — 被 `mcp_audit_server`, `ai_refine_pro`, `content_exporter`, `final_agent_run`, `tests` 导入
- `rules.json`, `config.yaml` — 被全部模块读取
- `intelligence_raw.json` — 行业情报数据源

## 外部集成

- `scripts/start-claude-proxy.ps1` — GPTSAPI 中转
- `scripts/start-claude-direct.ps1` — DeepSeek 直连
- `docs/mcp-config.md` — MCP 配置说明

## 关联

- 为 `01_Content_Seeds` 提供合规审计能力
- 为 `02_Client_Solutions` 提供底层引擎
