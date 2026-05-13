"""
feishu_bot/client.py — 飞书API客户端
发送消息、创建群组、操作多维表格
"""
import json, time, httpx
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).parent.parent / "ai_bridge" / "config.yaml"


class FeishuClient:
    """飞书开放平台API客户端"""

    def __init__(self, app_id: str = "", app_secret: str = ""):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token = None
        self._token_expires = 0

    def _load_config(self):
        if not self.app_id and CONFIG_PATH.exists():
            import yaml
            cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
            fc = cfg.get("feishu", {})
            self.app_id = fc.get("app_id", self.app_id)
            self.app_secret = fc.get("app_secret", self.app_secret)

    def _get_token(self) -> str:
        """获取tenant_access_token"""
        if time.time() < self._token_expires:
            return self._token

        self._load_config()
        if not self.app_id or not self.app_secret:
            raise ValueError("飞书App ID或App Secret未配置")

        with httpx.Client(timeout=30) as client:
            r = client.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret},
            )
        if r.status_code != 200:
            raise Exception(f"获取token失败: {r.text}")

        data = r.json()
        self._token = data["tenant_access_token"]
        self._token_expires = time.time() + data.get("expire", 7200) - 300
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    # ── 消息发送 ──
    def send_text(self, chat_id: str, text: str) -> dict:
        """发送文本消息到群聊"""
        body = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(
                "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
                headers=self._headers(), json=body,
            )
        return r.json()

    def send_markdown(self, chat_id: str, title: str, content: str) -> dict:
        """发送富文本消息"""
        body = {
            "receive_id": chat_id,
            "msg_type": "post",
            "content": json.dumps({
                "zh_cn": {
                    "title": title,
                    "content": [[{"tag": "text", "text": content}]],
                }
            }, ensure_ascii=False),
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(
                "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
                headers=self._headers(), json=body,
            )
        return r.json()

    def send_card(self, chat_id: str, title: str, content: str, btn_url: str = "") -> dict:
        """发送消息卡片（交互式）"""
        body = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "config": {"wide_screen_mode": True},
                "header": {"title": {"tag": "plain_text", "content": title}, "template": "blue"},
                "elements": [
                    {"tag": "markdown", "content": content},
                    *([{
                        "tag": "action",
                        "actions": [{
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "查看详情"},
                            "url": btn_url,
                            "type": "default",
                        }],
                    }] if btn_url else []),
                ],
            }, ensure_ascii=False),
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(
                "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
                headers=self._headers(), json=body,
            )
        return r.json()

    # ── 群组管理 ──
    def create_group(self, name: str, description: str = "") -> dict:
        """创建群聊"""
        body = {
            "name": name,
            "description": description or name,
            "chat_mode": "group",
            "chat_type": "public",
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(
                "https://open.feishu.cn/open-apis/im/v1/chats",
                headers=self._headers(), json=body,
            )
        return r.json()

    def add_member(self, chat_id: str, member_id: str, member_type: str = "open_id") -> dict:
        """添加成员到群聊"""
        body = {"id_list": [member_id]}
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members?member_id_type={member_type}",
                headers=self._headers(), json=body,
            )
        return r.json()

    # ── 多维表格 ──
    def create_bitable(self, app_token: str, name: str, fields: list) -> dict:
        """在多维表格中创建数据表"""
        body = {"name": name, "fields": fields}
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables",
                headers=self._headers(), json=body,
            )
        return r.json()

    def add_record(self, app_token: str, table_id: str, fields: dict) -> dict:
        """添加记录到多维表格"""
        body = {"fields": fields}
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records",
                headers=self._headers(), json=body,
            )
        return r.json()

    # ── 文件上传 ──
    def upload_file(self, file_path: str, file_type: str = "stream") -> dict:
        """上传文件到飞书"""
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/octet-stream")}
            data = {"file_name": Path(file_path).name, "file_type": file_type}
            with httpx.Client(timeout=60) as client:
                r = client.post(
                    "https://open.feishu.cn/open-apis/im/v1/files",
                    headers={"Authorization": f"Bearer {self._get_token()}"},
                    data=data, files=files,
                )
        return r.json()
