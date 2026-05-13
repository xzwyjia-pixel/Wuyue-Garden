"""
ai_bridge/client.py — 统一AI客户端
支持所有主流AI模型的统一调用接口
"""
import json, time, os, yaml
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_PATH = Path(__file__).parent / "config.yaml"

# ── 统一响应结构 ──
class AIResponse:
    def __init__(self, model: str, content: str, elapsed: float, success: bool, error: str = ""):
        self.model = model
        self.content = content
        self.elapsed = elapsed
        self.success = success
        self.error = error

    def to_dict(self):
        return {
            "model": self.model,
            "content": self.content,
            "elapsed": round(self.elapsed, 2),
            "success": self.success,
            "error": self.error,
        }


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def call_model(model_key: str, prompt: str, system_prompt: str = "") -> AIResponse:
    """统一调用任一AI模型"""
    config = load_config()
    cfg = config.get("models", {}).get(model_key)
    if not cfg or not cfg.get("api_key"):
        return AIResponse(model_key, "", 0, False, f"{model_key} 未配置API Key")

    start = time.time()
    provider = cfg["provider"]

    try:
        if provider == "OpenAI":
            return _call_openai(cfg, prompt, system_prompt)
        elif provider == "Google":
            return _call_gemini(cfg, prompt, system_prompt)
        elif provider == "Anthropic":
            return _call_claude(cfg, prompt, system_prompt)
        elif provider == "火山引擎":
            return _call_openai_compat(cfg, prompt, system_prompt)  # 兼容OpenAI格式
        elif provider == "阿里云":
            return _call_tongyi(cfg, prompt, system_prompt)
        elif provider == "百度":
            return _call_wenxin(cfg, prompt, system_prompt)
        elif provider == "DeepSeek":
            return _call_openai_compat(cfg, prompt, system_prompt)
        else:
            return AIResponse(cfg["name"], "", 0, False, f"未知provider: {provider}")
    except Exception as e:
        elapsed = time.time() - start
        return AIResponse(cfg["name"], "", elapsed, False, str(e))


def _call_openai(cfg: dict, prompt: str, system: str) -> AIResponse:
    import httpx
    headers = {"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"}
    body = {
        "model": cfg["model"],
        "messages": [],
        "max_tokens": cfg.get("max_tokens", 4096),
        "temperature": cfg.get("temperature", 0.7),
    }
    if system:
        body["messages"].append({"role": "system", "content": system})
    body["messages"].append({"role": "user", "content": prompt})

    start = time.time()
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{cfg['api_base']}/chat/completions", headers=headers, json=body)
    elapsed = time.time() - start

    if r.status_code != 200:
        return AIResponse(cfg["name"], "", elapsed, False, f"HTTP {r.status_code}: {r.text[:200]}")

    data = r.json()
    content = data["choices"][0]["message"]["content"]
    return AIResponse(cfg["name"], content, elapsed, True)


def _call_openai_compat(cfg: dict, prompt: str, system: str) -> AIResponse:
    """兼容OpenAI格式的第三方API（豆包/DeepSeek等）"""
    import httpx
    headers = {"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"}
    body = {
        "model": cfg["model"],
        "messages": [],
        "max_tokens": cfg.get("max_tokens", 4096),
        "temperature": cfg.get("temperature", 0.7),
    }
    if system:
        body["messages"].append({"role": "system", "content": system})
    body["messages"].append({"role": "user", "content": prompt})

    start = time.time()
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{cfg['api_base']}/chat/completions", headers=headers, json=body)
    elapsed = time.time() - start

    if r.status_code != 200:
        return AIResponse(cfg["name"], "", elapsed, False, f"HTTP {r.status_code}: {r.text[:200]}")
    content = r.json()["choices"][0]["message"]["content"]
    return AIResponse(cfg["name"], content, elapsed, True)


