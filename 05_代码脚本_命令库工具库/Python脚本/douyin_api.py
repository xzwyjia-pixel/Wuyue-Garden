"""
douyin_api.py — 抖音开放平台 API 接入模块
实时弹幕 + 直播间数据对接
"""
import json, time, hmac, hashlib, requests, threading, logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger("douyin_api")

# ── 配置模板 (需用户填入) ──
CONFIG_TEMPLATE = {
    "client_key": "",       # App ID (从开放平台获取)
    "client_secret": "",    # App Secret (从开放平台获取)
    "webhook_port": 5051,   # 接收抖音事件推送的端口
    "webhook_path": "/dy/callback",
    "ngrok_domain": "",     # 可选: ngrok 公网域名
    "refresh_token": "",
    "access_token": "",
    "token_expires_at": 0,
}

CONFIG_FILE = Path(__file__).parent / "douyin_config.json"


def load_config():
    """Load or create config file"""
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CONFIG_TEMPLATE, f, indent=2, ensure_ascii=False)
        logger.info(f"配置模板已创建: {CONFIG_FILE}")
        return CONFIG_TEMPLATE
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_access_token():
    """获取/刷新 access_token"""
    cfg = load_config()
    if not cfg["client_key"] or not cfg["client_secret"]:
        logger.error("请先在 douyin_config.json 填入 client_key 和 client_secret")
        return None
    now = time.time()
    if cfg["access_token"] and cfg["token_expires_at"] > now + 300:
        return cfg["access_token"]
    # Use refresh_token if available
    if cfg.get("refresh_token"):
        url = "https://open.douyin.com/oauth/refresh_token/"
        params = {
            "client_key": cfg["client_key"],
            "grant_type": "refresh_token",
            "refresh_token": cfg["refresh_token"],
        }
    else:
        # Initial token using client_credential (for server-side)
        url = "https://open.douyin.com/oauth/client_token/"
        params = {
            "client_key": cfg["client_key"],
            "client_secret": cfg["client_secret"],
            "grant_type": "client_credential",
        }
    try:
        resp = requests.post(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data", {}).get("error_code") == 0:
            d = data["data"]
            cfg["access_token"] = d["access_token"]
            cfg["token_expires_at"] = now + d.get("expires_in", 86400)
            if "refresh_token" in d:
                cfg["refresh_token"] = d["refresh_token"]
            save_config(cfg)
            logger.info(f"access_token 已更新, 有效期 {d.get('expires_in', '?')}s")
            return cfg["access_token"]
        else:
            logger.error(f"获取 token 失败: {data}")
            # For client_token, the first time requires manual auth
            if not cfg.get("refresh_token"):
                logger.info("首次使用需完成 OAuth 授权流程，详见 README")
            return None
    except Exception as e:
        logger.error(f"token 请求异常: {e}")
        return None


def verify_webhook_signature(body_bytes, signature, timestamp, nonce):
    """验证抖音事件推送签名"""
    cfg = load_config()
    if not cfg.get("client_secret"):
        return False
    # 抖音签名算法: SHA256(client_secret + timestamp + nonce + body)
    payload = f"{cfg['client_secret']}{timestamp}{nonce}".encode() + body_bytes
    expected = hmac.new(
        cfg["client_secret"].encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def api_get(path, params=None):
    """通用 GET 请求"""
    token = get_access_token()
    if not token:
        return {"error": "no_token", "data": []}
    headers = {"Access-Token": token}
    url = f"https://open.douyin.com{path}"
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def get_live_comments(room_id, cursor=0):
    """获取直播间评论"""
    return api_get("/live/comment/", {
        "room_id": room_id,
        "cursor": cursor,
        "count": 50,
    })


def get_live_room_data(room_id):
    """获取直播间数据 (观看/互动)"""
    return api_get("/live/data/get/", {
        "room_id": room_id,
    })


def get_live_room_info(room_id):
    """获取直播间信息"""
    return api_get("/live/room/info/", {
        "room_id": room_id,
    })


# ── 实时弹幕采集器 ──
class DouyinChatCollector:
    """轮询抖音API获取直播间弹幕, 写入 JSONL"""

    def __init__(self, room_id, out_dir, interval=10):
        self.room_id = room_id
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.interval = interval
        self.cursor = 0
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()
        logger.info(f"弹幕采集器已启动: room={self.room_id}, interval={self.interval}s")

    def stop(self):
        self.running = False

    def _poll(self):
        out_file = self.out_dir / "live_data_douyin.jsonl"
        while self.running:
            try:
                resp = get_live_comments(self.room_id, self.cursor)
                data = resp.get("data", {})
                comments = data.get("list", [])
                if comments:
                    for c in comments:
                        entry = {
                            "timestamp": time.time(),
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "source": "douyin_api",
                            "user": c.get("user", {}).get("nickname", ""),
                            "text": c.get("content", ""),
                            "room_id": self.room_id,
                        }
                        with open(out_file, "a", encoding="utf-8") as f:
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    self.cursor = data.get("cursor", self.cursor)
                    logger.info(f"采集到 {len(comments)} 条新弹幕")
            except Exception as e:
                logger.error(f"弹幕采集错误: {e}")
            time.sleep(self.interval)


# ── Webhook 服务 (接收抖音事件推送) ──
def start_webhook_server(callback_queue):
    """
    启动 Webhook 服务接收抖音实时事件
    需通过 ngrok 暴露公网地址
    """
    from flask import Flask, request, jsonify
    wh_app = Flask(__name__)

    @wh_app.route("/dy/callback", methods=["GET", "POST"])
    def dy_callback():
        if request.method == "GET":
            # 抖音验证 webhook 地址
            challenge = request.args.get("challenge")
            if challenge:
                return challenge, 200, {"Content-Type": "text/plain"}
            return "ok"

        # POST: 事件推送
        body = request.get_data()
        signature = request.headers.get("X-Douyin-Signature", "")
        timestamp = request.headers.get("X-Douyin-Timestamp", "")
        nonce = request.headers.get("X-Douyin-Nonce", "")

        if not verify_webhook_signature(body, signature, timestamp, nonce):
            logger.warning("签名验证失败")
            return "signature_error", 403

        event = request.json or {}
        event_type = event.get("event_type", "")
        logger.info(f"收到事件: {event_type}")
        callback_queue.append(event)
        return "ok"

    cfg = load_config()
    port = cfg.get("webhook_port", 5051)
    wh_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    print("=" * 50)
    print("抖音开放平台接入模块")
    print("=" * 50)
    cfg = load_config()
    if not cfg["client_key"]:
        print(f"\n[配置] 请编辑: {CONFIG_FILE}")
        print("\n需要填写:")
        print("  1. client_key — App ID (开放平台 → 我的应用 → 应用ID)")
        print("  2. client_secret — App Secret")
        print("\n注册地址: https://open.douyin.com")
        print("\n完成后重新运行本脚本获取 token 测试连接")
    else:
        token = get_access_token()
        if token:
            print(f"✅ 连接成功! access_token 已获取")
            print(f"   前20位: {token[:20]}...")
        else:
            print("❌ 获取 token 失败, 检查配置")
