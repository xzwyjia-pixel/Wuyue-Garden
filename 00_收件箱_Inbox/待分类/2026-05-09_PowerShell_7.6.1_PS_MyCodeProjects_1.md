---
title: PowerShell 7.6.1
PS C:\Windows\System32> cd E:/MyCodeProjects && git push --dry-run
fatal: The current branch master has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin master

To have this happen automatically for branches without a tracking
upstream, see 'push.autoSetupRemote' in 'git help config'.

PS E:\MyCodeProjects> where gstack
PS E:\MyCodeProjects> gstack --version
gstack: The term 'gstack' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> find_skill --help
find_skill: The term 'find_skill' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> skill_creator --helppip list | findstr "skill"
skill_creator: The term 'skill_creator' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> # 检查已安装的包中是否包含 "skill" 或 "gstack" 相关项
PS E:\MyCodeProjects> pip list | Select-String "skill", "gstack"
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 尝试作为模块运行 (如果它是以这种方式安装的)
PS E:\MyCodeProjects> python -m find_skill --help
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: No module named find_skill
PS E:\MyCodeProjects> python -m skill_creator --help
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: No module named skill_creator
PS E:\MyCodeProjects> # 假设你在项目根目录，尝试激活虚拟环境
PS E:\MyCodeProjects> .\.venv\Scripts\activate
.\.venv\Scripts\activate: The term '.\.venv\Scripts\activate' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 激活后再测试命令
PS E:\MyCodeProjects> where.exe gstack
信息: 用提供的模式无法找到文件。
PS E:\MyCodeProjects> find_skill --help
find_skill: The term 'find_skill' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> git push -u origin master
remote: Repository not found.
fatal: repository 'https://github.com/你的用户名/你的仓库名.git/' not found
PS E:\MyCodeProjects> git config --global push.autoSetupRemote true
PS E:\MyCodeProjects> # 搜索包含 "skill" 关键字的 Python 文件或可执行文件
PS E:\MyCodeProjects> Get-ChildItem -Path "E:\MyCodeProjects" -Filter "*skill*" -Recurse -ErrorAction SilentlyContinue

    Directory: E:\MyCodeProjects

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                skill-creator

    Directory: E:\MyCodeProjects\.claude

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-09 周六    15:08                skills

    Directory: E:\MyCodeProjects\.claude\skills\openspec-apply-change

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08           4774 SKILL.md

    Directory: E:\MyCodeProjects\.claude\skills\openspec-archive-change

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08           4157 SKILL.md

    Directory: E:\MyCodeProjects\.claude\skills\openspec-explore

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08          10738 SKILL.md

    Directory: E:\MyCodeProjects\.claude\skills\openspec-propose

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08           4646 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                skills

    Directory: E:\MyCodeProjects\skill-creator\skills

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-09 周六    13:26                skill-creator

    Directory: E:\MyCodeProjects\skill-creator\skills\algorithmic-art

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          20173 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\brand-guidelines

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           2308 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\canvas-design

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          12068 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\claude-api

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          33365 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\doc-coauthoring

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          16190 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\docx

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          20674 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\frontend-design

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           4482 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\internal-comms

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           1543 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\mcp-builder

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           9328 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\pdf

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           8386 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\pptx

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           9414 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\skill-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          33653 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\skill-creator\scripts

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           4370 package_skill.py

    Directory: E:\MyCodeProjects\skill-creator\skills\slack-gif-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           8095 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\theme-factory

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           3183 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\web-artifacts-builder

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           3160 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\webapp-testing

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           4008 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\xlsx

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          11754 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\spec

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45             90 agent-skills-spec.md

    Directory: E:\MyCodeProjects\skill-creator\template

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45            146 SKILL.md

PS E:\MyCodeProjects> uv tool list
uv: The term 'uv' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.

[General Feedback]
  The most similar commands are:
    > gv, nv, rv, sv, mv