def _call_gemini(cfg: dict, prompt: str, system: str = "") -> AIResponse:
    import httpx
    url = f"{cfg['api_base']}/models/{cfg['model']}:generateContent?key={cfg['api_key']}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    start = time.time()
    with httpx.Client(timeout=120) as client:
        r = client.post(url, json=body)
    elapsed = time.time() - start

    if r.status_code != 200:
        return AIResponse(cfg["name"], "", elapsed, False, f"HTTP {r.status_code}: {r.text[:200]}")
    candidates = r.json().get("candidates", [])
    if not candidates:
        return AIResponse(cfg["name"], "", elapsed, False, "空响应")
    content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return AIResponse(cfg["name"], content, elapsed, True)


def _call_claude(cfg: dict, prompt: str, system: str = "") -> AIResponse:
    import httpx
    headers = {
        "x-api-key": cfg["api_key"],
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    body = {
        "model": cfg["model"],
        "max_tokens": cfg.get("max_tokens", 4096),
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    start = time.time()
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{cfg['api_base']}/messages", headers=headers, json=body)
    elapsed = time.time() - start

    if r.status_code != 200:
        return AIResponse(cfg["name"], "", elapsed, False, f"HTTP {r.status_code}: {r.text[:200]}")
    content = r.json()["content"][0]["text"]
    return AIResponse(cfg["name"], content, elapsed, True)


def _call_tongyi(cfg: dict, prompt: str, system: str = "") -> AIResponse:
    import httpx
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    body = {
        "model": cfg["model"],
        "input": {"messages": []},
        "parameters": {
            "max_tokens": cfg.get("max_tokens", 4096),
            "temperature": cfg.get("temperature", 0.7),
        },
    }
    if system:
        body["input"]["messages"].append({"role": "system", "content": system})
    body["input"]["messages"].append({"role": "user", "content": prompt})

    start = time.time()
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{cfg['api_base']}/services/aigc/text-generation/generation", headers=headers, json=body)
    elapsed = time.time() - start

    if r.status_code != 200:
        return AIResponse(cfg["name"], "", elapsed, False, f"HTTP {r.status_code}: {r.text[:200]}")
    content = r.json()["output"]["text"]
    return AIResponse(cfg["name"], content, elapsed, True)


def _call_wenxin(cfg: dict, prompt: str, system: str = "") -> AIResponse:
    """文心一言——需要先获取access_token"""
    import httpx

    # 1. 获取access_token
    auth_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={cfg['api_key']}&client_secret={cfg.get('secret_key', '')}"
    start = time.time()
    with httpx.Client(timeout=30) as client:
        auth_r = client.post(auth_url)
    if auth_r.status_code != 200:
        return AIResponse(cfg["name"], "", time.time()-start, False, f"百度Auth失败: {auth_r.text[:200]}")
    access_token = auth_r.json().get("access_token")

    # 2. 调用文心
    url = f"{cfg['api_base']}/chat/completions?access_token={access_token}"
    body = {
        "model": cfg["model"],
        "messages": [],
        "temperature": cfg.get("temperature", 0.7),
    }
    if system:
        body["messages"].append({"role": "system", "content": system})
    body["messages"].append({"role": "user", "content": prompt})

    with httpx.Client(timeout=120) as client:
        r = client.post(url, json=body)
    elapsed = time.time() - start

    if r.status_code != 200:
        return AIResponse(cfg["name"], "", elapsed, False, f"HTTP {r.status_code}: {r.text[:200]}")
    content = r.json().get("result", "")
    return AIResponse(cfg["name"], content, elapsed, True)


def call_all(prompt: str, system_prompt: str = "", models: list = None) -> dict:
    """并行调用所有配置的AI模型"""
    config = load_config()
    if models is None:
        models = list(config.get("models", {}).keys())

    results = {}
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        future_map = {executor.submit(call_model, m, prompt, system_prompt): m for m in models}
        for future in as_completed(future_map):
            model_key = future_map[future]
            try:
                results[model_key] = future.result()
            except Exception as e:
                results[model_key] = AIResponse(model_key, "", 0, False, str(e))
    return results
