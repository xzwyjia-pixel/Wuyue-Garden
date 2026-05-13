"""
save_obsidian.py — Save content to Obsidian vault via Local REST API
Usage: python save_obsidian.py --path <vault/path.md> < content.txt
"""
import sys, json, requests
from urllib.parse import quote

BASE = 'http://127.0.0.1:27123'
KEY = '8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c'
HEADERS = {'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}

if len(sys.argv) < 2:
    print("Usage: python save_obsidian.py <vault/path.md>")
    sys.exit(1)

path = sys.argv[1]
content = sys.stdin.read()

url = f'{BASE}/vault/{quote(path, safe="/")}'
resp = requests.put(url, headers=HEADERS, json={'content': content})

if resp.status_code in (200, 201, 204):
    print(f"OK: {path}")
else:
    print(f"Error {resp.status_code}: {resp.text}")
    sys.exit(1)
