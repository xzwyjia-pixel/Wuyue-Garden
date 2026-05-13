---
title:  Windows 的自动化提取 Key 的脚本
source: gemini
date: 2026-05-10
category: 编程开发
tags: [gemini, 编程开发]
---

##  Windows 的自动化提取 Key 的脚本

这是一个针对 Windows 环境的 Python 自动化方案。该脚本的作用是自动定位你的 Obsidian Vault 配置文件，读取 Local REST API 插件的设置，并直接提取出那串复杂的 API Key。
📋 前置条件

你已经在 Obsidian 中安装并启用了 Local REST API 插件。
你的电脑安装了 Python（如果没有安装，手动复制仍是最快的方法）。


🐍 自动化提取脚本
你可以将以下代码保存为 get_obsidian_key.py 并运行：
import os
import json
import pathlib

def get_obsidian_api_key():
    # 1. 定位 Obsidian 在 Windows 上的配置文件根目录
    app_data = os.getenv('APPDATA')
    obsidian_config_path = os.path.join(app_data, 'obsidian', 'obsidian.json')
    
    if not os.path.exists(obsidian_config_path):
        return "❌ 未找到 Obsidian 配置文件，请确认 Obsidian 已安装。"

    try:
        with open(obsidian_config_path, 'r', encoding='utf-8') as f:
            vaults = json.load(f).get('vaults', {})
        
        if not vaults:
            return "❌ 未发现任何已注册的 Vault。"

        # 遍历所有 Vault，寻找安装了 Local REST API 的配置
        for vault_id, vault_info in vaults.items():
            vault_path = vault_info.get('path')
            # 插件配置文件通常存储在 .obsidian/plugins/obsidian-local-rest-api/data.json
            api_config_path = pathlib.Path(vault_path) / '.obsidian' / 'plugins' / 'obsidian-local-rest-api' / 'data.json'
            
            if api_config_path.exists():
                with open(api_config_path, 'r', encoding='utf-8') as af:
                    api_data = json.load(af)
                    api_key = api_data.get('apiKey')
                    if api_key:
                        return f"✅ 成功提取 API Key!\n\nVault 路径: {vault_path}\nAPI Key: {api_key}\n\n请复制上面的 Key 并粘贴到浏览器插件设置中。"
        
        return "❌ 找到了 Vault，但未发现 Local REST API 插件的配置数据。请确保该插件已在 Obsidian 中启用并生成了 Key。"

    except Exception as e:
        return f"❌ 运行出错: {str(e)}"

if __name__ == "__main__":
    print("正在搜索 Obsidian 本地 API 密钥...")
    result = get_obsidian_api_key()
    print(result)
    input("\n按下回车键退出...")


💡 为什么这还不是“全自动”？
即便脚本帮你拿到了 Key，你仍然需要手动粘贴到浏览器一次。原因如下：

浏览器安全沙箱：Windows 脚本无法直接修改浏览器插件内部的私有数据库（IndexedDB 或 LocalStorage）。
一次性握手：这种手动操作更像是一种“配对”。一旦你粘贴进去并保存，只要你不清除浏览器缓存或重置插件，这种连接就是永久生效的。

🚀 进阶建议：彻底告别粘贴
既然你对自动化感兴趣，且已经在使用 Claude，我强烈建议你尝试配置 MCP (Model Context Protocol)。
通过 MCP，Claude 可以直接调用你本地的 Python 环境。配置好后，你可以直接给 Claude 下达指令：

“把这段对话存入我的 Obsidian。”

它会绕过浏览器插件，通过本地协议直接把文件写入你的库。这才是真正的“自动完成”。如果你想尝试这个方案，我可以为你提供具体的 MCP 配置文件示例。

---
*从 Gemini 导出，2026-05*
