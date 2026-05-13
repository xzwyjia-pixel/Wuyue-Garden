#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — Google Drive 云端同步器
===================================================
功能：
  - 创建日期文件夹：Sentinel_Audit_YYYY-MM-DD/
  - 上传 data/ 下最新 .xlsx 模板和 .txt 剪映草稿
  - 上传 notes/ 下最新 Markdown 报告
  - 失败时转存至 data/pending_sync/ 待重试

用法：
  python google_drive_sync.py
  python google_drive_sync.py --dry-run    # 预览不上传
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_NOTES_DIR = Path(__file__).resolve().parent.parent.parent / "notes"
_PENDING_DIR = _DATA_DIR / "pending_sync"
_STATE_PATH = _DATA_DIR / "pipeline_state.json"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ──────────────────────────────────────────────
# 文件收集
# ──────────────────────────────────────────────

def _latest(pattern: str, directory: Path) -> Optional[Path]:
    files = sorted(directory.glob(pattern), reverse=True)
    return files[0] if files else None


def _collect_artifacts() -> List[Path]:
    """收集最新分发素材"""
    artifacts = []

    xlsx = _latest("export_video_*.xlsx", _DATA_DIR)
    txt = _latest("export_jianying_*.txt", _DATA_DIR)
    md = _latest("*规则演变报告*.md", _NOTES_DIR)

    if xlsx:
        artifacts.append(xlsx)
    if txt:
        artifacts.append(txt)
    if md:
        artifacts.append(md)

    return artifacts


# ──────────────────────────────────────────────
# Google Drive 上传
# ──────────────────────────────────────────────

def _get_drive_service():
    """初始化 Google Drive API 服务"""
    import google.auth
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds_path = _DATA_DIR / "gdrive_credentials.json"
    token_path = _DATA_DIR / "gdrive_token.json"
    scopes = ["https://www.googleapis.com/auth/drive.file"]

    if not creds_path.exists():
        print("[WARN] 未找到 gdrive_credentials.json")
        print("[HINT] 下载 Google Cloud OAuth 2.0 客户端 JSON 并保存到:")
        print(f"       {creds_path}")
        return None

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("drive", "v3", credentials=creds)


def _ensure_folder(service, name: str, parent_id: Optional[str] = None) -> str:
    """在 Google Drive 中创建/获取文件夹"""
    from googleapiclient.errors import HttpError

    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    try:
        results = service.files().list(q=query, spaces="drive", pageSize=1).execute()
        items = results.get("files", [])
        if items:
            return items[0]["id"]
    except Exception:
        pass

    body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        body["parents"] = [parent_id]
    folder = service.files().create(body=body, fields="id").execute()
    return folder["id"]


def _upload_file(service, local_path: Path, folder_id: str, dry_run: bool = False) -> bool:
    """上传单个文件到指定文件夹"""
    from googleapiclient.http import MediaFileUpload

    if dry_run:
        print(f"  [DRYRUN] 上传 {local_path.name} → folder {folder_id}")
        return True

    try:
        media = MediaFileUpload(str(local_path), resumable=True)
        body = {"name": local_path.name, "parents": [folder_id]}
        service.files().create(body=body, media_body=media, fields="id").execute()
        print(f"  [UPLOAD] {local_path.name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {local_path.name}: {e}")
        return False


# ──────────────────────────────────────────────
# 本地待同步区（离线回退）
# ──────────────────────────────────────────────

def _stash_to_pending(files: List[Path]):
    """上传失败时转存到本地 pending 目录"""
    _PENDING_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        dest = _PENDING_DIR / f.name
        shutil.copy2(f, dest)
        print(f"  [STASH] → {dest}")
    print(f"  [NOTE] 待同步文件在 {_PENDING_DIR}，可手动上传")


def _pending_retry(service, dry_run: bool = False) -> int:
    """尝试重传待同步区文件"""
    if not _PENDING_DIR.exists():
        return 0
    files = list(_PENDING_DIR.iterdir())
    if not files:
        return 0
    print(f"\n  [RETRY] {len(files)} 个待同步文件...")
    success = 0
    # 获取或创建 pending 文件夹
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_id = _ensure_folder(service, f"pending_retry_{ts}")
    for f in files:
        if f.is_file():
            ok = _upload_file(service, f, folder_id, dry_run)
            if ok:
                f.unlink()
                success += 1
    return success


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def sync(dry_run: bool = False) -> dict:
    """云端同步主入口"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 云端同步")
    print("=" * 48)

    # 收集素材
    artifacts = _collect_artifacts()
    if not artifacts:
        print("[SKIP] 无待同步素材")
        return {"status": "skipped", "files": 0}

    print(f"\n[ARTIFACTS] {len(artifacts)} 个文件:")
    for f in artifacts:
        print(f"  {f.parent.name}/{f.name}")

    # 初始化 Drive
    service = _get_drive_service()
    if service is None:
        print("[OFFLINE] Google Drive 不可用，转存本地")
        _stash_to_pending(artifacts)
        return {"status": "offline", "files": len(artifacts)}

    # 创建日期文件夹
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"Sentinel_Audit_{date_str}"

    try:
        folder_id = _ensure_folder(service, folder_name)
        print(f"\n[FOLDER] {folder_name}")
    except Exception as e:
        print(f"[FAIL] 创建文件夹失败: {e}")
        _stash_to_pending(artifacts)
        return {"status": "failed", "error": str(e)}

    # 上传
    success_count = 0
    fail_count = 0
    for f in artifacts:
        ok = _upload_file(service, f, folder_id, dry_run)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    # 失败文件转存
    failed_files = [f for f in artifacts if f not in []]  # 暂不支持精准追踪
    if fail_count > 0:
        print(f"\n[STASH] {fail_count} 个文件上传失败，转存本地")
        for f in artifacts:
            dest = _PENDING_DIR / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            print(f"  → {dest}")

    # 尝试重传待同步区
    retry_count = _pending_retry(service, dry_run)

    status = "completed" if fail_count == 0 else "partial"
    result = {
        "status": status,
        "dry_run": dry_run,
        "folder": folder_name,
        "files_total": len(artifacts),
        "files_uploaded": success_count,
        "files_failed": fail_count,
        "pending_retried": retry_count,
    }

    print(f"\n[DONE] {success_count}/{len(artifacts)} 上传成功"
          f"{' (dry-run)' if dry_run else ''}"
          f"{f', {retry_count} 重传' if retry_count else ''}")

    # 写入 pipeline_state
    if _STATE_PATH.exists():
        state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    else:
        state = {}
    state["gdrive_sync"] = result
    _STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Google Drive 云端同步")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不上传")
    args = parser.parse_args()
    sync(dry_run=args.dry_run)
