"""
Obsidian Karpathy Automation Agent
===================================
Reads raw-tagged notes via Local REST API.
Extracts core concepts. Tracks occurrences.
On 2nd occurrence: creates wiki/概念/{concept}.md
On co-occurrence: creates wiki/对比/{A}_vs_{B}.md

Usage:
  python obsidian_karpathy_agent.py scan    # one-shot scan
  python obsidian_karpathy_agent.py watch   # continuous polling
  python obsidian_karpathy_agent.py status  # show tracker stats
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
TRACKER_FILE = SCRIPT_DIR / "concept_tracker.json"

# ── Helpers ──────────────────────────────────────────────────────────

def load_config():
    if not CONFIG_FILE.exists():
        print(f"[ERROR] config.json not found. Copy config.example.json → config.json and fill in your API key.")
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_tracker():
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"concepts": {}, "processed_notes": []}


def save_tracker(tracker):
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)


def api_request(config, method, path, data=None):
    # URL-encode each path segment to handle Chinese characters
    segments = path.strip("/").split("/")
    encoded_path = "/".join(urllib.parse.quote(s, safe="") for s in segments)
    url = f"{config['obsidian_api']['base_url']}/vault/{encoded_path}"
    headers = {
        "Authorization": f"Bearer {config['obsidian_api']['api_key']}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return body if resp.status >= 200 and resp.status < 300 else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"  [API ERROR] {e.code} {e.reason} for {method} {url}")
        print(f"    {detail[:200]}")
        return None
    except urllib.error.URLError as e:
        print(f"  [API ERROR] Is Obsidian running? {e.reason}")
        return None


# ── Concept Extraction ──────────────────────────────────────────────

# Stopwords that should not become concepts
STOPWORDS = {
    "笔记", "分析", "报告", "总结", "记录", "整理",
    "note", "notes", "analysis", "report", "summary",
    "内容", "方法", "问题", "方案", "系统", "项目",
}


def extract_concepts(text, filename):
    """Extract core concepts from note content.

    Priority sources (Karpathy: atomic concept = one note):
    1. Wikilinks [[...]] in content
    2. YAML frontmatter 'aliases' field
    3. Markdown headings (## or ###)
    4. Bolded phrases
    """
    concepts = set()

    # 1. Wikilinks
    wikilinks = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text)
    for link in wikilinks:
        link = link.strip()
        if link and len(link) <= 50:
            concepts.add(link)

    # 2. Aliases from frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        alias_match = re.search(r'aliases:\s*\[([^\]]+)\]', fm_text)
        if alias_match:
            for alias in alias_match.group(1).split(","):
                alias = alias.strip().strip("\"'")
                if alias and alias not in STOPWORDS:
                    concepts.add(alias)

    # 3. H2/H3 headings
    headings = re.findall(r'^#{2,3}\s+(.+)', text, re.MULTILINE)
    for h in headings:
        h = h.strip()
        if h and h not in STOPWORDS and len(h) <= 40:
            concepts.add(h)

    # 4. Bold phrases (multi-word)
    bolds = re.findall(r'\*\*(.+?)\*\*', text)
    for b in bolds:
        b = b.strip()
        if b and len(b) >= 4 and len(b) <= 40 and b not in STOPWORDS:
            concepts.add(b)

    # Remove filename itself (not a cross-reference)
    name_stem = filename.replace(".md", "").replace("_", "")
    concepts = {c for c in concepts if c.replace(" ", "") != name_stem}

    return concepts


def get_note_content(config, path):
    """Fetch note content via REST API GET. Returns markdown string."""
    body = api_request(config, "GET", path)
    if not body:
        return None
    try:
        parsed = json.loads(body)
        return parsed.get("content", "")
    except (json.JSONDecodeError, TypeError):
        return body


def list_notes(config, folder="Inbox"):
    """List all note files in a folder via REST API."""
    # REST API doesn't have a directory listing endpoint.
    # We use a known list or a heuristic: list known files from config.
    # Alternative: we accept the note path as input or scan via the filesystem.
    body = api_request(config, "GET", folder)
    if body:
        return body.split("\n")
    return []


def get_note_tags(config, path):
    """Try to read tags from a note's frontmatter."""
    content = get_note_content(config, path)
    if not content:
        return []
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return []
    tags_match = re.search(r'tags:\s*\[([^\]]+)\]', fm_match.group(1))
    if not tags_match:
        return []
    return [t.strip().strip("\"'") for t in tags_match.group(1).split(",")]


# ── Wiki Note Generation ────────────────────────────────────────────

def sanitize_name(name):
    """Sanitize concept name for use as filename. Replace / → _."""
    return name.replace("/", "_").replace("\\", "_")


def generate_concept_note(concept, source_notes, config):
    """Generate content for a wiki/概念/{concept}.md note."""
    sources_bullets = "\n".join(f"- [[{s}]]" for s in source_notes)
    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""---
created: {date_str}
aliases: ["{concept}"]
tags: [concept]
---

# {concept}

## 出现来源

{sources_bullets}

## 概念描述

<!-- 概念第二次出现，自动创建。请补充核心描述 -->

## 关联概念

<!-- 自动检测到的关联 -->
"""


def generate_contrast_note(concept_a, concept_b, source_notes, config):
    """Generate content for a wiki/对比/{A}_vs_{B}.md note."""
    sources_bullets = "\n".join(f"- [[{s}]]" for s in source_notes)
    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""---
created: {date_str}
aliases: ["{concept_a} vs {concept_b}"]
tags: [contrast, concept]
---

# {concept_a} vs {concept_b}

## 同时出现于

{sources_bullets}

## 对比维度

<!-- 请在此处填写对比维度 -->
-
"""


def create_note_via_api(config, path, content):
    """Create a note via REST API PUT."""
    data = json.dumps({"content": content}).encode("utf-8")
    print(f"  [PUT] {path} ({len(data)} bytes)")
    result = api_request(config, "PUT", path, data)
    if result is not None:
        print(f"  [CREATED] {path}")
        return True
    print(f"  [FAILED] {path}")
    return False


# ── Core Logic ──────────────────────────────────────────────────────

def scan_raw_notes(config, tracker):
    """Scan all notes tagged 'raw', extract concepts, update tracker."""
    tag = config["tag_to_watch"]
    inbox_path = config["inbox_path"]

    # List files in Inbox via filesystem (REST API lacks directory listing)
    inbox_dir = SCRIPT_DIR.parent / inbox_path
    if not inbox_dir.exists():
        print(f"[WARN] Inbox folder not found: {inbox_dir}")
        return

    raw_files = []
    for f in sorted(inbox_dir.glob("*.md")):
        if f.name in tracker.get("processed_notes", []):
            continue
        # Check tags via REST API
        api_path = f"{inbox_path}/{f.name}"
        tags = get_note_tags(config, api_path)
        if tag in tags:
            raw_files.append((api_path, f.name))

    if not raw_files:
        print("  No new raw-tagged notes found.")
        return

    print(f"  Found {len(raw_files)} new raw note(s):")
    for api_path, fname in raw_files:
        print(f"    - {api_path}")

    for api_path, fname in raw_files:
        content = get_note_content(config, api_path)
        if not content:
            continue

        concepts = extract_concepts(content, fname)
        print(f"\n  [{fname}] Extracted concepts: {concepts}")

        # Update tracker for each concept
        for concept in concepts:
            if concept not in tracker["concepts"]:
                tracker["concepts"][concept] = {
                    "count": 0,
                    "sources": [],
                    "wiki_created": False,
                }

            entry = tracker["concepts"][concept]
            entry["count"] += 1
            if fname not in entry["sources"]:
                entry["sources"].append(fname)

            # Karpathy Principle: 2nd occurrence → model it
            if entry["count"] >= 2 and not entry["wiki_created"]:
                safe_name = sanitize_name(concept)
                print(f"  ⚡ CONCEPT MODELING: '{concept}' appeared {entry['count']}x")
                wiki_name = f"{config['wiki_paths']['concept']}/{safe_name}.md"
                content_note = generate_concept_note(concept, entry["sources"], config)
                if create_note_via_api(config, wiki_name, content_note):
                    entry["wiki_created"] = True

        # Create contrasts: one pass per note, between significant concepts only
        if len(concepts) >= 2:
            create_contrasts(concepts, fname, config, tracker)

        # Mark as processed
        tracker["processed_notes"].append(fname)

    save_tracker(tracker)


def create_contrasts(all_concepts, source_name, config, tracker):
    """Create contrast notes between significant co-occurring concepts.
    Only for concepts that have appeared 2+ times. Max 10 pairs per note.
    """
    significant = sorted(c for c in all_concepts
                         if c in tracker["concepts"]
                         and tracker["concepts"][c]["count"] >= 2)
    if len(significant) < 2:
        return

    pairs_created = 0
    for i in range(len(significant)):
        for j in range(i + 1, len(significant)):
            if pairs_created >= 10:
                return
            a, b = significant[i], significant[j]
            safe_a = sanitize_name(a)
            safe_b = sanitize_name(b)
            pair_name = f"{safe_a}_vs_{safe_b}"
            contrast_path = f"{config['wiki_paths']['contrast']}/{pair_name}.md"
            contrast_key = f"contrast:{pair_name}"
            if tracker.get(contrast_key):
                continue

            print(f"  ⚡ CONTRAST: '{a}' vs '{b}' co-occur in {source_name}")
            content = generate_contrast_note(a, b, [source_name], config)
            if create_note_via_api(config, contrast_path, content):
                tracker[contrast_key] = {"created": True, "sources": [source_name]}
                pairs_created += 1
    save_tracker(tracker)


def show_status(config, tracker):
    """Show current concept tracking status."""
    print("\n=== Concept Tracker Status ===\n")

    # Pending concepts (count=1, not yet modeled)
    pending = {k: v for k, v in tracker["concepts"].items() if v["count"] == 1 and not v["wiki_created"]}
    # Modeled concepts
    modeled = {k: v for k, v in tracker["concepts"].items() if v["wiki_created"]}

    print(f"Total unique concepts tracked: {len(tracker['concepts'])}")
    print(f"Processed notes: {len(tracker.get('processed_notes', []))}")

    if pending:
        print(f"\nPending (1st occurrence, waiting for 2nd):")
        for name, entry in sorted(pending.items()):
            print(f"  - {name}  (in: {', '.join(entry['sources'])})")

    if modeled:
        print(f"\nModeled (wiki created):")
        for name, entry in sorted(modeled.items()):
            print(f"  ✓ {name}  (sources: {', '.join(entry['sources'])})")

    # Pending notes (not yet processed)
    inbox_dir = SCRIPT_DIR.parent / config.get("inbox_path", "Inbox")
    if inbox_dir.exists():
        all_notes = set(f.name for f in inbox_dir.glob("*.md"))
        processed = set(tracker.get("processed_notes", []))
        unprocessed = all_notes - processed
        if unprocessed:
            print(f"\nUnprocessed notes in Inbox:")
            for n in sorted(unprocessed):
                print(f"  · {n}")


# ── Main ────────────────────────────────────────────────────────────

def main():
    config = load_config()
    tracker = load_tracker()

    if len(sys.argv) < 2:
        print("Usage: python obsidian_karpathy_agent.py [scan|watch|status]")
        return

    command = sys.argv[1]

    if command == "scan":
        print("[SCAN] Checking for new raw-tagged notes...")
        scan_raw_notes(config, tracker)
        print("[SCAN] Done.")

    elif command == "watch":
        interval = config.get("watch_interval_seconds", 60)
        print(f"[WATCH] Polling every {interval}s. Ctrl+C to stop.", flush=True)
        try:
            while True:
                scan_raw_notes(config, tracker)
                print(f"[WATCH] Next poll in {interval}s...", flush=True)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[WATCH] Stopped.")

    elif command == "status":
        show_status(config, tracker)

    else:
        print(f"Unknown command: {command}")
        print("Usage: python obsidian_karpathy_agent.py [scan|watch|status]")


if __name__ == "__main__":
    main()
