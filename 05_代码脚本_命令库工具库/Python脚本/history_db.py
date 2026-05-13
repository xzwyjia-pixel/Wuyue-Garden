"""
history_db.py — 历史数据库 SQLite
存储每次分析快照 → 趋势分析 / 跨期比较
"""
import json, sqlite3, time
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict

DB_PATH = Path("E:/MyCodeProjects/06-存档中心/history.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    """Ensure tables exist"""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            timestamp REAL NOT NULL,
            date TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            eng_score INTEGER DEFAULT 0,
            vis_score INTEGER DEFAULT 0,
            spk_score INTEGER DEFAULT 0,
            auth_score INTEGER DEFAULT 0,
            scene_score INTEGER DEFAULT 0,
            factors TEXT DEFAULT '[]',
            correlations TEXT DEFAULT '[]',
            moments_count INTEGER DEFAULT 0,
            stream_duration INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_snap_target_time
        ON analysis_snapshots(target, timestamp)
    """)
    conn.commit()
    conn.close()


def save_snapshot(target, analysis_result):
    """Save one analysis snapshot to history DB"""
    dims = analysis_result.get("dimensions", {})
    now_ts = time.time()
    today = date.today().isoformat()

    conn = _get_conn()
    conn.execute("""
        INSERT INTO analysis_snapshots
            (target, timestamp, date, overall_score,
             eng_score, vis_score, spk_score, auth_score, scene_score,
             factors, correlations, moments_count, stream_duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        target, now_ts, today,
        analysis_result.get("overall_score", 0),
        dims.get("engagement", {}).get("score", 0),
        dims.get("visual", {}).get("score", 0),
        dims.get("speaking", {}).get("score", 0),
        dims.get("authenticity", {}).get("score", 0),
        dims.get("scene", {}).get("score", 0),
        json.dumps(analysis_result.get("factors", []), ensure_ascii=False),
        json.dumps(analysis_result.get("correlations", []), ensure_ascii=False),
        len(analysis_result.get("moments", [])),
        analysis_result.get("stream_duration", 0),
    ))
    conn.commit()
    conn.close()


def get_history(target, limit=50):
    """Get last N snapshots for a target"""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT * FROM analysis_snapshots
        WHERE target = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (target, limit)).fetchall()
    conn.close()

    result = []
    for r in reversed(rows):  # chronological order
        result.append({
            "id": r["id"],
            "ts": r["timestamp"],
            "date": r["date"],
            "time": datetime.fromtimestamp(r["timestamp"]).strftime("%m-%d %H:%M"),
            "overall": r["overall_score"],
            "scores": {
                "engagement": r["eng_score"],
                "visual": r["vis_score"],
                "speaking": r["spk_score"],
                "authenticity": r["auth_score"],
                "scene": r["scene_score"],
            },
            "moments": r["moments_count"],
            "duration": r["stream_duration"],
        })
    return result


def get_trends(target):
    """Compute trend: direction, magnitude, moving avg for each dimension"""
    history = get_history(target, limit=20)
    if len(history) < 2:
        return {"direction": "stable", "trends": {}, "history": history, "total_snapshots": len(history)}

    # Split into two halves for comparison
    mid = len(history) // 2
    recent = history[mid:]
    older = history[:mid]

    dims = ["engagement", "visual", "speaking", "authenticity", "scene"]
    trends = {}

    for dim in dims:
        old_avg = sum(h["scores"][dim] for h in older) / max(len(older), 1)
        new_avg = sum(h["scores"][dim] for h in recent) / max(len(recent), 1)
        delta = round(new_avg - old_avg, 1)
        if abs(delta) < 3:
            direction = "stable"
            arrow = "→"
        elif delta > 0:
            direction = "up"
            arrow = "↑"
        else:
            direction = "down"
            arrow = "↓"
        trends[dim] = {
            "direction": direction,
            "delta": delta,
            "arrow": arrow,
            "old_avg": round(old_avg, 1),
            "new_avg": round(new_avg, 1),
        }

    # Overall direction
    total_delta = sum(t["delta"] for t in trends.values())
    if abs(total_delta) < 5:
        overall = "stable"
    elif total_delta > 0:
        overall = "up"
    else:
        overall = "down"

    return {
        "direction": overall,
        "trends": trends,
        "history": history,
        "total_snapshots": len(history),
    }


def get_sessions(target):
    """Group snapshots by date for session overview"""
    history = get_history(target, limit=200)
    sessions = defaultdict(list)
    for h in history:
        sessions[h["date"]].append(h)

    result = []
    for d in sorted(sessions.keys(), reverse=True):
        snaps = sessions[d]
        avg_overall = round(sum(s["overall"] for s in snaps) / len(snaps))
        peak = max(s["overall"] for s in snaps)
        result.append({
            "date": d,
            "snapshots": len(snaps),
            "avg_score": avg_overall,
            "peak_score": peak,
            "first_time": snaps[0]["time"],
            "last_time": snaps[-1]["time"],
        })
    return result


def get_daily_summaries(target):
    """Aggregate into daily averages"""
    sessions = get_sessions(target)
    summaries = []
    for s in sessions:
        history = get_history(target, limit=200)
        daily = [h for h in history if h["date"] == s["date"]]
        if not daily:
            continue
        dims = ["engagement", "visual", "speaking", "authenticity", "scene"]
        avg_scores = {}
        for dim in dims:
            avg_scores[dim] = round(sum(h["scores"][dim] for h in daily) / len(daily), 1)
        summaries.append({
            "date": s["date"],
            "snapshots": len(daily),
            "overall_avg": round(sum(h["overall"] for h in daily) / len(daily)),
            "scores": avg_scores,
        })
    return summaries
