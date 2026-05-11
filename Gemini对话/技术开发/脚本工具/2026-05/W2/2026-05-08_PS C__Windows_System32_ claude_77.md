---
title: PS C:\Windows\System32> claude
source: gemini
date: 2026-05-08
category: 技术开发
subcategory: 脚本工具
old_category: 编程开发
tags: [gemini, 技术开发, 脚本工具]
---

## PS C:\Windows\System32> claude

## PS C:\Windows\System32> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> 你好
  ⎿  Retrying in 18s · attempt 7/10

✽ Ideating… (57s)
  ⎿  Tip: Use /btw to ask a quick side question without interrupting Claude's current work

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt
这个问题如何解决，我已经困扰了一天了。我的token没有消耗。账户上还有钱。

这看起来是 Claude Code 在尝试与 Anthropic 的 API 建立连接时卡住了。既然你的账户余额充足且没有 Token 消耗，问题通常不在账号权限，而是在本地网络环境或程序运行权限上。
以下是几个排查和解决建议，希望能帮你结束这一天的困扰：
1. 检查网络代理 (最常见原因)
如果你在受限网络环境下（如在中国境内），命令行工具（CLI）往往不会自动继承系统的代理设置。

确认代理： 确保你的代理软件开启了“全局模式”或者“增强模式”。
手动配置： 在运行 claude 之前，尝试在 PowerShell 中手动设置环境变量：
$env:HTTP_PROXY="http://127.0.0.1:你的端口号"
$env:HTTPS_PROXY="http://127.0.0.1:你的端口号"

注：端口号通常是 7890、7897 或 1080，视你的代理软件而定。

2. 避免在 System32 目录下运行
看到你的路径是 C:\Windows\System32，这通常不是一个运行开发工具的好地方。

权限限制： System32 是系统核心目录，Windows 可能会限制程序的写操作（比如 Claude Code 无法在当前目录创建缓存或临时文件）。
解决： 切换到一个普通的文件夹（例如 D:\Projects 或你的用户文档目录）再尝试启动：

    cd C:\Users\你的用户名\Desktop
    claude
    ```

### 3. 检查 API Key 环境变量
虽然报错是 Retry，但如果 API Key 没被正确读取，有时也会导致异常挂起。
*   检查你是否正确配置了环境变量 `ANTHROPIC_API_KEY`。
*   或者在启动时尝试重新登录/初始化：
    ```bash
    claude --auth
    ```

### 4. 强制更新或重装
Claude Code 更新频率很快，版本冲突有时会导致“Ideating”无限循环。
*   尝试更新：
    ```bash
    npm install -g @anthropic-ai/claude-code@latest
    ```
*   清理缓存：有时候本地的认证缓存坏了，可以尝试删除用户目录下的 `.claude-code` 文件夹（通常在 `C:\Users\你的用户名\.claude-code`）。

### 5. 查看详细日志
如果上述方法都不行，你可以查看详细日志来定位到底卡在哪一步了：
*   在 `C:\Users\你的用户名\.claude-code\logs` 路径下找找最新的 `.log` 文件。
*   如果日志显示 `ETIMEDOUT` 或 `ECONNRESET`，那就百分之百是网络连接被拦截了。

**小建议：**
如果是因为“高强度思考”（High Effort）模式导致 API 响应过慢，你可以尝试先切换回普通模式启动，看看能否通畅：
`claude --model claude-3-5-sonnet` (或者你当前版本支持的其他基准模型)。

你现在使用的是哪个代理工具？如果手动设置了 `$env:HTTP_PROXY` 后依然报错，请告诉我报错代码的具体变化。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / 脚本工具 · 2026-05-08*
