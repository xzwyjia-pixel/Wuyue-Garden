# Task Progress: 规则甄查 v2.0 全方位润色与架构升级

## Todo List

### Task 1: 品牌逻辑升级 (The Soul)
- [x] Analyze existing brand positioning
- [x] Design "红绿灯双向导航" brand upgrade plan
- [x] Update rules.json with dual-direction (红灯避险 + 绿灯起量) rules
- [x] Update CLAUDE.md with v2.0 brand identity

### Task 2: 硬件性能适配 (The Engine)
- [x] Analyze P15V hardware specs requirements
- [x] Create async crawler with asyncio + aiohttp for P15V multi-core optimization
- [x] Implement SQLite cache with resume-from-breakpoint
- [x] Configure E:/MyCodeProjects/data/ storage path with buffer+flush IO strategy

### Task 3: 工程化开发 (The Action)
- [x] Rewrite audit_core.py with dual-direction audit (risk + incentive + optimization)
- [x] Rewrite mcp_audit_server.py with v2.0 protocol (新增 tools: audit_dual, policy_check)
- [x] Create dual-direction crawler script (负向受罚 + 正向获益)
- [x] Add "政策契合度" (policy fitness) evaluation function

### Task 4: 内容产出与存档 (The Output)
- [x] Draft 2026 platform policy interpretation script (案例回溯→政策深挖→正向对比→避坑起量)
- [x] Update README / CLAUDE.md to v2.0 (Dual-Direction Navigation)
- [x] Update MCP config documentation

### Task 5: 目录重构扫尾 (100% 完成)
- [x] 目录分层方案设计 (01-Production / 02-SubProjects / 03-Archive)
- [x] 27 个 .py 文件移入子目录 (core/agents/rules_engine/content_pipeline/monitoring/feedback/analysis)
- [x] 修复 23 个文件中的 import 路径 + _BASE_DIR + 硬编码路径
- [x] 添加 8 个 __init__.py + 1 个 conftest.py
- [x] 移动子项目 + 归档旧版代码
- [x] 编写 5 个 README.md
- [x] 编写 Index.md (Obsidian 兼容)
- [x] 清理缓存 (pyc/pycache/stray dirs)
- [x] 验证: 9/9 测试全部通过
- [x] 更新 CLAUDE.md 路径描述
