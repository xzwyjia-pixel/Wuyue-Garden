"""
feishu_bot/server.py — 飞书Webhook接收服务器
接收飞书事件回调，转发到AI分析引擎
"""
import json, hashlib, hmac, logging
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
log = logging.getLogger("feishu_bot")


class FeishuWebhookHandler(BaseHTTPRequestHandler):
    """飞书事件回调处理器"""

    # 可外部注入
    on_message = None  # callback: (message_text, sender, chat_id) -> str
    verify_token = ""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body) if body else {}

        log.info(f"收到飞书回调: {self.path}")

        # ── 地址验证 ──
        if data.get("type") == "url_verification":
            self._respond({"challenge": data.get("challenge", "")})
            return

        # ── 事件回调 ──
        event = data.get("event", {})
        event_type = event.get("type", "")

        if event_type == "im.message.receive_v1":
            self._handle_message(event)
        elif event_type == "event_callback":
            self._handle_message(event)
        else:
            log.info(f"未处理的事件类型: {event_type}")
            self._respond({"code": 0})

    def _handle_message(self, event):
        """处理收到的消息"""
        message = event.get("message", {})
        sender = event.get("sender", {}).get("sender_id", {}).get("open_id", "unknown")
        chat_id = message.get("chat_id", "")
        msg_type = message.get("msg_type", "")
        content_raw = message.get("content", "{}")

        try:
            content = json.loads(content_raw) if isinstance(content_raw, str) else content_raw
            text = content.get("text", "") if msg_type == "text" else content_raw
        except json.JSONDecodeError:
            text = content_raw

        log.info(f"消息来自 {sender}: {text[:50]}...")

        # 调用外部处理函数
        reply = ""
        if self.on_message:
            try:
                reply = self.on_message(text, sender, chat_id)
            except Exception as e:
                log.error(f"处理消息异常: {e}")
                reply = f"处理出错: {e}"

        self._respond({"code": 0, "reply": reply})

    def _respond(self, data: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        log.info(f"HTTP: {args}")


def start_server(port: int = 8080, on_message=None, verify_token: str = ""):
    """启动飞书Webhook服务器"""
    FeishuWebhookHandler.on_message = on_message
    FeishuWebhookHandler.verify_token = verify_token

    server = HTTPServer(("0.0.0.0", port), FeishuWebhookHandler)
    log.info(f"飞书Webhook服务器启动: http://0.0.0.0:{port}")
    log.info("按 Ctrl+C 停止")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("服务器停止")
        server.server_close()
