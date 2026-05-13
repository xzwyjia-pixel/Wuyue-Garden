"""
ai_bridge/obsidian_sync.py — Obsidian自动保存
研讨报告自动存入Obsidian，支持MD/Excel/Excalidraw多格式
"""
import json, csv, os, yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import httpx
except ImportError:
    httpx = None

CONFIG_PATH = Path(__file__).parent / "config.yaml"
DEFAULT_VAULT = "E:/MyCodeProjects"
DEFAULT_DIR = "AI研讨报告"


class ObsidianSync:
    """Obsidian自动同步"""

    def __init__(self, vault_path: str = "", api_url: str = "", api_key: str = ""):
        self.vault_path = Path(vault_path or DEFAULT_VAULT)
        self.api_url = api_url
        self.api_key = api_key
        self._load_config()

    def _load_config(self):
        if not self.api_url and CONFIG_PATH.exists():
            cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
            oc = cfg.get("obsidian", {})
            self.api_url = oc.get("api_url", self.api_url)
            self.api_key = oc.get("api_key", self.api_key)
            self.vault_path = Path(oc.get("vault_path", DEFAULT_VAULT))
        self.output_dir = self.vault_path / DEFAULT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Markdown保存 ──
    def save_markdown(self, title: str, content: str, tags: list = None) -> Path:
        """保存MD格式报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{title[:40].replace(' ', '_')}_{timestamp}.md"
        fpath = self.output_dir / fname

        header = "---\n"
        header += f"created: {datetime.now().isoformat()}\n"
        if tags:
            header += f"tags: {json.dumps(tags, ensure_ascii=False)}\n"
        header += "---\n\n"

        fpath.write_text(header + content, encoding="utf-8")
        print(f"[MD] 已保存: {fpath}")

        # 同步到Obsidian API
        self._obsidian_api_sync(str(fpath), fname)
        return fpath

    # ── Excel/CSV保存 ──
    def save_csv(self, title: str, data: list[dict]) -> Path:
        """保存CSV格式数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{title[:30].replace(' ', '_')}_{timestamp}.csv"
        fpath = self.output_dir / fname

        if not data:
            fpath.write_text("", encoding="utf-8-sig")
            return fpath

        with open(fpath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        print(f"[CSV] 已保存: {fpath}")
        return fpath

    # ── JSON保存 ──
    def save_json(self, title: str, data: dict) -> Path:
        """保存JSON格式原始数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{title[:30].replace(' ', '_')}_{timestamp}.json"
        fpath = self.output_dir / fname
        fpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[JSON] 已保存: {fpath}")
        return fpath

    # ── Excalidraw保存 ──
    def save_excalidraw(self, title: str, elements: list, description: str = "") -> Path:
        """保存Excalidraw可视化格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{title[:30].replace(' ', '_')}_{timestamp}.excalidraw.md"
        fpath = self.output_dir / fname

        content = f"""---

excalidraw-plugin: parsed
tags: [AI研讨, 可视化]

---
==⚠ Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu. ⚠==

# {title}

{description}

```json
{{
  "type": "excalidraw",
  "version": 2,
  "source": "AIBridge",
  "elements": {json.dumps(elements, ensure_ascii=False)},
  "appState": {{"viewBackgroundColor": "#ffffff"}}
}}
```
"""
        fpath.write_text(content, encoding="utf-8")
        print(f"[EXCALIDRAW] 已保存: {fpath}")
        return fpath

    # ── Obsidian Local REST API同步 ──
    def _obsidian_api_sync(self, file_path: str, filename: str):
        """通过Obsidian Local REST API将文件写入vault"""
        if not self.api_url or not httpx:
            return

        try:
            file_content = Path(file_path).read_text(encoding="utf-8")
            vault_relative = str(Path(file_path).relative_to(self.vault_path).as_posix())

            with httpx.Client(timeout=10) as client:
                r = client.put(
                    f"{self.api_url}/vault/{vault_relative}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "text/markdown; charset=utf-8",
                    },
                    content=file_content.encode("utf-8"),
                )
            if r.status_code in (200, 201):
                print(f"[OBSIDIAN-API] 同步成功: {vault_relative}")
            else:
                print(f"[OBSIDIAN-API] 同步失败 HTTP {r.status_code}")
        except Exception as e:
            print(f"[OBSIDIAN-API] 同步异常: {e}")

    # ── 一键保存所有格式 ──
    def save_all(self, title: str, md_content: str, csv_data: list[dict] = None,
                 json_data: dict = None, excalidraw_elements: list = None,
                 tags: list = None) -> dict:
        """一键保存多格式输出"""
        result = {"md": str(self.save_markdown(title, md_content, tags))}

        if csv_data:
            result["csv"] = str(self.save_csv(title, csv_data))
        if json_data:
            result["json"] = str(self.save_json(title, json_data))
        if excalidraw_elements:
            result["excalidraw"] = str(self.save_excalidraw(title, excalidraw_elements))

        return result
