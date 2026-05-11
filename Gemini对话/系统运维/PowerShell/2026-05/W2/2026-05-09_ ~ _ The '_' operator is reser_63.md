---
title: |                        ~
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## |                        ~

##      |                        ~
     | The '<' operator is reserved for future use.
PS E:\MyCodeProjects> # 1. 关联远程仓库（请替换实际 URL，不要带尖括号）
>> git remote add origin https://github.com/你的用户名/你的仓库名.git
>>
>> # 2. 切换主分支名为 master
>> git branch -M master
>>
>> # 3. 最终权限预检
>> git push -u origin master --dry-run
remote: Repository not found.
fatal: repository 'https://github.com/你的用户名/你的仓库名.git/' not found
PS E:\MyCodeProjects> gh repo create RuleInvestigator --public --source=. --remote=origin
To get started with GitHub CLI, please run:  gh auth login
Alternatively, populate the GH_TOKEN environment variable with a GitHub API authentication token.
PS E:\MyCodeProjects> # 启动 GitHub 登录流
>> gh auth login
? Where do you use GitHub?  [Use arrows to move, type to filter]
> GitHub.com
  Other

交互指南 (Interaction Guide)
1. 结论 (Conclusion)
由于无法在图形界面操作，我们将通过 GH CLI 终端认证 绕过网页打不开的障碍。请按照以下步骤在 PowerShell 中完成交互。
2. 执行步骤 (Step-by-Step)
请在终端继续操作：

Where do you use GitHub? 选中 GitHub.com 并按回车。
What is your preferred protocol for Git operations? 选中 HTTPS 并按回车。
Authenticate Git with your GitHub credentials? 选中 Yes 并按回车。
How would you like to authenticate GitHub CLI?

关键选择：选择 Login with a web browser。
系统会显示一个 8 位动态代号（如 ABCD-1234）。
操作：由于你电脑打不开网页，请在手机浏览器上访问 github.com/login/device（手机通常可以访问），输入电脑屏幕显示的代号并点击授权。



3. 授权成功后的指令 (Post-Auth Actions)
一旦终端显示 Logged in as [你的用户名]，请依次执行以下命令：
# 1. 创建远程仓库并关联
gh repo create RuleInvestigator --public --source=. --remote=origin

# 2. 初始推送
git push -u origin master

4. 阶段三全自动指令 (Phase 3 Execution)
当 GitHub 通路彻底打通后，向 Claude Code 发送：

指令： > "执行阶段三：1. 编写 obsidian_sync.py。在 notes 目录生成符合‘极简主义’原则的 Markdown 审计报告。2. 执行自动化 Git 同步：git pull --rebase origin master 随后 git add . && git commit -m 'Auto-sync: Phase 3' && git push origin master。若遇冲突立即停止，如实报告。"


⚠️ 审计禁令 (Negative Constraints)

NEVER：在授权未成功前执行阶段三，否则会导致 Claude Code 陷入死循环。
DO NOT：分享你的 8 位授权代号给任何人。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
