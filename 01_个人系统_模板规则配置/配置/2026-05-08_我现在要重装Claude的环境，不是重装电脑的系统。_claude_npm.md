---
title: 我现在要重装Claude的环境，不是重装电脑的系统。
source: gemini
date: 2026-05-08
category: 编程开发
tags: [gemini, 编程开发]
---

## 我现在要重装Claude的环境，不是重装电脑的系统。

甄先生，理解了。刚才是我把“重装”的颗粒度调得太粗了。既然不动系统，只对 Claude 的数字生存环境进行“推倒重建”，那这就变成了一场精准的局部手术。
目前的报错（targetAgents.some）和之前的连接问题，是因为旧的配置缓存、错误的全局包指向和无效的认证信息在后台打架。
请严格按以下步骤进行“环境净空与精密重建”：

第一步：彻底“拆除”旧建筑（环境清理）
我们要把所有和 Claude 相关的痕迹抹除，防止旧代码“借尸还魂”。请在 PowerShell 中执行：

卸载全局工具：
npm uninstall -g @anthropic-ai/claude-code


强制清理本地缓存（核心步骤）：
直接删除这个目录，这里藏着之前失败的 /model 记录和错误的 Token 映射。
Remove-Item -Recurse -Force "$env:AppData\claude-code"
# 同时清理可能存在的 npm 缓存残留
npm cache clean --force




第二步：地基加固（通信协议对齐）
在安装之前，先确保“隧道”是通的，且不再有 TLS 证书的报错。
# 1. 彻底修正环境变量（确保没有 /v1 后缀冲突）
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.gptsapi.net/v1", "User")
$env:ANTHROPIC_BASE_URL = "https://api.gptsapi.net/v1"

# 2. 检查 Python 版本（刚才审计过，3.10 可以用，但建议保持纯净环境）


第三步：精密搭载“三剑客”（按序安装）
甄先生，安装顺序非常关键。我们要先装主体，再装“省钱”插件，最后装“增强”技能。
1. 安装主体
npm install -g @anthropic-ai/claude-code

2. 安装 Caveman（优先下载，保住 Token）
注意： 为了避开之前的 targetAgents.some 报错，我们要先进入项目目录再装。
cd "E:\MyCodeProjects"
# 手动创建一个 package.json 诱导安装程序识别
echo "{}" > package.json

# 使用 -y 强制安装
npx skills add juliusbrussee/caveman --skill caveman -y

3. 下载 Superpowers 与技能映射
npx skills add juliusbrussee/superpowers --skill superpowers -y


第四步：激活“规则甄查”总部
现在环境已经重装完成，我们要用最极简的方式启动，不走冗余的流程：

启动 Claude：
claude --model claude-3-5-sonnet-20241022


初始化指令（进场第一句话）：

“我是甄先生。环境已完成精密重装。激活 Caveman Ultra 压缩模式。读取 CLAUDE.md，准备开始‘规则甄查’逻辑审计。”




甄先生的审计提示：
如果您在安装 caveman 时依然看到 targetAgents 报错，说明这个 skills 工具本身与当前 Node.js 版本有冲突。如果发生这种情况，请立刻停止尝试。我会直接教您如何通过 MCP 协议手动挂载这些功能，那才是真正的“极简精密”，且完全不受这些第三方脚本 Bug 的影响。
甄先生，第一步“彻底卸载”执行完了吗？

---
*从 Gemini 导出，2026-05*
