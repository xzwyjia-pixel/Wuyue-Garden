---
title: Prompted
source: gemini
date: 2026-05-03
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

很好，测试结果显示你的基础环境非常完美：Git 2.54.0 和 Git-LFS 3.7.1 均已安装成功。这说明你的电脑已经具备了拉取大型 AI 模型项目的“门票”。
现在我们可以直接开始 GPT-SoVITS 的部署。请严格按照以下步骤操作，确保每一步都在虚拟环境中进行，以保持系统的极简精密。
第一阶段：项目克隆与环境初始化
请在当前的命令行窗口（C:\Users\think）中继续输入：
# 1. 进入你创建好的目标目录
cd /d D:\git_project\GPT-SoVITS

# 2. 克隆项目到当前目录
git clone https://github.com/RVC-Boss/GPT-SoVITS.git .

# 3. 创建 Python 虚拟环境 (venv)
python -m venv venv

# 4. 激活虚拟环境 (注意：激活后命令行开头会出现 (venv) 字样)
.\venv\Scripts\activate


第二阶段：依赖库安装（强制清华源）
激活环境后，执行以下命令来安装核心组件。
# 1. 升级 pip 工具
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 安装 Torch 系列（建议安装适配 CUDA 的版本以发挥显卡性能）
pip install torch torchvision torchaudio --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 安装项目依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


第三阶段：从 ModelScope 下载权重
我们将使用 ModelScope 官方工具来下载 GPT-SoVITS 所需的所有预训练模型文件。
# 安装 ModelScope
pip install modelscope -i https://pypi.tuna.tsinghua.edu.cn/simple

# 运行 Python 脚本自动下载并放置模型文件
python -c "from modelscope import snapshot_download; snapshot_download('iic/GPT-SoVITS', local_dir='./GPT_SoVITS/pretrained_models')"


第四阶段：验证运行
一切准备就绪后，尝试启动 Web 界面：
python webui.py

操作贴士：

激活状态： 每次关闭电脑后重新进入该目录，记得都要先执行 .\venv\Scripts\activate。
FFmpeg： GPT-SoVITS 对音频切片需要调用 FFmpeg。如果你运行报错找不到 ffmpeg，请告诉我，我给你快速安装建议。

现在你可以先执行第一阶段的命令。克隆和安装过程需要一点时间，如果中间有任何报错，请直接截图发给我。

---
*从 Gemini 导出，2026-05*
