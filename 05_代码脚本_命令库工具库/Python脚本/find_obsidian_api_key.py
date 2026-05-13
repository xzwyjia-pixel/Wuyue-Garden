"""
Scan all Obsidian vaults → find obsidian-local-rest-api data.json → extract apiKey.
"""

import json
import os
from pathlib import Path


def get_vaults_from_config():
    """Read Obsidian vault list from its config file."""
    config_path = os.path.expandvars(
        r"%APPDATA%\obsidian\obsidian.json"
    )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        vaults = []
        for entry in config.get("vaults", {}).values():
            path = entry.get("path")
            if path and os.path.isdir(path):
                vaults.append(path)
        return vaults
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"[!] Cannot read Obsidian config: {e}")
        return []


def find_api_key(vault_path):
    """Check if vault has the plugin config; return apiKey if found."""
    data_file = (
        Path(vault_path)
        / ".obsidian"
        / "plugins"
        / "obsidian-local-rest-api"
        / "data.json"
    )
    if not data_file.exists():
        return None

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("apiKey")
    except (json.JSONDecodeError, KeyError, OSError) as e:
        print(f"[!] Error reading {data_file}: {e}")
        return None


def main():
    vaults = get_vaults_from_config()

    if not vaults:
        # Fallback: search common locations
        fallback_dirs = [
            os.path.expandvars(r"%USERPROFILE%\Documents"),
            os.path.expandvars(r"%USERPROFILE%\Desktop"),
            os.path.expandvars(r"%HOMEDRIVE%%HOMEPATH%"),
        ]
        print("[*] No vaults found in Obsidian config. Searching common locations...")
        for d in fallback_dirs:
            p = Path(d)
            if p.exists():
                vaults.extend(
                    str(item)
                    for item in p.iterdir()
                    if item.is_dir()
                    and (item / ".obsidian").is_dir()
                )

    if not vaults:
        print("[-] No Obsidian vaults found.")
        return

    print(f"[*] Found {len(vaults)} vault(s). Scanning for apiKey...\n")

    found = False
    for v in vaults:
        key = find_api_key(v)
        if key:
            print(f"  Vault: {v}")
            print(f"  apiKey: {key}")
            print()
            found = True

    if not found:
        print("[-] No vault has obsidian-local-rest-api plugin installed.")
    else:
        print("[+] Done. Copy the apiKey above into your browser extension.")


if __name__ == "__main__":
    main()
