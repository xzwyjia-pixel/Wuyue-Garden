---
title: Prompted
source: gemini
date: 2026-05-03
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

从你最新的截图来看，情况已经非常明朗了：你的 E:\git_project\GPT_SoVITS 文件夹目前是一个**“空壳”**。
通过 ls 命令可以看到，这个目录下只有一个 pretrained_models 文件夹。因为缺少 requirements.txt 和 webui.py 等核心文件，所以你执行任何安装或运行命令都会报错“No such file or directory”。
我们要执行一次**“灵魂搬家”**，把项目真正的文件放进去。请按以下步骤操作：

1. 找到真正的项目文件
你在之前肯定解压过一个从 Gitee 或 GitHub 下载的压缩包。请在电脑里找一下，目标文件夹里应该包含：

webui.py
requirements.txt
api.py
许多其他 .py 文件和文件夹。

它可能被重命名为了 GPT-SoVITS-master 或者就在你的下载文件夹里。
2. 执行搬运

选中刚才找到的那些所有文件和文件夹。
复制它们。
来到截图中的路径：E:\git_project\GPT_SoVITS。
粘贴进去。

3. 验证与启动
当你把文件贴进去后，回到这个黑色的 PowerShell 窗口，执行以下命令：
第一步：确认文件到位
ls

如果你能看到一长串文件名（尤其是 webui.py），说明成功了。
第二步：安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

第三步：下载模型（填满那个空目录）
python -c "from modelscope import snapshot_download; snapshot_download('iic/GPT-SoVITS', local_dir='pretrained_models')"

第四步：启动程序
python webui.py


💡 为什么会一直 404 或者报错？
因为 ModelScope 的下载脚本和 Python 运行脚本都依赖于当前路径下的文件结构。如果你的文件夹里只有 pretrained_models，就像一个只有地基没有房子的工地，工人（Python）进去找不到图纸（requirements）和工具（webui），自然就罢工了。
去把文件“搬”过来吧！只要 ls 能看到那些文件，我们这趟折腾就到终点了。

---
*从 Gemini 导出，2026-05*