PS E:\MyCodeProjects> # 或者尝试通过 uv 直接运行（如果已安装，它会自动找到）
PS E:\MyCodeProjects> uvx find_skill --help
uvx: The term 'uvx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> # 查看目前的远程地址
PS E:\MyCodeProjects> git remote -v
origin  https://github.com/你的用户名/你的仓库名.git (fetch)
origin  https://github.com/你的用户名/你的仓库名.git (push)
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 更换为正确的地址 (替换下方的 URL)
PS E:\MyCodeProjects> git remote set-url origin https://github.com/你的真实用户名/你的真实仓库名.git
PS E:\MyCodeProjects>
source: gemini
date: 2026-05-09
category: 编程开发
tags: [gemini, 编程开发]
---

## PowerShell 7.6.1
PS C:\Windows\System32> cd E:/MyCodeProjects && git push --dry-run
fatal: The current branch master has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin master

To have this happen automatically for branches without a tracking
upstream, see 'push.autoSetupRemote' in 'git help config'.

PS E:\MyCodeProjects> where gstack
PS E:\MyCodeProjects> gstack --version
gstack: The term 'gstack' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> find_skill --help
find_skill: The term 'find_skill' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> skill_creator --helppip list | findstr "skill"
skill_creator: The term 'skill_creator' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> # 检查已安装的包中是否包含 "skill" 或 "gstack" 相关项
PS E:\MyCodeProjects> pip list | Select-String "skill", "gstack"
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 尝试作为模块运行 (如果它是以这种方式安装的)
PS E:\MyCodeProjects> python -m find_skill --help
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: No module named find_skill
PS E:\MyCodeProjects> python -m skill_creator --help
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: No module named skill_creator
PS E:\MyCodeProjects> # 假设你在项目根目录，尝试激活虚拟环境
PS E:\MyCodeProjects> .\.venv\Scripts\activate
.\.venv\Scripts\activate: The term '.\.venv\Scripts\activate' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 激活后再测试命令
PS E:\MyCodeProjects> where.exe gstack
信息: 用提供的模式无法找到文件。
PS E:\MyCodeProjects> find_skill --help
find_skill: The term 'find_skill' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> git push -u origin master
remote: Repository not found.
fatal: repository 'https://github.com/你的用户名/你的仓库名.git/' not found
PS E:\MyCodeProjects> git config --global push.autoSetupRemote true
PS E:\MyCodeProjects> # 搜索包含 "skill" 关键字的 Python 文件或可执行文件
PS E:\MyCodeProjects> Get-ChildItem -Path "E:\MyCodeProjects" -Filter "*skill*" -Recurse -ErrorAction SilentlyContinue

    Directory: E:\MyCodeProjects

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                skill-creator

    Directory: E:\MyCodeProjects\.claude

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-09 周六    15:08                skills

    Directory: E:\MyCodeProjects\.claude\skills\openspec-apply-change

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08           4774 SKILL.md

    Directory: E:\MyCodeProjects\.claude\skills\openspec-archive-change

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08           4157 SKILL.md

    Directory: E:\MyCodeProjects\.claude\skills\openspec-explore

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08          10738 SKILL.md

    Directory: E:\MyCodeProjects\.claude\skills\openspec-propose

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-09 周六    15:08           4646 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    18:45                skills

    Directory: E:\MyCodeProjects\skill-creator\skills

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-09 周六    13:26                skill-creator

    Directory: E:\MyCodeProjects\skill-creator\skills\algorithmic-art

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          20173 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\brand-guidelines

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           2308 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\canvas-design

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          12068 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\claude-api

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          33365 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\doc-coauthoring

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          16190 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\docx

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          20674 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\frontend-design

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           4482 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\internal-comms

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           1543 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\mcp-builder

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           9328 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\pdf

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           8386 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\pptx

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           9414 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\skill-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          33653 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\skill-creator\scripts

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           4370 package_skill.py

    Directory: E:\MyCodeProjects\skill-creator\skills\slack-gif-creator

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           8095 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\theme-factory

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           3183 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\web-artifacts-builder

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           3160 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\webapp-testing

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45           4008 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\skills\xlsx

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45          11754 SKILL.md

    Directory: E:\MyCodeProjects\skill-creator\spec

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45             90 agent-skills-spec.md

    Directory: E:\MyCodeProjects\skill-creator\template

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---     2026-05-08 周五    18:45            146 SKILL.md

