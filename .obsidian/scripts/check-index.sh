#!/bin/bash
# Obsidian index health check
# Usage: bash check-index.sh

IDB="$HOME/AppData/Roaming/Obsidian/IndexedDB/app_obsidian.md_0.indexeddb.leveldb"
OMNI="E:/Obsidian/.obsidian/plugins/omnisearch/data.json"

echo "=== Obsidian Index Check ==="
date

# Process
tasklist //FI "IMAGENAME eq Obsidian.exe" 2>&1 | grep Obsidian | wc -l | xargs -I{} echo "Processes: {}"

# Memory (max PID)
tasklist //FI "IMAGENAME eq Obsidian.exe" 2>&1 | grep Obsidian | awk '{print $NF}' | sort -rn | head -1 | xargs -I{} echo "Max mem: {} KB"

# IndexedDB (real index)
if [ -d "$IDB" ]; then
  last=$(find "$IDB" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -1)
  now=$(date +%s)
  idle=$((now - ${last%.*}))
  size=$(du -sh "$IDB" 2>/dev/null | cut -f1)
  tables=$(ls "$IDB"/*.ldb 2>/dev/null | wc -l)

  echo "Index: $size ($tables tables)"

  if [ $idle -lt 180 ]; then
    echo "Status: ACTIVE"
  elif [ $idle -lt 600 ]; then
    echo "Status: RECENT"
  else
    echo "Status: STABLE (idle ${idle}s)"
  fi
else
  echo "Index: NONE (not built)"
fi

# omnisearch config (not index!)
ls -lh "$OMNI" 2>/dev/null | awk '{print "Config:", $5, "modified:", $6, $7, $8}'
