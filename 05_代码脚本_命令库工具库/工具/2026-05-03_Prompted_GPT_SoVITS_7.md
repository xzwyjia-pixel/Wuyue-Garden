---
title: Prompted
source: gemini
date: 2026-05-03
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

根据截图中的报错信息，我们现在遇到了两个具体问题：

Git 链接连写错误： 你的 git clone 命令后面紧跟着 cd 命令，中间没有空格或换行，导致 Git 把 ...gitcd 当成了错误的网址。同时，网络出现了 Connection was reset，说明访问 GitHub 需要稍微“稳”一点。
模型下载依然 404： 因为克隆没成功，E:\git_project 下面没有 GPT-SoVITS 文件夹，所以下载脚本找不到存放路径。

我们来一次**“终极精密修复”。请不要**一次性复制多行，一行一行来，确保每一行执行完都没有红色字：
1. 确保在正确的文件夹
你现在已经在 E:\git_project 了（截图显示路径是正确的），直接开始克隆。
2. 正确克隆项目（拆分命令）
如果 GitHub 连接不稳定，我们可以尝试使用学术加速镜像（镜像站仅用于加速下载，内容一致）：
# 使用镜像地址克隆，避免连接重置
git clone https://mirror.ghproxy.com/https://github.com/RVC-Boss/GPT-SoVITS.git

执行完后，输入 ls 看看是不是多了一个 GPT-SoVITS 文件夹。
3. 进入文件夹
cd GPT-SoVITS

4. 再次执行模型下载
现在你已经在项目目录里了，ModelScope 就能找到路径了：
python -c "from modelscope import snapshot_download; snapshot_download('iic/GPT-SoVITS', local_dir='GPT_SoVITS/pretrained_models')"


⚠️ 为什么你之前的操作失败了？（深度纠错）

命令粘连： 截图显示你输入的是 ...GPT-SoVITS.gitcd GPT-SoVITS。在计算机眼里，它认为你要下载一个叫 .gitcd 的奇怪文件。
网络波动： Connection was reset 通常是由于网络环境直接连接 GitHub 不稳定造成的。换用镜像地址（ghproxy）通常能解决 90% 的下载报错。

请先尝试执行第 2 步的镜像克隆。如果还是报错 fatal: destination path 'GPT-SoVITS' already exists，说明文件夹其实已经有了，请直接跳到第 3 步 cd 进去。

---
*从 Gemini 导出，2026-05*
