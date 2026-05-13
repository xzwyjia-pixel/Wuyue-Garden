---
title: Prompted
source: gemini
date: 2026-05-03
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

看到报错了。这是因为在 PowerShell 中切换盘符时，必须带上英文冒号 :，而且不能直接把我的回复文本（如“小贴士”字样）粘贴进终端。
既然你确定在 E 盘操作，请务必完全按照下面的指令序列一行一行地输入（不要复制多余的汉字）：
第一步：正确切换到 E 盘
在终端里输入并回车：
E:

第二步：进入你的项目目录
（假设你还是在 git_project\GPT-SoVITS 目录下操作）
cd \git_project\GPT-SoVITS

第三步：激活虚拟环境
这是确保不污染全局环境的关键步骤，请确认文件夹下有 venv 目录：
.\venv\Scripts\activate

执行完这行，如果看到路径前面多了个 (venv)，就说明成功了。
第四步：重新尝试模型下载
现在你已经有了 E 盘的写入权限，且在虚拟环境下，执行下载脚本：
python -c "from modelscope import snapshot_download; snapshot_download('iic/GPT-SoVITS', local_dir='./GPT_SoVITS/pretrained_models')"


为什么你之前的操作会报错？

缺少冒号： 只打 D 或 C 而不带 :，Windows 会认为你在运行一个叫 "D" 的软件，所以提示找不到命令。
粘贴了非命令文本： PowerShell 无法识别“请确认一下”这种自然语言，它只能听懂特定的指令代码。
权限冲突： 之前的 PermissionError 是因为你试图在系统受保护的 Python 安装目录下（E:\Users\think\AppData\...）创建缓存，激活 venv 后，它会优先使用项目本地目录，权限问题就会迎刃而解。

如果第一步 E: 执行后成功切换，请继续后续操作。如果 cd 找不到目录，请告诉我，我们重新克隆项目。

---
*从 Gemini 导出，2026-05*
