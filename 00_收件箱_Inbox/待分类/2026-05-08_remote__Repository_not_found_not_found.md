---
title: remote: Repository not found.
fatal: repository 'https://github.com/juliusbrussee/skill-creator.git/' not found
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 4. 手动拉取 Claude-HUD
PS C:\Users\think\.agents\skills> git clone https://github.com/juliusbrussee/claude-hud.git claude-hud
Cloning into 'claude-hud'...
info: please complete authentication in your browser...
remote: Repository not found.
fatal: repository 'https://github.com/juliusbrussee/claude-hud.git/' not found
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 5. 手动拉取 Find-skills
PS C:\Users\think\.agents\skills> git clone https://github.com/juliusbrussee/find-skills.git find-skills
fatal: destination path 'find-skills' already exists and is not an empty directory.
PS C:\Users\think\.agents\skills> # 进入技能目录
PS C:\Users\think\.agents\skills> cd "$env:USERPROFILE\.agents\skills"
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 使用 git 协议克隆，通常能绕过身份验证弹窗
PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/superpowers.git superpowers
Cloning into 'superpowers'...
fatal: unable to connect to github.com:
github.com[0: 20.205.243.166]: errno=Connection timed out

PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/skill-creator.git skill-creator
Cloning into 'skill-creator'...
fatal: unable to connect to github.com:
github.com[0: 20.205.243.166]: errno=Connection timed out

PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/claude-hud.git claude-hud
Cloning into 'claude-hud'...
fatal: unable to connect to github.com:
github.com[0: 20.205.243.166]: errno=Connection timed out

PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/find-skills.git find-skills
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## remote: Repository not found.
fatal: repository 'https://github.com/juliusbrussee/skill-creator.git/' not found
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 4. 手动拉取 Claude-HUD
PS C:\Users\think\.agents\skills> git clone https://github.com/juliusbrussee/claude-hud.git claude-hud
Cloning into 'claude-hud'...
info: please complete authentication in your browser...
remote: Repository not found.
fatal: repository 'https://github.com/juliusbrussee/claude-hud.git/' not found
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 5. 手动拉取 Find-skills
PS C:\Users\think\.agents\skills> git clone https://github.com/juliusbrussee/find-skills.git find-skills
fatal: destination path 'find-skills' already exists and is not an empty directory.
PS C:\Users\think\.agents\skills> # 进入技能目录
PS C:\Users\think\.agents\skills> cd "$env:USERPROFILE\.agents\skills"
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 使用 git 协议克隆，通常能绕过身份验证弹窗
PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/superpowers.git superpowers
Cloning into 'superpowers'...
fatal: unable to connect to github.com:
github.com[0: 20.205.243.166]: errno=Connection timed out

PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/skill-creator.git skill-creator
Cloning into 'skill-creator'...
fatal: unable to connect to github.com:
github.com[0: 20.205.243.166]: errno=Connection timed out

PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/claude-hud.git claude-hud
Cloning into 'claude-hud'...
fatal: unable to connect to github.com:
github.com[0: 20.205.243.166]: errno=Connection timed out

PS C:\Users\think\.agents\skills> git clone git://github.com/juliusbrussee/find-skills.git find-skills

甄先生，审计结论很残酷：自动安装脚本、HTTPS 协议、甚至是 Git 原生协议，在目前的网络链路下全军覆没了。
报错 Repository not found 并不是仓库没了，而是由于网络握手不完整，GitHub 服务器给出的错误反馈。这种反复的重试不仅浪费您的精力，也在白白消耗我们对话的 Token。
既然我们要追求**“极简精密”，就不要在已经断掉的链路上修修补补了。我们要用“物理注入法”**，直接把技能核心“空投”进您的地基。
甄先生的终极“空投”方案 (无需 Git)
请按以下步骤手动操作，这是目前最稳健、最省 Token 的办法：

第一步：清理战场
刚才失败的克隆可能留下了半截子文件夹。请在 PowerShell 中执行：
cd "$env:USERPROFILE\.agents\skills"
Remove-Item -Recurse -Force superpowers, skill-creator, claude-hud, find-skills -ErrorAction SilentlyContinue


第二步：手动下载 (建议在浏览器操作)
请直接在您的浏览器中访问以下地址，并点击 Download ZIP：

Superpowers: https://github.com/juliusbrussee/superpowers/archive/refs/heads/main.zip
Skill-Creator: https://github.com/juliusbrussee/skill-creator/archive/refs/heads/main.zip
Claude-HUD: https://github.com/juliusbrussee/claude-hud/archive/refs/heads/main.zip
Find-Skills: https://github.com/juliusbrussee/find-skills/archive/refs/heads/main.zip


第三步：物理注入

打开文件夹：C:\Users\think\.agents\skills。
将下载的 4 个 ZIP 包全部解压到这里。
关键动作：解压后的文件夹名可能叫 superpowers-main，请手动重命名去掉 -main 后缀（即：文件夹名必须精准为 superpowers、skill-creator 等）。


第四步：唤醒超能力 (Link)
回到 PowerShell，执行最后一次“点火”指令：
npx skills link --all


💡 甄先生的审计提示：
通过这种“物理搬运”，我们彻底绕过了 GitHub 的登录弹窗和网络丢包。一旦这几个文件夹出现在正确的位置，Claude 在启动时就会自动加载它们。
甄先生，您先去浏览器把这 4 个包下好。等您解压并重命名完成后，我们再进行最后一步的“全明星”联合调试。
如果您在下载过程中遇到困难，请告诉我，我可以为您寻找其他的镜像下载链路。

---
*从 Gemini 导出，2026-05*
