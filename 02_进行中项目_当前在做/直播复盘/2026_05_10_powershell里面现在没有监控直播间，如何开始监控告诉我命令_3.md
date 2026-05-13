---
title: powershell里面现在没有监控直播间，如何开始监控?告诉我命令
source: gemini
date: 2026-05-10
category: 直播运营
tags: [gemini, 直播运营]
---

## powershell里面现在没有监控直播间，如何开始监控?告诉我命令

既然你已经完成了系统的重构和乱码修复，现在启动监控非常简单。根据你之前的工程结构，你需要通过 start_audit.py 这个总控脚本来运行。
在 PowerShell 中执行以下命令：
1. 启动特定直播间监控（以“凡姐”为例）
直接运行你封装好的启动脚本，并指定目标：
python start_audit.py --target "凡姐走乡村"

2. 如果你想更换直播间
由于你已经要求 Claude 实现了“动态向量引擎”，你只需要更换参数名（前提是你在 instructions.md 中已经配置了该直播间的坐标和关键词）：
python start_audit.py --target "新的直播间名称"


💡 启动后的操作建议

确认窗口位置：
启动命令后，脚本会尝试调用 find_and_pin()。请确保你的直播间浏览器窗口或微信视频号窗口是打开状态，且没有被最小化。
查看静默日志：
如果你刚才执行了“静默运行”指令，控制台可能输出较少。你可以随时打开另一个 PowerShell 窗口查看实时详细日志：
Get-Content E:\MyCodeProjects\logs\audit.log -Wait


检查资产生成：
监控运行几分钟后，你可以去文件夹确认截图是否在生成：
ls E:\MyCodeProjects\Audit_Assets\Fanjie\



如果你发现输入 python start_audit.py 报错，请把错误代码贴给我，我帮你排查是否是路径或 Python 环境的问题。

---
*从 Gemini 导出，2026-05*
