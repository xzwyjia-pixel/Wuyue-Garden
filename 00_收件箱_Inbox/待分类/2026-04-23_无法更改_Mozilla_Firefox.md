---
title: 无法更改
source: gemini
date: 2026-04-23
category: 项目管理
tags: [gemini, 项目管理]
---

## 无法更改

从您第二张截图（about:policies）可以看到，问题非常明确：火狐浏览器被注入了**“企业策略”（Enterprise Policies）**。
在“策略值”一栏清楚地显示了 Homepage 被设置为 360 导航，且 Locked 状态为 true。这就是为什么您在常规设置里无法更改的原因——系统层面的策略强制锁定了它。
这种情况通常是某些安装包或第三方优化工具修改了注册表。请按照以下步骤手动解锁：
第一步：删除火狐策略配置文件

彻底关闭火狐浏览器。
打开资源管理器（我的电脑），进入火狐的安装目录。通常路径是：

C:\Program Files\Mozilla Firefox
或者 C:\Program Files (x86)\Mozilla Firefox


查找一个名为 distribution 的文件夹。
如果有这个文件夹，请点进去，删除里面的 policies.json 文件。

第二步：清理注册表锁定（关键步骤）
如果第一步没解决，说明策略写进了 Windows 注册表。

按下快捷键 Win + R，输入 regedit 并回车。
在左侧导航栏中依次展开以下路径：
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Mozilla\Firefox
在右侧窗口中，检查是否存在 Homepage 项。
操作： 直接右键删除 Mozilla 文件夹（或者它下面的 Firefox 文件夹）。
同样地，检查这个路径（如果有也删除）：
HKEY_CURRENT_USER\SOFTWARE\Policies\Mozilla\Firefox

第三步：重启火狐

完成上述操作后，重新打开火狐浏览器。
现在进入“设置” -> “主页”，您应该发现那个 360 的链接变灰可以修改，或者已经恢复成默认状态了。


温馨提示：
这种通过“企业策略”锁定的手段比较底层。鉴于您之前提到在处理一些项目（如“规则情报局”），这类深度定制的系统环境可能是在安装某些“国产化”适配软件或特定的系统镜像时带进来的。如果以后还遇到类似点击图标就跳转的情况，基本都可以通过检查 about:policies 来确认是否被“策略锁定”了。
搞定了吗？如果没有恢复，我再带您看下快捷方式的底层指向。

---
*从 Gemini 导出，2026-04*