PS E:\MyCodeProjects> uv tool list
uv: The term 'uv' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.

[General Feedback]
  The most similar commands are:
    > gv, nv, rv, sv, mv

PS E:\MyCodeProjects> # 或者尝试通过 uv 直接运行（如果已安装，它会自动找到）
PS E:\MyCodeProjects> uvx find_skill --help
uvx: The term 'uvx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> # 查看目前的远程地址
PS E:\MyCodeProjects> git remote -v
origin  https://github.com/你的用户名/你的仓库名.git (fetch)
origin  https://github.com/你的用户名/你的仓库名.git (push)
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 更换为正确的地址 (替换下方的 URL)
PS E:\MyCodeProjects> git remote set-url origin https://github.com/你的真实用户名/你的真实仓库名.git
PS E:\MyCodeProjects>

找到了！从你的搜索结果来看，情况已经非常明朗了：
1. 你的“Skills”在哪里？
你电脑里确实有这些东西，但它们不是全局安装的软件，而是位于 E:\MyCodeProjects\skill-creator 目录下的 Markdown 规范文件和脚本。

技能库位置： E:\MyCodeProjects\skill-creator\skills。这里包含了你提到的各种技能（如 skill-creator、mcp-builder 等），它们是以 SKILL.md 的形式存在的。
.claude 目录： 你的项目根目录下有一个 .claude\skills 文件夹。这通常意味着你正在使用 Claude Desktop 或某个支持 Claude Skills 协议的插件，这些 SKILL.md 文件是给 AI Agent 读取的“指令集”。

2. 为什么命令无效？

find_skill 和 skill_creator： 这些并不是系统命令。根据目录结构，它们应该是你正在使用的某个 AI 代理（Agent）内部定义的工具（Tools）。只有当你在 Claude 或特定的 Agent 环境中对话时，AI 才能调用这些“技能”。
package_skill.py： 我在 E:\MyCodeProjects\skill-creator\skills\skill-creator\scripts 下发现了一个 Python 脚本。如果你想运行它，需要进入该目录并使用 Python：
cd E:\MyCodeProjects\skill-creator\skills\skill-creator\scripts
python package_skill.py


gstack： 搜索结果中完全没有出现 gstack。这可能是一个误记，或者是你之前尝试安装但失败了的某个 MCP Server（比如 gstack-mcp）。


3. 接下来的操作建议
如果你想“使用”这些技能：
你不需要在 PowerShell 里运行它们。你应该打开 Claude Desktop 或 Cursor，确保你的项目路径指向 E:\MyCodeProjects。AI 会自动读取 .claude/skills 下的说明书，然后你直接在对话框里对 AI 说：

“请使用 find_skill 帮我查找关于 XXX 的技能”

如果你想修复 Git：
你已经执行了 git remote set-url，但请确保你把 [https://github.com/你的真实用户名/你的真实仓库名.git](https://github.com/你的真实用户名/你的真实仓库名.git) 替换成了你 GitHub 页面上显示的那个真实地址。
你可以运行这个命令检查一下：
git remote -v

关于 uv：
既然 uv 命令报错，说明你还没安装这个极速的 Python 包管理器。如果你以后要频繁玩 MCP 或 AI Agent，建议安装它（它是目前 AI 开发圈的最爱）：
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

总结： 你的电脑里已经装好了全套的 Skill 模板，只是它们是“文档型工具”，需要通过 AI 界面（如 Claude）来激活，而不是在命令行里直接敲。你想试试用 Claude 调试一下这些技能吗？

---
*从 Gemini 导出，2026-05*
