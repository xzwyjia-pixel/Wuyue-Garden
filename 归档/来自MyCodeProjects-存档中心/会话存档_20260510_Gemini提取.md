# 会话存档: Gemini 对话提取 + 重分类 + 批量改名准备

日期: 2026-05-10 (已存档, 继续会话用)

## 已完成

### 目录重组
- 04-凡姐案例 + 05-小桃案例 → 合并为 `05-参考案例`
- 新建 `04-宝妈直播诊断系统`
- `03-规则甄查系统` 独立
- 新建 `07-工业私有云系统` + `08-RFID专用设备`

### Gemini 对话导出 (Takeout)
- 2616 条活动记录 → 2245 条有效对话
- 脚本: `02-审计工具/process_gemini_takeout.py`
- 同步到 Obsidian: `E:/Obsidian/Gemini对话/`

### Gemini API 逆向
- 改名 RPC: `MaZiqc` (POST batchexecute)
- 参数: `[20, "<conversation_token>", "<new_title>"]`
- 认证: `at=<auth_token>` 在 POST body
- 捕获数据: `02-审计工具/gemini_api_capture.json`
- 抓包脚本: `02-审计工具/gemini_api_capture.py`

### 网络优化
- Clash for Windows v0.18.1, 端口 7890
- Chrome CDP 启动脚本: `02-审计工具/start_chrome_cdp.ps1`

### 分类系统重构 (本会话新增)
**旧 10 分类 → 新 8 分类 (按内容领域):**

| 前缀 | 分类 | 条数 | 说明 |
|------|------|------|------|
| [AUD] | 审计合规 | 355 | 规则甄查/违禁词/广告法/平台风控 |
| [LIV] | 直播运营 | 123 | 小桃/凡姐/苏苏/通用策略 |
| [DEV] | 技术开发 | 387 | Python/脚本/API/调试 |
| [CPY] | 文案创意 | 524 | 短视频脚本/Prompt/标题/故事 |
| [BRD] | 品牌设计 | 168 | LOGO/VI/配色/命名 |
| [OPS] | 系统运维 | 324 | PowerShell/网络/环境/Obsidian |
| [CON] | 方案咨询 | 341 | 教育/商业/建议/决策 |
| [DAT] | 数据报表 | 23 | SQL/报表/分析 |

**层级目录结构 (≤30 条/目录):**
- 一级: 8 分类
- 二级: 话题子分类 (topic-based keywords)
- 三级: 若 >30 条, 按月拆分 (YYYY-MM)
- 四级(必要时): 按周拆分 (W1-W5)
- 共 351 个目录
- 分类器升级: 加权评分, 标题 3x 权重, 内容辅助

**更新文件:**
- `process_gemini_takeout.py` — 新 CATEGORY_RULES + weighted classify()
- `gemini_reclassify.py` — v3 重分类 + 子目录层级
- `gemini_batch_rename.py` — PREFIX_MAP 更新为 8 分类
- 输出: `gemini_exported/reorganized_v3/` (2245 条)
- Obsidian 已同步: `E:/Obsidian/Gemini对话/`

### 临时脚本清理
已删: `gemini_discover.py`, `gemini_extract.py`, `gemini_sidebar_dump.py`
保留: `gemini_prefix_rename.py` (记录)
新建: `gemini_discover_rpc.py`, `gemini_batch_rename.py`, `gemini_reclassify.py`

## 待办 (下次会话继续)

### Gemini 网页端改名 (核心)
需要先发现对话列表 RPC, 再批量发改名请求. 流程:

```bash
# 终端 1: 启动 Chrome CDP (已登录 Gemini)
cd E:/MyCodeProjects/02-审计工具
powershell -File start_chrome_cdp.ps1

# 终端 2: 发现对话列表 RPC
python gemini_discover_rpc.py    # 等 60s, 滚动侧边栏

# 把输出发 Claude → 确认 RPCID → 批量改名
python gemini_batch_rename.py --dry-run    # 预览
python gemini_batch_rename.py              # 执行
```

### 注意事项
- 改名脚本用 page.evaluate fetch 发送请求 (带 cookies, 不需要额外认证)
- RPCID 未知, 需要 discovery 脚本捕获
- 1.5s 间隔防限流, 2245 条 ≈ 56 分钟
- Claude context 已满, 需新会话继续

## 分类前缀对照 (批量改名用)
| 前缀 | 分类 | 含义 |
|------|------|------|
| [AUD] | 审计合规 | 规则甄查/违禁词/广告法 |
| [LIV] | 直播运营 | 小桃/凡姐/苏苏/带货 |
| [DEV] | 技术开发 | Python/脚本/API/调试 |
| [CPY] | 文案创意 | 短视频/prompt/标题/故事 |
| [BRD] | 品牌设计 | LOGO/VI/配色/命名 |
| [OPS] | 系统运维 | PowerShell/网络/配置 |
| [CON] | 方案咨询 | 教育/商业/建议 |
| [DAT] | 数据报表 | SQL/报表/分析 |

## 关键文件索引
| 文件 | 位置 |
|------|------|
| 分类器 + 导出处理 | `02-审计工具/process_gemini_takeout.py` |
| 重分类 + 层级目录 | `02-审计工具/gemini_reclassify.py` |
| RPC 发现工具 | `02-审计工具/gemini_discover_rpc.py` |
| 批量改名脚本 | `02-审计工具/gemini_batch_rename.py` |
| API 抓包 | `02-审计工具/gemini_api_capture.py` |
| Chrome CDP 启动 | `02-审计工具/start_chrome_cdp.ps1` |
| API 捕获数据 | `02-审计工具/gemini_api_capture.json` |
| 新分类导出 | `02-审计工具/gemini_exported/reorganized_v3/` |
| Obsidian 对话 | `E:/Obsidian/Gemini对话/` |
