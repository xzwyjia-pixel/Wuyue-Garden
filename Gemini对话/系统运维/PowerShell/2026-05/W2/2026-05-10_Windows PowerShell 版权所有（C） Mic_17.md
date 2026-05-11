---
title: Windows PowerShell
source: gemini
date: 2026-05-10
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## Windows PowerShell

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> python live_observer.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'C:\\Users\\think\\live_observer.py': [Errno 2] No such file or directory
PS C:\Users\think> python live_observer.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'C:\\Users\\think\\live_observer.py': [Errno 2] No such file or directory
PS C:\Users\think> python live_observer.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'C:\\Users\\think\\live_observer.py': [Errno 2] No such file or directory
PS C:\Users\think> # 1. 进入正确的硬盘和目录
PS C:\Users\think> E:
PS E:\> cd MyCodeProjects
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 2. 运行 Claude 刚写好的脚本
PS E:\MyCodeProjects> python monitor_桃.py
E:\Users\think\AppData\Local\Programs\Python\Python310\python.exe: can't open file 'E:\\MyCodeProjects\\monitor_桃.py': [Errno 2] No such file or directory
PS E:\MyCodeProjects> # 1. 进入正确的硬盘和目录
PS E:\MyCodeProjects> E:
PS E:\MyCodeProjects> cd MyCodeProjects
cd : 找不到路径“E:\MyCodeProjects\MyCodeProjects”，因为该路径不存在。
所在位置 行:1 字符: 1
+ cd MyCodeProjects
+ ~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (E:\MyCodeProjects\MyCodeProjects:String) [Set-L
   ocation], ItemNotFoundException
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.SetLocationCommand

PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 2. 运行 Claude 刚写好的脚本
PS E:\MyCodeProjects> python monitor_桃.py
2026-05-10 12:07:24,155 [WARNING] Using CPU. Note: This module is much faster with a GPU.
2026-05-10 12:07:26,527 [INFO] 检测到浏览器窗口: 微信  (1025×1041)
2026-05-10 12:07:26,528 [INFO] 自适应评论区: (1563, 616, 328, 364)
2026-05-10 12:07:26,528 [INFO] == 监控启动  区域=(1563, 616, 328, 364)  间隔=30s  全景=300s ==
E:\Users\think\AppData\Local\Programs\Python\Python310\lib\site-packages\torch\utils\data\dataloader.py:775: UserWarning: 'pin_memory' argument is set as true but no accelerator is found, then device pinned memory won't be used.
  super().__init__(loader)
2026-05-10 12:07:27,743 [INFO] [OCR] 9 段文字  命中=[]
2026-05-10 12:07:27,914 [INFO] 全景 → temp_frames/tao_pano_20260510_120727.png
2026-05-10 12:07:27,970 [ERROR] 全景/比对失败
Traceback (most recent call last):
  File "E:\MyCodeProjects\monitor_桃.py", line 295, in main
    append_jsonl("triage_log.jsonl", triage)
  File "E:\MyCodeProjects\monitor_桃.py", line 82, in append_jsonl
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
  File "E:\Users\think\AppData\Local\Programs\Python\Python310\lib\json\__init__.py", line 238, in dumps
    **kw).encode(obj)
  File "E:\Users\think\AppData\Local\Programs\Python\Python310\lib\json\encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "E:\Users\think\AppData\Local\Programs\Python\Python310\lib\json\encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
  File "E:\Users\think\AppData\Local\Programs\Python\Python310\lib\json\encoder.py", line 179, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type float32 is not JSON serializable

好消息是，你的脚本已经成功运行并定位到了“微信”窗口！这说明我们的自适应坐标逻辑是正确的。
目前的报错 TypeError: Object of type float32 is not JSON serializable 是一个非常典型的 Python 技术细节问题：EasyOCR 或 OpenCV 输出的数值（float32）无法直接写入 JSON 文件。
别担心，这只需一行代码就能修复。请直接在 Claude Code 的终端里输入以下指令，让它自动完成修复：

🛠️ 给 Claude Code 的修复指令

指令：

修复 JSON 报错： 在 monitor_桃.py 中，找到 append_jsonl 或处理 triage 字典的地方。在执行 json.dumps 之前，确保将所有的 float32 数值转换为标准的 Python float。或者在 json.dumps 中增加一个 cls=NumpyEncoder（如果你定义了它）。
优化 OCR 频率： 目前似乎在启动时就报错了，请修复后重新启动监控。
清理旧文件： 启动前先清空 temp_frames/ 文件夹。



🧐 报错原因拆解（帮你快速理解）
你在终端看到的报错链：

monitor_桃.py 第 295 行调用了 append_jsonl。
json.dumps 试图把计算出来的“视觉评分”或“对比度数值”写进文件。
因为这些数值是由 numpy 计算出来的（类型是 float32），标准的 Python json 库不认识它。


🚀 修复后的操作流程
等 Claude 提示“Fixed”或“Updated”后，请在你的 PowerShell 中运行：
# 再次运行（现在路径已经是 E:\MyCodeProjects 了）
python monitor_桃.py

📈 针对“大山里的小桃”直播间的实时观察
虽然报错了，但日志显示它已经抓到了 9 段文字。这说明：

光线问题： 此时直播间可能是室内或夜间（火光背景），OCR 能认出 9 段文字说明对比度尚可。
命中率： 命中=[] 说明当前评论区没有出现你设定的关键词（如“多少钱”）。

建议改进： 让 Claude 在关键词里增加：“火、灶、好香、想吃、辛苦、小桃”。这类充满农村生活气息的词汇是这个直播间的“热度指标”。



一旦脚本重新跑起来不再报错，请盯住控制台。如果抓到了关键词，立刻把那段 JSON 日志发给我，我来帮你做“人设健康度”审计！

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-10*
