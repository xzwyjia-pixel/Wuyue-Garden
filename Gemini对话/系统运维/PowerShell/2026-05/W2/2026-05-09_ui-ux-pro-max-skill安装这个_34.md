---
title: ui-ux-pro-max-skill安装这个
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## ui-ux-pro-max-skill安装这个

## ui-ux-pro-max-skill安装这个

既然你已经进入了 Claude Code 界面，安装这个技能非常简单。
由于你刚才已经成功运行了 skill_creator，说明你的环境支持通过“技能名”自动构建或检索。请直接在 Claude Code 的输入框（即 > 后面）输入以下指令：

create_skill ui-ux-pro-max-skill
或者
使用 skill_creator 安装 ui-ux-pro-max-skill


为什么这样做？
在你的系统中，这些 "Pro Max" 级别的技能通常遵循你 E:\MyCodeProjects\skill-creator\spec 目录下的规范。

自动检索模板：Claude 会去你的 template 文件夹寻找最匹配的高级 UI/UX 规范。
生成增强型 SKILL.md：它不仅会包含你刚才看到的简单映射表，还会加入你偏好的 “极简主义精密感” (Minimalist Precision) 和 “工业级” (Industrial-grade) 的设计审美逻辑。
用户级安装：它会自动把文件放在 C:\Users\think\.claude\skills\ui-ux-pro-max-skill\SKILL.md，让你所有的项目都能调用这套高级 UI 准则。

如果你想手动安装（通过 PowerShell）：
如果你想从某个路径直接复制过去，可以使用：
# 先创建目录
mkdir -p "C:/Users/think/.claude/skills/ui-ux-pro-max-skill"

# 复制你的高级规范模板（假设你在 skill-creator 目录下有这个备份）
cp "E:\MyCodeProjects\skill-creator\template\SKILL.md" "C:/Users/think/.claude/skills/ui-ux-pro-max-skill/SKILL.md"

执行完安装后，别忘了对 Claude 说：

"Reload skills and check if ui-ux-pro-max-skill is active."

这样它就能立刻应用那套“工业级精密感”的设计逻辑来帮你写代码了。需要我帮你直接写一段符合这个技能标准的 语义化图标可视化 前端代码吗？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
