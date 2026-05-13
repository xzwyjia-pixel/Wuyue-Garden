---
title: Prompted
source: gemini
date: 2026-05-03
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

看到你的新截图了。报错 ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt' 说明你虽然进入了文件夹，但这个文件夹里没有项目文件。
这通常是因为解压时，文件被套在了多层文件夹里（比如 GPT_SoVITS/GPT-SoVITS-master/requirements.txt）。
咱们用最直接的方法定位文件：
第一步：找准文件到底在哪
在当前的黑色窗口里输入：
ls


如果你看到里面只有一个文件夹（比如 GPT-SoVITS-master），请执行：
cd GPT-SoVITS-master（换成你看到的那个文件夹名），然后再次输入 ls 确认能看到 requirements.txt。
如果你看到里面是空的，说明解压的位置不对。


第二步：正确的安装和下载流程
一旦你在 ls 命令的结果里亲眼看到了 requirements.txt，请依次执行：


安装依赖：
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple



下载模型：
（确保你在 requirements.txt 所在的目录下执行）
python -c "from modelscope import snapshot_download; snapshot_download('iic/GPT-SoVITS', local_dir='GPT_SoVITS/pretrained_models')"



启动：
python webui.py




💡 核心原因排查
从 image_5c2914.png 来看，你当时身处 pretrained_models 文件夹的子目录里。运行代码必须在项目的根目录（即包含 webui.py 的那个文件夹）。
请现在输入 ls 并截图发给我，我帮你看看你现在的“脚下”到底有哪些文件，这样我们就知道该往哪跑了！

---
*从 Gemini 导出，2026-05*
