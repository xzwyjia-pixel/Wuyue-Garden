---
title: Prompted
source: gemini
date: 2026-05-08
category: 项目管理
tags: [gemini, 项目管理]
---

## Prompted

甄先生，这张弹窗正是克隆失败的**“最后一道关卡”**。这是 GitHub 的凭据管理器在要求验证身份。
既然我们要追求**“静奢”且不被打扰**的自动化环境，与其在这里反复输入验证码，不如换一种更“极简”的物理绕过方式。
甄先生的两种“精准拆弹”方案：
方案 A：点击“Sign in with your browser” (推荐)
这是最快的。点击蓝色按钮，它会跳到您的浏览器（只要您浏览器里登录了 GitHub），点一下确认，这边的克隆就会立刻自动继续。

优点：一劳永逸。
注意：请确保您的浏览器能够正常访问 github.com。

方案 B：由于网络原因无法登录？改用 SSH 协议 (最专业)
如果浏览器弹不出来，或者网页打不开，我们可以彻底绕过这个登录界面。

直接关掉这个弹窗（点右上角的 X）。
改用以下命令克隆（将 https:// 换成极简的 git://）：

# 进入技能目录
cd "$env:USERPROFILE\.agents\skills"

# 使用 git 协议克隆，通常能绕过身份验证弹窗
git clone git://github.com/juliusbrussee/superpowers.git superpowers
git clone git://github.com/juliusbrussee/skill-creator.git skill-creator
git clone git://github.com/juliusbrussee/claude-hud.git claude-hud
git clone git://github.com/juliusbrussee/find-skills.git find-skills


甄先生，如果您觉得折腾 GitHub 身份验证太繁琐：
您可以直接采用我的**“手动降维打击”**法：

直接在浏览器下载这几个仓库的 Zip 包。
解压到 C:\Users\您的用户名\.agents\skills\。
执行 npx skills link --all。

只要文件夹进去了，Claude 就能拥有超能力，不需要非得通过 Git 认证。
甄先生，您是准备点一下那个蓝色按钮，还是让我帮您准备 Zip 包的下载地址？

---
*从 Gemini 导出，2026-05*
