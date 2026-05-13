---
title: Prompted
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## Prompted

甄先生，非常棒！从图 2 来看，你已经成功创建了 .ssh 目录并成功运行了 ssh-keyscan。虽然最后一行提示了 unsupported KEX method，但前面的 # github.com:22 SSH-2.0-00779af 说明你已经成功抓取到了 GitHub 的服务器信息并写入了信任名单。
现在，障碍已经基本扫除。我们来执行最后一步安装。

1. 确认安装环境
在执行安装前，请确保你的 VPN 依然处于“全局”模式。
在 PowerShell 中输入以下命令，确保你能通向 GitHub 的 HTTPS 端口：
Test-NetConnection github.com -Port 443

如果返回 TcpTestSucceeded : True，请继续。

2. 执行安装（HTTPS 绕过法）
进入 claude 界面，我们要避开容易报错的 SSH 协议，改用最稳妥的 HTTPS 链接 直接安装：
/plugin add https://github.com/JuliusBrussee/caveman

或者尝试简化版：
/plugin install JuliusBrussee/caveman


3. 如果依然报错 504（网关超时）
如果你发现命令发出去后又转了很久，然后跳出红色的 504 错误，这说明 api.gptsapi.net 的中转网关在下载大文件时依然不稳定。
此时请用“偷梁换柱”法：

退出 Claude。
输入：$env:ANTHROPIC_BASE_URL="" (临时禁用中转站地址)。
输入：claude (直接进入原生模式)。
执行安装命令：/plugin install JuliusBrussee/caveman。
注意：此步如果提示 API Key 无效是正常的（因为 Key 是中转站的），但有时它会先完成插件下载。


4. 业务检查清单
安装完成后，请执行以下命令检查“甄先生”的视觉化业务是否打通：

检查插件状态： /plugins (看 caveman 是否在列表中)
检查 Agent： /stats (看 Agent 数量是否从 0 变成了 1)
尝试运行： /caveman (看是否能弹出“进入 Caveman 模式”的提示)


💡 为什么你刚才的操作很关键？
你手动创建 .ssh 并写入 known_hosts 的动作，相当于给你的电脑和 GitHub 之间建立了一份**“信任协议”**。此前系统报错是因为它不认识 GitHub，为了安全起见拒绝了下载。现在有了这份名单，底层的 Git 模块就不会再拦截 Claude Code 的下载请求了。
甄先生，请执行安装命令。一旦安装成功，我们立刻回到 E 盘，把那 5 个文件夹的视觉化效果彻底跑通。

---
*从 Gemini 导出，2026-05*
