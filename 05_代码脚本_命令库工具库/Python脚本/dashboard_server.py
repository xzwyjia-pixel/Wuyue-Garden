"""
dashboard_server.py — 多直播间实时监控 Web 面板
Flask 移动端自适应, 端口 5050
多直播间: ?target=<slug>, /api/streams 列表
时间范围: ?range=1h|4h|all
"""
import json, time, os, re, ast, threading, webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque, Counter

from flask import Flask, render_template_string, jsonify, request

# ── 分析引擎 ──
from behavior_analyzer import analyze as analyze_host, analyze_per_host

# ── 历史数据库 ──
from history_db import init_db as init_history_db, save_snapshot, get_history, get_trends, get_sessions, get_daily_summaries

# ── 抖音开放平台 ──
try:
    from douyin_api import load_config as load_dy_config, get_access_token as get_dy_token
    HAS_DOUYIN = True
except ImportError:
    HAS_DOUYIN = False

# ── 基础路径 ──
BASE = Path("E:/MyCodeProjects")
INSTRUCTIONS = BASE / "审计工具" / "instructions.md"
STREAMS_DIR = BASE / "04-宝妈直播诊断系统"
FRAME_DIR = BASE / "06-存档中心" / "temp_frames"
LOG_DIR = BASE / "06-存档中心" / "logs"
DEFAULT_TARGET = "排骨走遍乡村"

app = Flask(__name__)

# ── 初始化历史数据库 ──
init_history_db()

# ── 缓存 (keyed by target) ──
_cache = {}  # {target: {"live":[], "triage":[], "stt":[], "audio_files":{}, "last_read":0}}


def parse_profiles():
    """Parse Live_Profiles from instructions.md"""
    if not INSTRUCTIONS.exists():
        return {}
    try:
        text = INSTRUCTIONS.read_text(encoding="utf-8")
        m = re.search(r"Live_Profiles\s*=\s*(\{.+?\n\})", text, re.DOTALL)
        if not m:
            return {}
        profiles = ast.literal_eval(m.group(1))
        return profiles
    except:
        return {}


def discover_streams():
    """Scan STREAMS_DIR for subdirs with live_data_*.jsonl. Auto-create dirs for profile entries."""
    streams = {}
    profiles = parse_profiles()
    for slug, val in profiles.items():
        display = val.get("display", slug)
        target_dir = STREAMS_DIR / slug
        if not target_dir.exists():
            target_dir = STREAMS_DIR / display
            if not target_dir.exists():
                target_dir = STREAMS_DIR / val.get("_alias", "")
                if not target_dir.exists():
                    # Auto-create directory for this profile
                    target_dir = STREAMS_DIR / slug
                    target_dir.mkdir(parents=True, exist_ok=True)
        streams[slug] = {
            "name": display,
            "dir": str(target_dir),
            "live_count": 0, "triage_count": 0, "stt_count": 0,
            "has_audio": False, "latest_time": "", "style": val.get("style", ""),
        }
    # Always add DEFAULT_TARGET
    if DEFAULT_TARGET not in streams:
        d = STREAMS_DIR / DEFAULT_TARGET
        streams[DEFAULT_TARGET] = {
            "name": DEFAULT_TARGET, "dir": str(d),
            "live_count": 0, "triage_count": 0, "stt_count": 0,
            "has_audio": False, "latest_time": "", "style": "",
        }
    # Scan directories for actual data
    if STREAMS_DIR.exists():
        for subdir in STREAMS_DIR.iterdir():
            if not subdir.is_dir():
                continue
            live_files = list(subdir.glob("live_data_*.jsonl"))
            if not live_files:
                continue
            name = subdir.name
            if name not in streams:
                streams[name] = {
                    "name": name, "dir": str(subdir),
                    "live_count": 0, "triage_count": 0, "stt_count": 0,
                    "has_audio": False, "latest_time": "", "style": "",
                }
            s = streams[name]
            for lf in live_files:
                try:
                    s["live_count"] += sum(1 for _ in lf.read_text(encoding="utf-8").split("\n") if _.strip())
                except:
                    pass
            for tf in subdir.glob("triage_log_*.jsonl"):
                try:
                    s["triage_count"] += sum(1 for _ in tf.read_text(encoding="utf-8").split("\n") if _.strip())
                except:
                    pass
            sttf = subdir / "stt.jsonl"
            if sttf.exists():
                try:
                    s["stt_count"] = sum(1 for _ in sttf.read_text(encoding="utf-8").split("\n") if _.strip())
                except:
                    pass
            s["has_audio"] = (subdir / "audio").exists()
    return streams


def get_paths(target):
    """Resolve data paths for a given target name"""
    tdir = STREAMS_DIR / target
    if not tdir.exists():
        for d in STREAMS_DIR.iterdir():
            if d.is_dir() and (target.lower() in d.name.lower() or d.name.lower() in target.lower()):
                tdir = d
                break
    tdir.mkdir(parents=True, exist_ok=True)
    # Try exact filename first, then glob for any live_data_*.jsonl
    live_file = tdir / f"live_data_{target}.jsonl"
    if not live_file.exists():
        files = list(tdir.glob("live_data_*.jsonl"))
        if files:
            live_file = files[0]
    triage_file = tdir / f"triage_log_{target}.jsonl"
    if not triage_file.exists():
        files = list(tdir.glob("triage_log_*.jsonl"))
        if files:
            triage_file = files[0]
    return {
        "live": live_file,
        "triage": triage_file,
        "stt": tdir / "stt.jsonl",
        "audio": tdir / "audio",
        "frames": FRAME_DIR / target,
    }


def tail_jsonl(path, max_lines=500):
    """Read last N lines of a JSONL file efficiently"""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        results = []
        for line in lines[-max_lines:]:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except:
                    pass
        return results
    except:
        return []


def refresh_cache(target=None):
    """Refresh data caches for a specific target"""
    if target is None:
        target = DEFAULT_TARGET
    if target not in _cache:
        _cache[target] = {"live": [], "triage": [], "stt": [], "audio_files": {}, "last_read": 0}
    p = get_paths(target)
    _cache[target]["live"] = tail_jsonl(p["live"], 300)
    _cache[target]["triage"] = tail_jsonl(p["triage"], 200)
    _cache[target]["stt"] = tail_jsonl(p["stt"], 100)
    if p["audio"].exists():
        wavs = sorted(p["audio"].glob("*.wav"), key=lambda f: f.stat().st_mtime, reverse=True)
        total_size = sum(f.stat().st_size for f in wavs) / (1024 * 1024)
        _cache[target]["audio_files"] = {"count": len(wavs), "latest": wavs[0].name if wavs else None, "size_mb": round(total_size, 1)}
    _cache[target]["last_read"] = time.time()


# ── 默认关键词 ──
KEYWORDS = ["苏苏", "江南", "农村", "家乡", "好吃", "香", "怎么做",
            "菜", "炒", "煮", "蒸", "妈妈", "小时候", "回忆",
            "想吃", "流口水", "关注", "点赞", "分享", "回购",
            "食材", "新鲜", "土", "农家", "绿色", "多少", "下单",
            "姐", "海燕"]


# ── API 端点 ──

@app.route("/api/streams")
def api_streams():
    """Return discovered streams with summary"""
    try:
        return jsonify({"streams": discover_streams()})
    except Exception as e:
        return jsonify({"error": str(e), "streams": {}})


@app.route("/api/restart-server")
def api_restart():
    """Health check / no-op keepalive"""
    return jsonify({"ok": True, "time": time.time()})


@app.route("/api/data")
def api_data():
    """实时数据, 含错误兜底"""
    try:
        target = request.args.get("target", DEFAULT_TARGET)
        time_range = request.args.get("range", "all")
        if time_range not in ("1h", "4h", "all"):
            time_range = "all"
        refresh_cache(target)
        c = _cache.get(target, {})
        live = c.get("live", [])
        triage = c.get("triage", [])
        stt = c.get("stt", [])

        # Apply time range filter
        if time_range == "1h":
            cutoff = time.time() - 3600
            live = [e for e in live if e.get("timestamp", 0) >= cutoff]
            triage = [e for e in triage if e.get("timestamp", 0) >= cutoff]
        elif time_range == "4h":
            cutoff = time.time() - 14400
            live = [e for e in live if e.get("timestamp", 0) >= cutoff]
            triage = [e for e in triage if e.get("timestamp", 0) >= cutoff]

        all_kw = Counter()
        conv_count = 0
        for entry in live[-100:]:
            for h in entry.get("keyword_hits", []):
                all_kw[h] += 1
            if entry.get("conversion_hits"):
                conv_count += 1

        latest_triage = triage[-1] if triage else None
        latest_stt = stt[-1] if stt else None

        chart_data = []
        for t in triage[-60:]:
            ts = t.get("timestamp", 0)
            chart_data.append({
                "time": datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "?",
                "brightness": t.get("brightness", 0),
                "warm_ratio": round(t.get("warm_ratio", 0) * 100, 1),
                "food_sat": t.get("food_saturation", 0),
                "authentic": t.get("score_authentic", 0),
                "detail": t.get("detail", 0),
            })

        trend_stats = {}
        if len(chart_data) >= 2:
            for key in ["brightness", "food_sat", "warm_ratio", "authentic", "detail"]:
                vals = [d[key] for d in chart_data]
                trend_stats[key] = {
                    "min": round(min(vals), 1),
                    "max": round(max(vals), 1),
                    "avg": round(sum(vals) / len(vals), 1),
                }

        seen = set()
        chat_texts = []
        profiles = parse_profiles()
        target_kw = KEYWORDS
        for slug, val in profiles.items():
            if slug == target or val.get("_alias", "") == target or val.get("display", "") == target:
                target_kw = val.get("keywords", KEYWORDS)
                break

        from behavior_analyzer import _analyze_speaking as _spk_analysis
        speaking_detail = _spk_analysis(stt)

        kw_timeline = {}
        for entry in live[-120:]:
            ts = entry.get("timestamp", 0)
            if not ts:
                continue
            bucket = int(ts // 300) * 300
            for h in entry.get("keyword_hits", []):
                if h not in target_kw:
                    continue
                bstr = datetime.fromtimestamp(bucket).strftime("%H:%M")
                if bstr not in kw_timeline:
                    kw_timeline[bstr] = {}
                kw_timeline[bstr][h] = kw_timeline[bstr].get(h, 0) + 1
        kw_series = []
        for tstr in sorted(kw_timeline.keys()):
            row = {"time": tstr}
            row.update(kw_timeline[tstr])
            kw_series.append(row)
        kw_names = sorted(set(k for b in kw_timeline.values() for k in b.keys()))[:6]

        for entry in reversed(live):
            for t in entry.get("real_texts", []):
                if t not in seen:
                    seen.add(t)
                    chat_texts.append({"text": t, "time": entry.get("time", ""), "has_kw": any(kw in t for kw in target_kw)})
            if len(chat_texts) >= 30:
                break

        return jsonify({
            "ocr_total": len(live),
            "keyword_hits": all_kw.most_common(15),
            "conversion_count": conv_count,
            "latest_triage": latest_triage,
            "latest_stt": latest_stt,
            "chat_texts": chat_texts,
            "chart": chart_data,
            "trend_stats": trend_stats,
            "kw_series": kw_series,
            "kw_names": kw_names,
            "audio": c.get("audio_files", {"count": 0, "size_mb": 0}),
            "stt_count": len(stt),
            "speaking_detail": speaking_detail,
            "target": target,
        })
    except Exception as e:
        return jsonify({"error": str(e), "ocr_total": 0, "keyword_hits": [], "conversion_count": 0,
                        "chat_texts": [], "chart": [], "trend_stats": {}, "kw_series": [],
                        "kw_names": [], "stt_count": 0, "speaking_detail": {}, "target": target})



@app.route("/api/health")
def api_health():
    """系统健康状态"""
    try:
        import psutil
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("E:/")
        cpu = psutil.cpu_percent(interval=0.5)
        return jsonify({
            "cpu_percent": cpu,
            "memory_percent": round(mem.percent, 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "streams": len(discover_streams()),
            "uptime": time.time() - _cache.get(DEFAULT_TARGET, {}).get("last_read", time.time()),
        })
    except ImportError:
        return jsonify({"error": "psutil not installed"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/ops")
def api_ops():
    """运营监控面板: 进程/告警/数据新鲜度/跨流对比"""
    import psutil
    now = time.time()

    # ── 进程检测 ──
    daemons = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            pid = proc.info["pid"]
            cmd = " ".join(proc.info["cmdline"] or [])
            name = proc.info["name"] or ""
            if not cmd:
                continue
            ct = proc.info["create_time"]
            uptime_min = int((now - ct) / 60) if ct else 0
            # Classify by script name
            if "monitor_engine" in cmd or "monitor_" in cmd:
                daemons.append({"type": "monitor", "pid": pid, "uptime": uptime_min, "status": "running"})
            elif "audio_capture" in cmd:
                daemons.append({"type": "audio", "pid": pid, "uptime": uptime_min, "status": "running"})
            elif "whisper_stt" in cmd or "stt" in cmd:
                daemons.append({"type": "stt", "pid": pid, "uptime": uptime_min, "status": "running"})
            elif "dashboard_server" in cmd:
                daemons.append({"type": "dashboard", "pid": pid, "uptime": uptime_min, "status": "running"})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # ── 系统资源 ──
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("E:/")
    cpu = psutil.cpu_percent(interval=0.5)
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%m-%d %H:%M")

    # ── 各流数据新鲜度 ──
    streams = discover_streams()
    stream_health = {}
    for slug, s in streams.items():
        p = get_paths(slug)
        live_file = p["live"]
        if live_file.exists():
            mtime = live_file.stat().st_mtime
            age_min = int((now - mtime) / 60)
            line_count = s.get("live_count", 0)
            # Load last few lines for error detection
            errors = 0
            try:
                with open(live_file, "r", encoding="utf-8") as f:
                    for line in f.readlines()[-30:]:
                        if line.strip() and "error" in line.lower():
                            errors += 1
            except:
                pass
            status = "good" if age_min < 5 else ("warning" if age_min < 30 else "critical")
            stream_health[slug] = {
                "name": s["name"],
                "age_min": age_min,
                "status": status,
                "lines": line_count,
                "triage": s.get("triage_count", 0),
                "stt": s.get("stt_count", 0),
                "errors_30": errors,
            }
        else:
            stream_health[slug] = {
                "name": s["name"], "age_min": -1, "status": "inactive",
                "lines": 0, "triage": 0, "stt": 0, "errors_30": 0,
            }

    # ── 告警 ──
    alerts = []
    # Daemon alerts
    daemon_types = {d["type"] for d in daemons}
    if "monitor" not in daemon_types:
        alerts.append({"level": "critical", "source": "进程", "msg": "监控引擎未运行"})
    if "audio" not in daemon_types:
        alerts.append({"level": "warning", "source": "音频", "msg": "音频采集未运行"})
    if "stt" not in daemon_types:
        alerts.append({"level": "warning", "source": "语音", "msg": "语音识别未运行"})
    # Stream alerts
    for slug, sh in stream_health.items():
        if sh["status"] == "critical":
            alerts.append({"level": "critical", "source": sh["name"], "msg": f"数据已停滞{sh['age_min']}分钟"})
        elif sh["status"] == "warning":
            alerts.append({"level": "warning", "source": sh["name"], "msg": f"数据{sh['age_min']}分钟未更新"})
        if sh.get("errors_30", 0) > 5:
            alerts.append({"level": "warning", "source": sh["name"], "msg": f"近30行错误{sh['errors_30']}次"})
        # Visual anomaly check from triage data
        p = get_paths(slug)
        triage_data = tail_jsonl(p["triage"], 10)
        if triage_data:
            last = triage_data[-1]
            b = last.get("brightness", 0)
            if b < 20:
                alerts.append({"level": "critical", "source": sh["name"], "msg": f"画面过暗(亮度{b})，检查直播间画面"})
            elif b > 230:
                alerts.append({"level": "warning", "source": sh["name"], "msg": f"画面过亮(亮度{b})，检查曝光"})
            if last.get("freeze_detected"):
                recent_freeze = sum(1 for t in triage_data[-5:] if t.get("freeze_detected"))
                if recent_freeze >= 3:
                    alerts.append({"level": "warning", "source": sh["name"], "msg": f"画面疑似冻结(连续{recent_freeze}/5帧)"})
            fq = last.get("food_quality", 0)
            if fq > 0 and fq < 20:
                alerts.append({"level": "warning", "source": sh["name"], "msg": f"食物质量分偏低({fq})"})
    # System alerts
    if disk.free / (1024**3) < 10:
        alerts.append({"level": "critical", "source": "系统", "msg": f"磁盘剩余仅{round(disk.free/(1024**3),1)}GB"})
    elif disk.free / (1024**3) < 30:
        alerts.append({"level": "warning", "source": "系统", "msg": f"磁盘剩余{round(disk.free/(1024**3),1)}GB"})

    # ── 跨流对比 (top N by data volume) ──
    ranking = sorted(stream_health.values(), key=lambda x: x["lines"], reverse=True)[:10]

    return jsonify({
        "daemons": daemons,
        "system": {
            "cpu": cpu, "mem": round(mem.percent, 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "boot": boot_time,
        },
        "streams": stream_health,
        "alerts": alerts,
        "ranking": ranking,
        "active_streams": sum(1 for sh in stream_health.values() if sh["status"] != "inactive"),
    })


@app.route("/api/compare")
def api_compare():
    """跨流对比雷达图: 所有活跃流归一化维度分"""
    try:
        profiles = parse_profiles()
        now = time.time()
        dims = ["brightness", "contrast", "warm_ratio", "detail", "color_entropy", "food_saturation"]
        labels = {"brightness": "亮度", "contrast": "对比度", "warm_ratio": "暖色", "detail": "纹理", "color_entropy": "色彩", "food_saturation": "食物sat"}
        streams = discover_streams()
        result = []
        for slug, s in streams.items():
            if s.get("triage_count", 0) < 2:
                continue
            p = get_paths(slug)
            triage_data = tail_jsonl(p["triage"], 20)
            if not triage_data:
                continue
            avg = {d: 0 for d in dims}
            for t in triage_data:
                for d in dims:
                    avg[d] += t.get(d, 0)
            n = len(triage_data)
            for d in dims:
                avg[d] = round(avg[d] / n, 1) if n else 0
            # Normalize to 0-100 scale
            ranges = {"brightness": 250, "contrast": 150, "warm_ratio": 0.5, "detail": 150, "color_entropy": 8, "food_saturation": 150}
            normalized = {}
            for d in dims:
                raw = avg[d]
                max_val = ranges[d]
                normalized[d] = round(min(100, raw / max_val * 100), 1) if max_val else 0
            result.append({
                "slug": slug,
                "name": s["name"],
                "style": s.get("style", ""),
                "raw": avg,
                "normalized": normalized,
                "labels": labels,
                "triage_count": s["triage_count"],
            })
        return jsonify({"streams": result, "dimensions": dims, "labels": labels})
    except Exception as e:
        return jsonify({"error": str(e), "streams": [], "dimensions": [], "labels": {}})


@app.route("/api/hosts")
def api_hosts():
    """Per-host segmented analysis"""
    target = request.args.get("target", DEFAULT_TARGET)
    refresh_cache(target)
    c = _cache.get(target, {})
    try:
        r = analyze_per_host(target, c.get("live", []), c.get("triage", []), c.get("stt", []))
        return jsonify(r)
    except Exception as e:
        return jsonify({"hosts": [], "error": str(e)})


@app.route("/api/behavior")
def api_behavior():
    """主播行为分析"""
    target = request.args.get("target", DEFAULT_TARGET)
    platform = request.args.get("platform", "视频号")
    host_type = request.args.get("host_type", "friendly")
    refresh_cache(target)
    c = _cache.get(target, {})
    try:
        r = analyze_host(target, c.get("live", []), c.get("triage", []), c.get("stt", []), platform, host_type)
        # Save to history database (async-friendly, SQLite is fast enough for inline)
        try:
            save_snapshot(target, r)
        except Exception as he:
            print(f"[history] save error: {he}")
        return jsonify(r)
    except Exception as e:
        return jsonify({"error": str(e), "overall_score": 0, "dimensions": {}, "moments": [], "topics": []})


@app.route("/api/history")
def api_history():
    """Historical analysis snapshots"""
    try:
        target = request.args.get("target", DEFAULT_TARGET)
        mode = request.args.get("mode", "trends")
        if mode not in ("trends", "sessions", "daily", "raw"):
            mode = "trends"
        if mode == "sessions":
            return jsonify({"sessions": get_sessions(target)})
        elif mode == "daily":
            return jsonify({"summaries": get_daily_summaries(target)})
        elif mode == "raw":
            limit = int(request.args.get("limit", 50))
            return jsonify({"history": get_history(target, limit)})
        else:
            return jsonify(get_trends(target))
    except Exception as e:
        return jsonify({"error": str(e), "direction": "unknown", "trends": {}, "history": [], "total_snapshots": 0})


@app.route("/api/export")
def api_export():
    """Download JSONL data as JSON"""
    try:
        target = request.args.get("target", DEFAULT_TARGET)
        fmt = request.args.get("format", "json")
        if fmt not in ("json", "csv"):
            fmt = "json"
        p = get_paths(target)
        lines = []
        for lf in [p["live"], p["triage"], p["stt"]]:
            if lf.exists():
                lines += tail_jsonl(lf, 2000)
        if fmt == "csv":
            from io import StringIO
            import csv
            si = StringIO()
            w = csv.writer(si)
            w.writerow(["timestamp", "time", "type", "text"])
            for e in lines:
                t = "ocr" if "texts" in e else ("triage" if "brightness" in e else "stt")
                txt = json.dumps(e.get("real_texts", e.get("text", "")), ensure_ascii=False)
                w.writerow([e.get("timestamp", ""), e.get("time", ""), t, txt])
            return si.getvalue(), 200, {"Content-Type": "text/csv; charset=utf-8", "Content-Disposition": f'attachment; filename="{target}_export.csv"'}
        return jsonify(lines)
    except Exception as e:
        return jsonify({"error": str(e)})


# ── HTML 模板 (inline, 无 CDN) ──

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>直播复盘系统</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0f0f14;color:#e0e0e0;padding:8px}
h1{font-size:15px;color:#fff;display:flex;align-items:center;gap:6px;margin-bottom:6px}
.stamp{font-size:10px;color:#555;text-align:right;margin-bottom:4px}
.scrollx{display:flex;gap:4px;overflow-x:auto;padding:4px 0 8px 0;scrollbar-width:none}
.scrollx::-webkit-scrollbar{display:none}
.chip{flex-shrink:0;padding:4px 10px;border-radius:12px;font-size:11px;cursor:pointer;background:#1a1a24;color:#777;border:1px solid #2a2a34;white-space:nowrap}
.chip.on{background:#3b82f6;color:#fff;border-color:#3b82f6}
.chip .cnt{color:#999;font-size:9px;margin-left:4px}
.rbar{display:flex;gap:4px;margin-bottom:6px}
.rbtn{padding:3px 10px;border-radius:10px;cursor:pointer;background:#1a1a24;color:#666;border:1px solid #2a2a34;font-size:11px}
.rbtn.on{background:#3b82f6;color:#fff;border-color:#3b82f6}
.cgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:4px;margin-bottom:6px}
.card{background:#1a1a24;border-radius:6px;padding:6px}
.card .l{font-size:9px;color:#777}
.card .v{font-size:16px;font-weight:700;color:#fff;margin-top:1px}
.card .v.g{color:#4ade80}.card .v.y{color:#facc15}.card .v.r{color:#f87171}.card .v.b{color:#60a5fa}
.charts{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px}
.charts canvas{background:#1a1a24;border-radius:6px;flex:1;min-width:180px;height:120px}
.stats{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:6px;font-size:10px;color:#888}
.statbox{background:#1a1a24;border-radius:4px;padding:3px 6px;display:inline-flex;gap:4px}
.statbox .s{color:#666}.statbox .g{color:#4ade80}.statbox .y{color:#facc15}
.tabbar{display:flex;gap:3px;margin-bottom:4px;flex-wrap:wrap}
.tab{padding:4px 10px;border-radius:5px;cursor:pointer;background:#1a1a24;color:#777;border:none;font-size:11px}
.tab.on{background:#3b82f6;color:#fff}
.tab:hover{background:#2a2a38}
.panel{display:none}
.panel.on{display:block}
pre{font-size:11px;color:#ccc;white-space:pre-wrap;word-break:break-all;background:#1a1a24;border-radius:6px;padding:8px;max-height:50vh;overflow-y:auto}
.devbar{display:flex;gap:3px;margin-bottom:4px;flex-wrap:wrap}
.devbtn{padding:2px 8px;border-radius:8px;cursor:pointer;background:#1a1a24;color:#666;border:1px solid #2a2a34;font-size:9px}
.devbtn.on{background:#3b82f6;color:#fff;border-color:#3b82f6}
.mode-mobile .cgrid{grid-template-columns:1fr 1fr}
.mode-mobile .charts canvas{min-width:140px;height:80px}
.mode-mobile .card .v{font-size:13px}
.mode-mobile .tab{font-size:9px;padding:3px 6px}
.mode-tablet .charts canvas{min-width:200px;height:100px}
.verbar{display:flex;gap:3px;margin-bottom:4px}
.verbtn{padding:3px 10px;border-radius:8px;cursor:pointer;background:#1a1a24;color:#666;border:1px solid #2a2a34;font-size:10px}
.verbtn.on{background:#3b82f6;color:#fff;border-color:#3b82f6}
</style>
</head>
<body>
<h1 style="text-align:center;font-size:16px;font-weight:700;color:#fff;justify-content:center">直播复盘系统</h1>
<div class="stamp" id="stamp"></div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
  <div class="scrollx" id="streamBar" style="flex:1"></div>
  <button id="pauseBtn" style="flex-shrink:0;padding:3px 8px;border-radius:8px;background:#1a1a24;color:#888;border:1px solid #2a2a34;font-size:10px;cursor:pointer;margin-left:4px">⏸</button>
</div>
<div id="hiddenStreams" style="font-size:9px;color:#555;margin-bottom:4px;display:none">
  <span id="hiddenToggle" style="cursor:pointer;text-decoration:underline dotted #444" onclick="toggleHiddenStreams()">📦 未开播...</span>
  <div id="hiddenList" style="display:none;margin-top:2px"></div>
</div>
<div class="cgrid" id="cards"></div>
<div class="charts" id="charts">
  <canvas id="ch_bright"></canvas>
  <canvas id="ch_kw"></canvas>
  <canvas id="ch_sat"></canvas>
  <canvas id="ch_kwt"></canvas>
</div>
<div class="stats" id="stats"></div>
<div class="tabbar" id="tabBar">
  <button class="tab on" onclick="switchTab(0)">💬弹幕</button>
  <button class="tab" onclick="switchTab(1)">📊关键词</button>
  <button class="tab" onclick="switchTab(2)">🎙语音</button>
  <button class="tab" onclick="switchTab(3)">🧠行为</button>
  <button class="tab" onclick="switchTab(4)">📈历史</button>
  <button class="tab" onclick="switchTab(5)">📋复盘</button>
  <label style="margin-left:auto;font-size:10px;color:#666;display:flex;align-items:center;gap:3px;flex-shrink:0">
    <input type="checkbox" id="scrollCb" checked> 自动滚动
  </label>
</div>
<div class="panel on"><pre id="out_chat">加载中...</pre></div>
<div class="panel"><pre id="out_kw">加载中...</pre></div>
<div class="panel"><pre id="out_stt">加载中...</pre></div>
<div class="panel"><div id="out_behavior" style="padding:4px">加载中...</div></div>
<div class="panel"><div id="out_history" style="padding:4px">加载中...</div></div>
<div class="panel"><div id="out_ops" style="padding:4px">加载中...</div><div style="margin-top:6px"><canvas id="ch_radar" style="width:100%;height:200px;background:#1a1a24;border-radius:6px"></canvas></div><div id="out_compare" style="padding:4px;margin-top:4px"></div><div id="out_report" style="padding:4px;margin-top:6px;border-top:1px solid #2a2a34"></div></div>
<script>
(function(){
var curTarget = '苏苏在浙里'; // 苏苏在浙里
var curRange = 'all';
var paused = false;
var pauseBtn = document.getElementById('pauseBtn');
pauseBtn.onclick=function(){
  paused=!paused;
  pauseBtn.textContent=paused?'▶':'⏸';
  pauseBtn.style.background=paused?'#3b82f6':'#1a1a24';
  if(!paused) fetchData();
};

// ── 版本系统 ──
var panels = document.querySelectorAll('.panel');

function switchTab(id){
  var tabBar = document.getElementById('tabBar');
  tabBar.querySelectorAll('.tab').forEach(function(b){b.className='tab';});
  tabBar.children[id].className = 'tab on';
  panels.forEach(function(p,j){
    p.className = 'panel' + (j===id?' on':'');
  });
  if(id===3) fetchBehavior();
  if(id===4) fetchHistory();
  if(id===5) { fetchOps(); fetchReport(); }
}
var ALL_TABS = [
  {id:1, name:'关键词', icon:'📊', key:'kw'},
  {id:2, name:'语音', icon:'🎙️', key:'stt'},
  {id:3, name:'行为', icon:'🧠', key:'behavior'},
  {id:4, name:'历史', icon:'📈', key:'history'},
  {id:5, name:'复盘', icon:'📋', key:'ops'},
];

// Auto scroll ref
var scrollCb = document.getElementById('scrollCb');

// Range buttons
var rbtns = document.querySelectorAll('.rbtn');
rbtns.forEach(function(b){
  b.onclick=function(){
    rbtns.forEach(function(t){t.className='rbtn'});
    b.className='rbtn on';
    curRange = b.getAttribute('data-r');
    fetchData();
  };
});



function setupCanvas(canvas,w,h){
  var dpr=window.devicePixelRatio||1;
  canvas.width=w*dpr; canvas.height=h*dpr;
  canvas.style.width=w+'px'; canvas.style.height=h+'px';
  var ctx=canvas.getContext('2d');
  ctx.scale(dpr,dpr); return ctx;
}

// Line chart
function drawLineChart(canvas,data,key,color,label,unit){
  var W=canvas.clientWidth||300, H=canvas.clientHeight||120;
  var ctx=setupCanvas(canvas,W,H);
  var P={t:16,b:14,l:28,r:8}, cw=W-P.l-P.r, ch=H-P.t-P.b;
  ctx.clearRect(0,0,W,H);
  if(!data||data.length<2){
    ctx.fillStyle='#555'; ctx.font='11px sans-serif';
    ctx.fillText('等待数据...',P.l,H/2+4);
    ctx.fillStyle='#666'; ctx.font='9px sans-serif';
    ctx.fillText(label||key,P.l,12); return;
  }
  var vals=data.map(function(d){return d[key];});
  var min=Math.min.apply(null,vals), max=Math.max.apply(null,vals);
  var range=max-min||1, n=data.length;
  ctx.beginPath();
  data.forEach(function(d,i){
    var x=P.l+(i/(n-1))*cw, y=P.t+ch-((d[key]-min)/range)*ch;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  });
  ctx.lineTo(P.l+cw,P.t+ch); ctx.lineTo(P.l,P.t+ch); ctx.closePath();
  ctx.fillStyle=color+'22'; ctx.fill();
  ctx.beginPath();
  data.forEach(function(d,i){
    var x=P.l+(i/(n-1))*cw, y=P.t+ch-((d[key]-min)/range)*ch;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  });
  ctx.strokeStyle=color; ctx.lineWidth=2; ctx.stroke();
  data.forEach(function(d,i){
    var x=P.l+(i/(n-1))*cw, y=P.t+ch-((d[key]-min)/range)*ch;
    ctx.beginPath(); ctx.arc(x,y,2,0,Math.PI*2); ctx.fillStyle=color; ctx.fill();
  });
  ctx.fillStyle='#888'; ctx.font='9px sans-serif';
  ctx.fillText((label||key)+(unit||''),P.l,12);
  ctx.fillStyle='#666'; ctx.font='8px sans-serif';
  ctx.textAlign='right'; ctx.fillText(max.toFixed(1),P.l-3,P.t+10);
  ctx.fillText(min.toFixed(1),P.l-3,P.t+ch+1);
  ctx.textAlign='left';
  if(n>1){ctx.fillText(data[0].time,P.l,H-2); ctx.textAlign='right'; ctx.fillText(data[n-1].time,P.l+cw,H-2); ctx.textAlign='left';}
}

// Bar chart
function drawBarChart(canvas,data,color){
  var W=canvas.clientWidth||300, H=canvas.clientHeight||120;
  var ctx=setupCanvas(canvas,W,H);
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#666'; ctx.font='9px sans-serif';
  ctx.fillText('关键词排行',6,12);
  if(!data||data.length===0){ctx.fillStyle='#555'; ctx.font='11px sans-serif'; ctx.fillText('暂无',8,H/2+4); return;}
  var topN=data.slice(0,7), maxVal=topN[0][1]||1;
  var barH=Math.min(12,(H-28)/topN.length), gap=2, lW=55;
  topN.forEach(function(item,i){
    var kw=item[0], cnt=item[1], y=18+i*(barH+gap);
    var bw=(cnt/maxVal)*(W-lW-16);
    ctx.fillStyle='#2a2a34'; ctx.fillRect(lW,y,W-lW-16,barH);
    ctx.fillStyle=color; ctx.fillRect(lW,y,bw,barH);
    ctx.fillStyle='#ccc'; ctx.font='9px sans-serif';
    ctx.fillText(kw+' '+cnt,3,y+barH-2);
  });
}

// Update UI
function update(d){
  try{
    var alive=d.latest_triage?true:false;
    document.getElementById('dot').textContent=alive?'● 运行中':'●';
    document.getElementById('dot').style.color=alive?'#4ade80':'#facc15';
    document.getElementById('targetName').textContent=(d.target||curTarget)+' 监控';
    document.getElementById('stamp').textContent='更新: '+new Date().toLocaleTimeString()+' | '+(d.chart.length)+'数据点';

    var totalKw=d.keyword_hits?d.keyword_hits.reduce(function(a,kv){return a+kv[1];},0):0;
    var cards='';
    cards+='<div class=card><div class=l>弹幕</div><div class="v b">'+(d.ocr_total||0)+'</div></div>';
    cards+='<div class=card><div class=l>关键词</div><div class="v y">'+totalKw+'</div></div>';
    cards+='<div class=card><div class=l>转化</div><div class="v g">'+(d.conversion_count||0)+'</div></div>';
    cards+='<div class=card><div class=l>STT</div><div class="v b">'+(d.stt_count||0)+'</div></div>';
    if(d.latest_triage){
      cards+='<div class=card><div class=l>亮度</div><div class=v>'+(d.latest_triage.brightness||'-')+'</div></div>';
      cards+='<div class=card><div class=l>食物sat</div><div class=v>'+(d.latest_triage.food_saturation||'-')+'</div></div>';
      var sceneLabel = {kitchen:'厨房',dining:'餐桌',outdoor:'户外',product:'带货',freeze:'静止',general:'直播'};
      var sceneC = {kitchen:'#facc15',dining:'#f87171',outdoor:'#4ade80',product:'#60a5fa',freeze:'#888',general:'#666'};
      var sc = d.latest_triage.scene||'general';
      cards+='<div class=card style="border-left:3px solid '+(sceneC[sc]||'#666')+'"><div class=l>场景</div><div class=v style="font-size:13px">'+(sceneLabel[sc]||sc)+'</div></div>';
      cards+='<div class=card><div class=l>食物质量</div><div class=v>'+(d.latest_triage.food_quality||'-')+'</div></div>';
    }
    document.getElementById('cards').innerHTML=cards;

    drawLineChart(document.getElementById('ch_bright'),d.chart,'brightness','#4ade80','亮度','');
    drawBarChart(document.getElementById('ch_kw'),d.keyword_hits,'#facc15');
    drawLineChart(document.getElementById('ch_sat'),d.chart,'food_sat','#f87171','食物sat','');

    var stats='';
    if(d.trend_stats){
      var labels={brightness:'亮度',food_sat:'食物sat',warm_ratio:'曉色'};
      for(var k in labels){
        if(d.trend_stats[k]){
          var s=d.trend_stats[k];
          stats+='<span class=statbox><span class=s>'+labels[k]+'</span> avg:<span class=g>'+s.avg+'</span> '+s.min+'~'+s.max+'</span>';
        }
      }
    }
    document.getElementById('stats').innerHTML=stats;

    var chat='';
    if(d.chat_texts&&d.chat_texts.length){
      d.chat_texts.slice(0,20).forEach(function(c){
        chat+=(c.has_kw?'[ ':'')+c.time+' '+c.text+'\\n';
      });
    }else{chat='暂无弹幕\\n';}
    var outChat=document.getElementById('out_chat');
outChat.textContent=chat;
if(scrollCb.checked) outChat.scrollTop=outChat.scrollHeight;

    var kw='';
    if(d.keyword_hits&&d.keyword_hits.length){
      d.keyword_hits.forEach(function(kv){
        var bar='';
        for(var b=0;b<Math.min(kv[1],20);b++) bar+='|';
        kw+=kv[0]+': '+kv[1]+' '+bar+'\\n';
      });
    }else{kw='暂无\\n';}
    document.getElementById('out_kw').textContent=kw;

    // Voice tab with speaking detail
    var sttOut = document.getElementById('out_stt');
    var spk = d.speaking_detail;
    if(spk && spk.stt_count > 0){
      var sttHtml = '';
      sttHtml += '最新: ' + (d.latest_stt?d.latest_stt.text:'') + ' [' + (d.latest_stt?d.latest_stt.time:'') + ']\\n';
      sttHtml += '总条数: ' + spk.stt_count + ' | 总字数: ' + spk.total_chars + '\\n';
      sttHtml += '语速: ' + spk.speech_rate + '字/秒 | 平均长度: ' + spk.avg_length + '字\\n';
      sttHtml += '提问: ' + spk.question_count + '次(' + (spk.question_ratio*100).toFixed(0) + '%) ';
      sttHtml += 'CTA: ' + spk.cta_count + '次(' + (spk.cta_density*100).toFixed(0) + '%) ';
      sttHtml += '情绪表达: ' + spk.emotion_count + '次\\n';
      sttHtml += '句间停顿: 平均' + spk.pause_avg + 's 最长' + spk.pause_max + 's ' + spk.pause_count + '次停顿\\n';
      // 价格/促销信号
      sttHtml += '\\n--- 价格/促销信号 ---\\n';
      sttHtml += '价格询问: ' + (spk.price_query_count||0) + '次 ';
      sttHtml += '促销提及: ' + (spk.promotion_count||0) + '次 ';
      sttHtml += '数量规格: ' + (spk.quantity_count||0) + '次\\n';
      sttHtml += '品质询问: ' + (spk.quality_query_count||0) + '次 ';
      sttHtml += '复购信号: ' + (spk.repurchase_count||0) + '次\\n';
      // 问题归类
      var qcats = spk.question_categories||{};
      var qkeys = Object.keys(qcats);
      if(qkeys.length){
        sttHtml += '\\n--- 观众问题归类 ---\\n';
        qkeys.forEach(function(qk){
          sttHtml += qk + ': ' + qcats[qk] + '次\\n';
        });
      }
      sttOut.textContent = sttHtml;
    }else if(d.latest_stt){
      sttOut.textContent='最新: '+(d.latest_stt.text||'')+'\\n时间: '+(d.latest_stt.time||'')+'\\n总数: '+(d.stt_count||0);
    }else{
      sttOut.textContent='暂无语音数据';
    }
  }catch(e){document.getElementById('out_chat').textContent='错误: '+e.message;}
}

function drawKwtChart(canvas, series, names){
  var W=canvas.clientWidth||300, H=canvas.clientHeight||120;
  if(!names||!series||series.length<2){var ctx=setupCanvas(canvas,W,H); ctx.clearRect(0,0,W,H);ctx.fillStyle='#666';ctx.font='9px sans-serif';ctx.fillText('关键词趋势',4,12);ctx.fillStyle='#555';ctx.font='11px sans-serif';ctx.fillText('暂无',W/2-12,H/2+4);return;}
  var colors=['#facc15','#4ade80','#60a5fa','#f87171','#a78bfa','#34d399'];
  var P={t:16,b:14,l:24,r:8,rowH:12};
  var totalH=H-P.t-P.b;
  var rowH=Math.min(14,(totalH-names.length*2)/names.length);
  var ctx=setupCanvas(canvas,W,H);
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#666';ctx.font='9px sans-serif';ctx.fillText('关键词趋势',4,12);
  var maxCnt=1;
  series.forEach(function(s){names.forEach(function(n){if(s[n]>maxCnt)maxCnt=s[n];});});
  names.forEach(function(n,i){
    var y=P.t+i*(rowH+2);
    ctx.fillStyle=colors[i%colors.length];ctx.font='8px sans-serif';
    ctx.fillText(n.slice(0,4),2,y+rowH-2);
    var lx=24;
    series.forEach(function(s,j){
      var val=s[n]||0;
      var bw=(val/maxCnt)*(W-lx-12);
      ctx.fillStyle=colors[i%colors.length]+(j===series.length-1?'bb':'44');
      ctx.fillRect(lx,y,bw,rowH);
      lx+=bw+1;
    });
  });
}

// Radar chart for cross-stream comparison
function drawRadarChart(canvas, streams, dimKeys, labels){
  var W=canvas.clientWidth||400, H=canvas.clientHeight||200;
  var dpr=window.devicePixelRatio||1;
  canvas.width=W*dpr; canvas.height=H*dpr;
  canvas.style.width=W+'px'; canvas.style.height=H+'px';
  var ctx=canvas.getContext('2d');
  ctx.scale(dpr,dpr);
  ctx.clearRect(0,0,W,H);
  if(!streams||streams.length<1){
    ctx.fillStyle='#555'; ctx.font='11px sans-serif'; ctx.fillText('暂无对比数据',W/2-30,H/2+4); return;
  }
  var cx=W/2, cy=H/2-10, r=Math.min(cx-40, cy-20, 80);
  var n=dimKeys.length;
  var colors=['#facc15','#4ade80','#60a5fa','#f87171','#a78bfa','#34d399','#f97316','#ec4899'];
  // Draw grid
  for(var ring=1; ring<=4; ring++){
    ctx.beginPath();
    var ri=r*ring/4;
    for(var i=0; i<n; i++){
      var angle=-Math.PI/2 + i*2*Math.PI/n;
      var x=cx+ri*Math.cos(angle), y=cy+ri*Math.sin(angle);
      i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
    }
    ctx.closePath(); ctx.strokeStyle='#2a2a34'; ctx.lineWidth=1; ctx.stroke();
  }
  // Axis lines + labels
  ctx.font='9px sans-serif'; ctx.textAlign='center';
  for(var i=0; i<n; i++){
    var angle=-Math.PI/2 + i*2*Math.PI/n;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+r*Math.cos(angle),cy+r*Math.sin(angle));
    ctx.strokeStyle='#2a2a34'; ctx.stroke();
    var lx=cx+(r+14)*Math.cos(angle), ly=cy+(r+14)*Math.sin(angle);
    ctx.fillStyle='#888'; ctx.fillText(labels[dimKeys[i]]||dimKeys[i], lx, ly+3);
  }
  // Draw each stream
  streams.forEach(function(st, idx){
    var nd=st.normalized;
    ctx.beginPath();
    for(var i=0; i<n; i++){
      var angle=-Math.PI/2 + i*2*Math.PI/n;
      var val=(nd[dimKeys[i]]||0)/100;
      var x=cx+r*val*Math.cos(angle), y=cy+r*val*Math.sin(angle);
      i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
    }
    ctx.closePath();
    var c=colors[idx%colors.length];
    ctx.fillStyle=c+'33'; ctx.fill();
    ctx.strokeStyle=c; ctx.lineWidth=2; ctx.stroke();
    // Label at last point
    var lastAngle=-Math.PI/2 + (n-1)*2*Math.PI/n;
    var lastVal=(nd[dimKeys[n-1]]||0)/100;
    ctx.fillStyle=c; ctx.font='bold 9px sans-serif'; ctx.textAlign='left';
    ctx.fillText(st.name, cx+r*lastVal*Math.cos(lastAngle)+6, cy+r*lastVal*Math.sin(lastAngle)+3);
  });

}

function fetchBehavior(){
  var out=document.getElementById('out_behavior');
  out.innerHTML='加载中...';
  fetch('/api/behavior?target='+encodeURIComponent(curTarget))
    .then(function(r){return r.json()})
    .then(function(d){
      if(d.error){out.innerHTML='<span style=color:#f87171>'+d.error+'</span>';return;}
      var h='';
      h+='<div style="font-size:24px;font-weight:700;margin-bottom:6px">综合评分: <span style=color:'+(d.overall_score>=60?'#4ade80':'#facc15')+'>'+d.overall_score+'</span>/100</div>';
      h+='<div style="font-size:11px;color:#999;margin-bottom:8px">'+d.summary+'</div>';
      // Recommendations
      if(d.recommendations&&d.recommendations.length){
        var prioColors = {high:'#f87171',medium:'#facc15',low:'#60a5fa'};
        h+='<div style="margin-bottom:6px">';
        d.recommendations.slice(0,6).forEach(function(rec){
          var pc = prioColors[rec.priority]||'#888';
          h+='<div style="font-size:10px;padding:4px;margin:2px 0;background:#1a1a24;border-radius:4px;border-left:3px solid '+pc+'">';
          h+='<div style="display:flex;gap:4px;align-items:center">';
          h+='<span style=color:'+pc+';font-weight:600>'+rec.title+'</span>';
          h+='<span style=color:#666;font-size:9px>['+rec.dim+']</span>';
          h+='<span style="color:'+pc+';margin-left:auto;font-size:8px">'+rec.priority+'</span>';
          h+='</div>';
          h+='<div style=color:#999;margin-top:1px>'+rec.detail+'</div>';
          h+='<div style=color:#4ade80;font-size:9px;margin-top:1px>→ '+rec.action+'</div></div>';
        });
        h+='</div>';
      }
      // Compliance risk
      if(d.compliance){
        var c = d.compliance.risk_level==='safe'?'#4ade80':d.compliance.risk_level==='low'?'#facc15':d.compliance.risk_level==='warning'?'#f87171':'#ff4444';
        var label = d.compliance.risk_level==='safe'?'安全':d.compliance.risk_level==='low'?'低风险':d.compliance.risk_level==='warning'?'中风险':'高风险';
        h += '<div style="font-size:11px;font-weight:600;margin:4px 0">合规审查</div>';
        h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:4px 10px;text-align:center">';
        h += '<div style="font-size:20px;font-weight:700;color:'+c+'">'+d.compliance.risk_score+'</div>';
        h += '<div style="font-size:8px;color:'+c+'">'+label+'</div></div>';
        h += '<div style="flex:1"><div style="background:#1a1a24;border-radius:4px;padding:4px 8px">';
        h += '<div style="font-size:9px;color:#888">限流风险 '+d.compliance.traffic_risk_pct+'% | '+d.compliance.summary+'</div>';
        if(d.compliance.found_words&&d.compliance.found_words.length){
          h += '<div style="font-size:9px;color:#f87171;margin-top:2px">违规词: '+d.compliance.found_words.slice(0,6).join(', ')+'</div>';
        }
        h += '</div></div></div>';
        // Violation detail
        if(d.compliance.violations&&d.compliance.violations.length){
          d.compliance.violations.slice(0,4).forEach(function(v){
            var vc = v.severity==='high'?'#f87171':v.severity==='medium'?'#facc15':'#60a5fa';
            h += '<div style="display:flex;gap:4px;font-size:9px;padding:1px 4px;margin:1px 0;background:#1a1a24;border-radius:3px">';
            h += '<span style=color:'+vc+';width:50px>['+v.severity+']</span>';
            h += '<span style=color:#ccc>'+v.word+'</span>';
            h += '<span style=color:#888>('+v.category+')</span>';
            h += '<span style=color:#555;margin-left:auto>权重'+v.weight+'</span></div>';
          });
        }
      }
      // Platform algorithm fit
      if(d.platform){
        h += '<div style="font-size:11px;font-weight:600;margin:4px 0">算法匹配: '+d.platform.platform+'</div>';
        h += '<div style="display:flex;gap:6px;margin-bottom:4px">';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:4px 8px;text-align:center">';
        h += '<div style="font-size:9px;color:#888">匹配度</div>';
        var fitC = d.platform.fit_score >= 60 ? '#4ade80' : d.platform.fit_score >= 40 ? '#facc15' : '#f87171';
        h += '<div style="font-size:16px;font-weight:700;color:'+fitC+'">'+d.platform.fit_score+'</div></div>';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:4px 8px;flex:1">';
        h += '<div style="font-size:9px;color:#888">'+d.platform.note+'</div>';
        h += '<div style="display:flex;gap:3px;margin-top:2px;flex-wrap:wrap">';
        (d.platform.factors||[]).forEach(function(f){
          h += '<span style="font-size:8px;padding:1px 4px;background:#0f0f14;border-radius:3px;color:#60a5fa">'+f+'</span>';
        });
        h += '</div></div></div>';
        // Platform factor evals
        if(d.platform.evals&&d.platform.evals.length){
          h += '<div style="margin-bottom:4px">';
          d.platform.evals.forEach(function(ev){
            var c = ev.score==='优'?'#4ade80':ev.score==='良'?'#facc15':'#f87171';
            h += '<div style="display:flex;gap:4px;font-size:9px;padding:1px 0"><span style=color:#888;width:60px>'+ev.factor+'</span>';
            h += '<span style=color:'+c+';width:36px>'+ev.score+'</span>';
            h += '<span style=color:#555;width:50px>'+ev.value+'</span>';
            h += '<span style=color:#666;flex:1>'+ev.tip+'</span></div>';
          });
          h += '</div>';
        }
      }
      // Traffic insights
      if(d.traffic){
        h += '<div style="font-size:11px;font-weight:600;margin:4px 0">流量分析</div>';
        h += '<div style="display:flex;gap:3px;margin-bottom:4px">';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:3px 6px;font-size:10px">脉冲: <span style=color:#facc15>'+d.traffic.spike_count+'</span></div>';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:3px 6px;font-size:10px">自然流量: <span style=color:#4ade80>'+(d.traffic.organic_ratio?Math.round(d.traffic.organic_ratio*100):'?')+'%</span></div>';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:3px 6px;font-size:10px">最佳时段: <span style=color:#60a5fa>'+(d.traffic.best_ad_window||'')+'</span></div>';
        h += '</div>';
        if(d.traffic.suggestion){
          h += '<div style="font-size:10px;color:#999;margin-bottom:4px">'+d.traffic.suggestion+'</div>';
        }
        if(d.traffic.traffic_peaks&&d.traffic.traffic_peaks.length){
          h += '<div style="margin-bottom:4px">';
          d.traffic.traffic_peaks.slice(0,3).forEach(function(sp){
            h += '<div style="display:flex;gap:4px;font-size:9px;padding:1px 0"><span style=color:#888>'+sp.time+'</span><span style=color:#facc15>'+sp.chats+'条</span><span style=color:#555>'+sp.multiplier+'x均值</span></div>';
          });
          h += '</div>';
        }
      // Sales analysis
      if(d.sales){
        h += '<div style="font-size:11px;font-weight:600;margin:6px 0 4px">带货分析</div>';
        h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
        var saleC = d.sales.score>=60?"#4ade80":d.sales.score>=40?"#facc15":"#f87171";
        h += '<div style="background:#1a1a24;border-radius:4px;padding:4px 10px;text-align:center">';
        h += '<div style="font-size:20px;font-weight:700;color:'+saleC+'">'+d.sales.score+'</div>';
        h += '<div style="font-size:8px;color:#888">带货分</div></div>';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:4px 8px;flex:1">';
        h += '<div style="display:flex;gap:6px;flex-wrap:wrap;font-size:9px">';
        h += '<span>产品提及 <span style=color:#facc15>'+d.sales.product_count+'次</span></span>';
        h += '<span>漏斗 <span style=color:#4ade80>'+d.sales.funnel_completeness+'/'+d.sales.funnel_total+'</span></span>';
        h += '<span>紧迫感 <span style=color:#60a5fa>'+Math.round(d.sales.urgency_density*100)+'%</span></span>';
        h += '<span>行动号召 <span style=color:#f87171>'+Math.round(d.sales.action_density*100)+'%</span></span>';
        if(d.sales.demo_quality) h += '<span>展示质量 <span style=color:#a78bfa>'+d.sales.demo_quality+'</span></span>';
        h += '</div></div></div>';
        // Product mentions by category
        if(d.sales.product_mentions&&d.sales.product_mentions.length){
          h += '<div style="display:flex;gap:3px;flex-wrap:wrap;margin-bottom:4px">';
          d.sales.product_mentions.slice(0,5).forEach(function(pm){
            h += '<div style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:9px">';
            h += '<span style=color:#ccc>'+pm[0]+'</span> <span style=color:#facc15>'+pm[1]+'</span></div>';
          });
          h += '</div>';
        }
        // Sales funnel status
        var funnelKeys = Object.keys(d.sales.funnel||{});
        if(funnelKeys.length){
          h += '<div style="display:flex;gap:2px;margin-bottom:4px">';
          var funnelColors = {attention:"#60a5fa",interest:"#4ade80",desire:"#facc15",action:"#f87171"};
          funnelKeys.forEach(function(fk){
            var f = d.sales.funnel[fk];
            var fc = funnelColors[fk]||"#888";
            var dotColor = f.active ? fc : "#444";
            h += '<div style="flex:1;background:#1a1a24;border-radius:4px;padding:3px 4px;text-align:center;opacity:'+(f.active?"1":"0.4")+'">';
            h += '<div style="font-size:8px;color:#888">'+f.label+'</div>';
            h += '<div style="color:'+dotColor+';font-size:12px">'+(f.active?"●":"○")+'</div>';
            h += '<div style="font-size:7px;color:#555;word-wrap:break-word">'+(f.active_phrases?f.active_phrases.slice(0,2).join(" "):"")+'</div></div>';
          });
          h += '</div>';
        }
        // Product display durations
        if(d.sales.display_durations&&d.sales.display_durations.length){
          h += '<div style="font-size:10px;font-weight:600;margin:4px 0;color:#888">产品展示时长TOP</div>';
          d.sales.display_durations.slice(0,4).forEach(function(pd){
            var mins = Math.floor(pd.duration_sec/60);
            var secs = pd.duration_sec%60;
            h += '<div style="display:flex;gap:4px;font-size:9px;padding:2px 4px;margin:1px 0;background:#1a1a24;border-radius:3px">';
            h += '<span style=color:#facc15>'+pd.category+'</span>';
            h += '<span style=color:#ccc>'+pd.product+'</span>';
            h += '<span style=color:#888>'+mins+'分'+secs+'秒</span>';
            h += '<span style=color:#555;margin-left:auto>提及'+pd.mentions+'次</span></div>';
          });
        }
        // Stage conversion estimates
        if(d.sales.stage_conversion_estimate){
          var sce = d.sales.stage_conversion_estimate;
          h += '<div style="font-size:10px;font-weight:600;margin:4px 0;color:#888">阶段转化估算</div>';
          h += '<div style="display:flex;gap:3px">';
          h += '<div style="flex:1;background:#1a1a24;border-radius:3px;padding:2px 4px;text-align:center;font-size:8px">';
          h += '<span style=color:#888>吸引→兴趣</span><div style=color:#60a5fa;font-size:11px>'+(sce.attention_to_interest||'?')+'</div></div>';
          h += '<div style="flex:1;background:#1a1a24;border-radius:3px;padding:2px 4px;text-align:center;font-size:8px">';
          h += '<span style=color:#888>兴趣→渴望</span><div style=color:#4ade80;font-size:11px>'+(sce.interest_to_desire||'?')+'</div></div>';
          h += '<div style="flex:1;background:#1a1a24;border-radius:3px;padding:2px 4px;text-align:center;font-size:8px">';
          h += '<span style=color:#888>渴望→行动</span><div style=color:#f87171;font-size:11px>'+(sce.desire_to_action||'?')+'</div></div>';
          h += '<div style="flex:1;background:#1a1a24;border-radius:3px;padding:2px 4px;text-align:center;font-size:8px">';
          h += '<span style=color:#888>综合转化</span><div style=color:#facc15;font-size:11px>'+(sce.overall_conversion_rate*100).toFixed(1)+'%</div></div>';
          h += '</div>';
        }
      }
      }
      // Host segments
      (function(){
        fetch('/api/hosts?target='+encodeURIComponent(curTarget))
          .then(function(r){return r.json()})
          .then(function(hd){
            var hosts = hd.hosts||[];
            if(hosts.length < 2) return; // single host, no section
            var hh = '<div style="font-size:11px;font-weight:600;margin:4px 0">主播分段</div>';
            var hostColors = {'苏苏':'#facc15','姐':'#f87171','海燕':'#60a5fa'};
            var currentSegment = 0;
            hosts.forEach(function(seg,i){
              var c = hostColors[seg.host]||'#888';
              var scoreC = seg.overall_score >= 60 ? '#4ade80' : seg.overall_score >= 40 ? '#facc15' : '#f87171';
              var dims = seg.dimensions||{};
              hh += '<div style="font-size:10px;padding:4px;margin:3px 0;background:#1a1a24;border-radius:4px;border-left:3px solid '+c+'">';
              hh += '<div style="display:flex;gap:6px;align-items:center">';
              hh += '<span style="color:'+c+';font-weight:600">'+seg.host+'</span>';
              hh += '<span style=color:#888>'+seg.segment_start+'-'+seg.segment_end+'</span>';
              hh += '<span style=color:#555>'+seg.duration+'min</span>';
              hh += '<span style="color:'+scoreC+';margin-left:auto">'+seg.overall_score+'分</span>';
              hh += '</div><div style=color:#666;margin-top:2px>'+seg.summary+'</div></div>';
            });
            // Find behavior panel and append
            var behPanel = document.getElementById('out_behavior');
            var existing = behPanel.querySelector('.host-segments');
            if(existing) existing.outerHTML = '<div class=host-segments>'+hh+'</div>';
            else behPanel.innerHTML = behPanel.innerHTML + '<div class=host-segments>'+hh+'</div>';
          })
          .catch(function(){});
      })();
      h+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:8px">';
      var dims=d.dimensions||{}, labels={engagement:'互动',visual:'视觉',speaking:'语态',authenticity:'真实感',scene:'场景',popularity:'人气'};
      var dimOrder=['engagement','visual','speaking','authenticity','scene','popularity'];
      dimOrder.forEach(function(k){
        var s=dims[k]?dims[k].score:0;
        var c=s>=60?'#4ade80':s>=40?'#facc15':'#f87171';
        h+='<div style="background:#1a1a24;border-radius:6px;padding:6px"><div style="font-size:9px;color:#888">'+labels[k]+'</div><div style="font-size:18px;font-weight:700;color:'+c+'">'+s+'</div></div>';
      });
      h+='</div>';
      // Moments timeline
      if(d.moments&&d.moments.length){
        h+='<div style="font-size:11px;font-weight:600;margin-bottom:4px">时刻线</div>';
        d.moments.forEach(function(m){
          var icons={start:'',kw_spike:'',conversion:'',freeze:'',end:''};
          h+='<div style="display:flex;gap:6px;font-size:10px;padding:2px 0;border-bottom:1px solid #1a1a24"><span style=color:#888>'+m.time+'</span><span style=color:#4ade80>'+m.label+'</span><span style=color:#666>'+m.detail+'</span></div>';
        });
      }
      // Scene monitoring analysis
      var scene=dims&&dims.scene;
      if(scene&&scene.dominant){
        h+='<div style="font-size:11px;font-weight:600;margin:6px 0 4px">场景监控</div>';
        h+='<div style="font-size:10px;color:#999;margin-bottom:4px">'+scene.summary+'</div>';
        // Scene distribution bars
        var sceneKeys=Object.keys(scene.distribution);
        if(sceneKeys.length){
          h+='<div style="margin-bottom:6px">';
          sceneKeys.forEach(function(sk){
            var info=scene.distribution[sk];
            var colors={kitchen:'#facc15',dining:'#f87171',outdoor:'#4ade80',food_prep:'#60a5fa',freeze:'#888',general:'#666'};
            var c=colors[sk]||'#666';
            h+='<div style="display:flex;align-items:center;gap:4px;margin:2px 0;font-size:10px">';
            h+='<span style=width:40px;flex-shrink:0;color:#ccc>'+info.label+'</span>';
            h+='<div style="flex:1;height:12px;background:#1a1a24;border-radius:3px;overflow:hidden">';
            h+='<div style="width:'+info.pct+'%;height:100%;background:'+c+';border-radius:3px"></div></div>';
            h+='<span style=width:40px;text-align:right;color:#888>'+info.pct+'%</span>';
            h+='</div>';
          });
          h+='</div>';
        }
        // Transition count
        h+='<div style="font-size:10px;color:#555;margin-bottom:4px">场景切换: '+scene.transitions+' 次</div>';
      }
      // Factors (affect viewers)
      if(d.factors&&d.factors.length){
        h+='<div style="font-size:11px;font-weight:600;margin:6px 0 4px">观众影响因子</div>';
        d.factors.slice(0,8).forEach(function(f){
          var c = f.impact > 0 ? '#4ade80' : '#f87171';
          var barW = Math.min(Math.abs(f.impact)*4, 80);
          h+='<div style="display:flex;align-items:center;gap:4px;margin:2px 0;font-size:10px">';
          h+='<span style=width:50px;flex-shrink:0;color:#ccc>'+f.name+'</span>';
          h+='<span style=color:#666;width:60px>'+f.value+'</span>';
          h+='<div style="flex:1;height:10px;background:#1a1a24;border-radius:3px;overflow:hidden">';
          h+='<div style="width:'+barW+'%;height:100%;background:'+c+';border-radius:3px"></div></div>';
          h+='<span style=width:24px;text-align:right;color:'+c+'>'+(f.impact>0?'+':'')+f.impact+'</span>';
          h+='</div>';
        });
      }
      // Correlations
      if(d.correlations&&d.correlations.length){
        h+='<div style="font-size:11px;font-weight:600;margin:6px 0 4px">因子关联</div>';
        d.correlations.slice(0,6).forEach(function(cor){
          var c = cor.r > 0.3 ? '#4ade80' : cor.r > 0 ? '#facc15' : '#f87171';
          h+='<div style="font-size:10px;padding:3px 4px;margin:2px 0;background:#1a1a24;border-radius:4px">';
          h+='<div style="display:flex;gap:4px"><span style=color:#4ade80>'+cor.factor_a+'</span>';
          h+='<span style=color:#888>vs</span>';
          h+='<span style=color:#60a5fa>'+cor.factor_b+'</span>';
          h+='<span style="color:'+c+';margin-left:auto">r='+cor.r+'</span></div>';
          h+='<div style="color:#666;margin-top:1px">'+cor.interpretation+'</div>';
          h+='</div>';
        });
      }
      // Topics
      if(d.topics&&d.topics.length){
        h+='<div style="font-size:11px;font-weight:600;margin:6px 0 4px">话题排行</div>';
        d.topics.slice(0,8).forEach(function(t){
          h+='<div style="display:flex;gap:4px;font-size:10px;padding:1px 0"><span style=color:#facc15>'+t[0]+'</span><span style=color:#666>'+t[1]+'次</span></div>';
        });
      }
      if(d.stream_duration){
        h+='<div style="font-size:10px;color:#555;margin-top:6px">直播时长: '+Math.floor(d.stream_duration/60)+'分钟</div>';
      }
      out.innerHTML=h;
    })
    .catch(function(e){out.innerHTML='<span style=color:#f87171>请求失败: '+e.message+'</span>'});
}

function fetchHistory(){
  var out = document.getElementById('out_history');
  out.innerHTML = '加载历史趋势...';
  fetch('/api/history?target='+encodeURIComponent(curTarget)+'&mode=trends')
    .then(function(r){return r.json()})
    .then(function(d){
      var h = '';
      var directionIcon = d.direction==='up'?'↑':d.direction==='down'?'↓':'→';
      var dirColor = d.direction==='up'?'#4ade80':d.direction==='down'?'#f87171':'#888';
      h += '<div style="font-size:11px;color:#888;margin-bottom:6px">' +
           '总快照: '+(d.total_snapshots||0)+' 趋势: <span style=color:'+dirColor+'>'+directionIcon+'</span></div>';

      // Trend cards per dimension
      if(d.trends){
        h += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px;margin-bottom:6px">';
        var dimLabels = {engagement:'互动',visual:'视觉',speaking:'语态',authenticity:'真实感',scene:'场景'};
        var keys = Object.keys(dimLabels);
        keys.forEach(function(k){
          var t = d.trends[k];
          if(!t) return;
          var c = t.direction==='up'?'#4ade80':t.direction==='down'?'#f87171':'#888';
          h += '<div style="background:#1a1a24;border-radius:6px;padding:4px;text-align:center">';
          h += '<div style="font-size:8px;color:#666">'+dimLabels[k]+'</div>';
          h += '<div style="font-size:14px;font-weight:700;color:'+c+'">'+t.arrow+' '+t.delta+'</div>';
          h += '<div style="font-size:8px;color:#555">'+t.old_avg+'→'+t.new_avg+'</div></div>';
        });
        h += '</div>';
      }

      // History line chart (last 20 snapshots)
      if(d.history && d.history.length >= 2){
        h += '<div style="font-size:10px;font-weight:600;margin-bottom:3px">评分走势</div>';
        h += '<div style="background:#1a1a24;border-radius:6px;padding:6px;margin-bottom:8px">';
        // Simple ASCII-style mini chart using div bars
        var snapshots = d.history;
        var maxVal = 100;
        h += '<div style="display:flex;align-items:end;gap:2px;height:60px;padding:0 2px">';
        snapshots.slice(-20).forEach(function(s){
          var barH = Math.max(3, (s.overall/maxVal)*55);
          h += '<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:end">';
          h += '<div style="width:100%;height:'+barH+'px;background:#3b82f6;border-radius:2px;min-height:3px" title="'+s.time+' '+s.overall+'"></div>';
          h += '</div>';
        });
        h += '</div>';
        h += '<div style="display:flex;justify-content:space-between;font-size:7px;color:#555;margin-top:2px">';
        h += '<span>'+(snapshots[0]?snapshots[0].time:'')+'</span>';
        h += '<span>'+(snapshots[snapshots.length-1]?snapshots[snapshots.length-1].time:'')+'</span>';
        h += '</div></div>';

        // Dimension overlay: engagement + visual line
        h += '<div style="font-size:10px;font-weight:600;margin-bottom:3px">维度趋势</div>';
        h += '<div style="background:#1a1a24;border-radius:6px;padding:6px;margin-bottom:8px">';
        var dimColors = {engagement:'#facc15',visual:'#4ade80',speaking:'#60a5fa',authenticity:'#a78bfa',scene:'#f87171'};
        keys.forEach(function(k){
          var vals = snapshots.map(function(s){return s.scores[k];});
          var avg = vals.reduce(function(a,b){return a+b;},0)/vals.length;
          var firstV = vals[0]||0, lastV = vals[vals.length-1]||0;
          var dir2 = lastV > firstV ? '↑' : lastV < firstV ? '↓' : '→';
          var c2 = lastV > firstV ? '#4ade80' : '#888';
          h += '<div style="display:flex;gap:4px;font-size:9px;padding:2px 0;align-items:center">';
          h += '<span style="color:'+dimColors[k]+';width:35px">'+dimLabels[k]+'</span>';
          h += '<div style="flex:1;height:6px;background:#0f0f14;border-radius:3px;overflow:hidden">';
          var pct = Math.min(100, avg);
          h += '<div style="width:'+pct+'%;height:100%;background:'+dimColors[k]+';border-radius:3px;opacity:0.6"></div></div>';
          h += '<span style="color:#888;width:30px;text-align:right;font-size:8px">'+avg.toFixed(0)+'</span>';
          h += '<span style=color:'+c2+';width:12px;text-align:right;font-size:9px">'+dir2+'</span>';
          h += '</div>';
        });
        h += '</div>';
      }

      // Sessions card
      h += '<div style="font-size:11px;font-weight:600;margin:6px 0 4px">直播场次</div>';
      fetch('/api/history?target='+encodeURIComponent(curTarget)+'&mode=sessions')
        .then(function(r2){return r2.json()})
        .then(function(sd){
          var sessions = sd.sessions||[];
          if(sessions.length){
            sessions.slice(0,10).forEach(function(s){
              var c3 = s.avg_score >= 60 ? '#4ade80' : s.avg_score >= 40 ? '#facc15' : '#f87171';
              h += '<div style="display:flex;gap:4px;font-size:10px;padding:3px 4px;margin:2px 0;background:#1a1a24;border-radius:4px">';
              h += '<span style=color:#888;width:80px>'+s.date+'</span>';
              h += '<span style=color:'+c3+';width:30px>'+s.avg_score+'</span>';
              h += '<span style=color:#666;flex:1>均'+s.avg_score+' 峰'+s.peak_score+'</span>';
              h += '<span style=color:#555>'+s.snapshots+'次</span>';
              h += '</div>';
            });
          } else {
            h += '<div style="font-size:10px;color:#555">暂无历史场次数据</div>';
          }
          out.innerHTML = h;
        })
        .catch(function(){
          out.innerHTML = h + '<div style="font-size:10px;color:#555">场次加载中...</div>';
        });
    })
    .catch(function(e){
      out.innerHTML = '<span style=color:#f87171>历史数据加载失败: '+e.message+'</span>';
    });
}

function fetchData(){
  if(paused) return;
  fetch('/api/data?target='+encodeURIComponent(curTarget)+'&range='+curRange)
    .then(function(r){return r.json()})
    .then(function(d){
      update(d);
      drawKwtChart(document.getElementById('ch_kwt'),d.kw_series,d.kw_names);
    })
    .catch(function(e){
      document.getElementById('out_chat').textContent='请求失败, 自动重试...';
      // Auto-reconnect: try again after 10s
      setTimeout(function(){
        if(!paused) fetchData();
      }, 10000);
    });
}

function fetchOps(){
  var out = document.getElementById('out_ops');
  fetch('/api/ops')
    .then(function(r){return r.json()})
    .then(function(d){
      var h = '';

      // Alerts bar
      if(d.alerts&&d.alerts.length){
        d.alerts.slice(0,5).forEach(function(a){
          var c = a.level==='critical'?'#f87171':'#facc15';
          h += '<div style="font-size:10px;padding:2px 4px;margin:2px 0;background:#1a1a24;border-left:3px solid '+c+';border-radius:3px">';
          h += '<span style=color:'+c+';font-weight:600>['+a.source+']</span> ';
          h += '<span style=color:#ccc>'+a.msg+'</span></div>';
        });
        h += '<div style="height:4px"></div>';
      } else {
        h += '<div style="font-size:10px;color:#4ade80;margin-bottom:4px">无告警</div>';
      }

      // System status cards
      h += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px;margin-bottom:6px">';
      h += '<div style="background:#1a1a24;border-radius:6px;padding:4px;text-align:center">'+
           '<div style="font-size:8px;color:#666">CPU</div>'+
           '<div style="font-size:14px;font-weight:700">'+(d.system?d.system.cpu:'?')+'%</div></div>';
      h += '<div style="background:#1a1a24;border-radius:6px;padding:4px;text-align:center">'+
           '<div style="font-size:8px;color:#666">内存</div>'+
           '<div style="font-size:14px;font-weight:700">'+(d.system?d.system.mem:'?')+'%</div></div>';
      h += '<div style="background:#1a1a24;border-radius:6px;padding:4px;text-align:center">'+
           '<div style="font-size:8px;color:#666">磁盘</div>'+
           '<div style="font-size:14px;font-weight:700">'+(d.system?d.system.disk_free_gb:'?')+'GB</div></div>';
      h += '</div>';

      // Daemon status
      h += '<div style="font-size:11px;font-weight:600;margin:4px 0">后台进程</div>';
      var daemonLabels = {monitor:'监控引擎',audio:'音频采集',stt:'语音识别',dashboard:'Web面板'};
      var daemonFound = {};
      if(d.daemons){
        d.daemons.forEach(function(dm){daemonFound[dm.type]=dm;});
      }
      var daemonKeys = Object.keys(daemonLabels);
      daemonKeys.forEach(function(k){
        var dm = daemonFound[k];
        var c = dm?'#4ade80':'#f87171';
        var icon = dm?'●':'○';
        var info = dm ? ('PID '+dm.pid+' 运行'+dm.uptime+'min') : '未运行';
        h += '<div style="display:flex;gap:4px;font-size:10px;padding:3px 4px;margin:1px 0;background:#1a1a24;border-radius:4px">'+
             '<span style=color:'+c+';width:8px>'+icon+'</span>'+
             '<span style=color:#ccc;width:60px>'+daemonLabels[k]+'</span>'+
             '<span style=color:#666>'+info+'</span></div>';
      });

      // Cross-stream ranking
      h += '<div style="font-size:11px;font-weight:600;margin:6px 0 4px">直播排行</div>';
      if(d.ranking&&d.ranking.length){
        d.ranking.slice(0,8).forEach(function(sh,i){
          var c = sh.status==='good'?'#4ade80':sh.status==='warning'?'#facc15':'#f87171';
          var rankIcon = i===0?'🥇':i===1?'🥈':i===2?'🥉':(i+1)+'.';
          h += '<div style="display:flex;gap:3px;font-size:10px;padding:2px 4px;margin:1px 0;background:#1a1a24;border-radius:4px">'+
               '<span style=color:#888;width:20px>'+rankIcon+'</span>'+
               '<span style=color:#ccc;width:70px>'+sh.name+'</span>'+
               '<span style=color:'+c+';width:12px>●</span>'+
               '<span style=color:#888>弹幕'+sh.lines+' triage'+sh.triage+' STT'+sh.stt+'</span>'+
               '<span style=color:#555;margin-left:auto>'+(sh.age_min>=0?sh.age_min+'min前':'无数据')+'</span></div>';
        });
      }

      // Active stream count
      h += '<div style="font-size:10px;color:#555;margin-top:4px">活跃流: '+(d.active_streams||0)+'/'+(Object.keys(d.streams||{}).length)+'</div>';

      out.innerHTML = h;

      // Fetch comparison data + draw radar chart
      fetch('/api/compare')
        .then(function(r){return r.json()})
        .then(function(cd){
          if(cd.streams&&cd.streams.length>=2){
            drawRadarChart(document.getElementById('ch_radar'), cd.streams, cd.dimensions, cd.labels);
            // Comparison detail table
            var cmp = '<div style="font-size:11px;font-weight:600;margin:4px 0">跨流对比</div>';
            cmp += '<div style="display:flex;gap:2px;overflow-x:auto;font-size:9px;margin-bottom:4px">';
            cd.streams.forEach(function(st){
              cmp += '<div style="flex-shrink:0;width:100px;background:#1a1a24;border-radius:4px;padding:4px">';
              cmp += '<div style="color:#ccc;font-weight:600">'+st.name+'</div>';
              cmp += '<div style="color:#888;font-size:8px">'+st.style+'</div>';
              cd.dimensions.slice(0,5).forEach(function(d){
                var v = st.normalized[d]||0;
                var c = v>=60?'#4ade80':v>=30?'#facc15':'#f87171';
                cmp += '<div style="display:flex;justify-content:space-between;margin:1px 0">';
                cmp += '<span style=color:#666>'+(cd.labels[d]||d)+'</span>';
                cmp += '<span style=color:'+c+'>'+v+'</span></div>';
              });
              cmp += '</div>';
            });
            cmp += '</div>';
            document.getElementById('out_compare').innerHTML = cmp;
          } else {
            document.getElementById('ch_radar').style.display = 'none';
            document.getElementById('out_compare').innerHTML = '<div style="font-size:10px;color:#555">需2个以上活跃流才能对比</div>';
          }
        })
        .catch(function(){});
    })
    .catch(function(e){
      out.innerHTML = '<span style=color:#f87171>运营数据加载失败: '+e.message+'</span>';
    });
}

var reviewRange = 'today'; // today | week | month
function setReviewRange(r){
  reviewRange = r;
  var btns = document.querySelectorAll('.verbtn');
  if(btns.length){
    btns.forEach(function(b){b.className='verbtn';});
    var idx = r==='today'?0:r==='week'?1:2;
    if(btns[idx]) btns[idx].className='verbtn on';
  }
  fetchReport();
}

function fetchReport(){
  var out = document.getElementById('out_report');
  var target = curTarget;
  // Show review range buttons
  var btns = '<div style="display:flex;gap:4px;margin-bottom:6px">';
  ['today','week','month'].forEach(function(r){
    var label = r==='today'?'当日复盘':r==='week'?'本周复盘':'本月复盘';
    var cls = r===reviewRange ? 'on' : '';
    btns += '<div class="verbtn '+cls+'" onclick="setReviewRange(\''+r+'\')">'+label+'</div>';
  });
  btns += '</div>';
  out.innerHTML = btns + '<div style="font-size:10px;color:#555">加载中...</div>';

  fetch('/api/data-integrate?target='+encodeURIComponent(target)+'&mode=full&range='+reviewRange)
    .then(function(r){return r.json()})
    .then(function(d){
      var m = d.meta||{};
      var ld = d.live||{};
      var td = d.triage||{};
      var sd = d.stt||{};
      var ad = d.analysis||{};
      var compliance = ad.compliance||{};
      var platform = ad.platform_fit||{};
      var traffic = ad.traffic||{};
      var sales = ad.sales||{};
      var dims = ad.dimensions||{};
      var recs = ad.recommendations||[];

      var h = btns;

      // Title
      h += '<div style="font-size:15px;font-weight:700;color:#fff;margin:8px 0 6px">📋 '+(m.target||target)+' · 直播复盘报告</div>';
      h += '<div style="font-size:10px;color:#555;margin-bottom:8px">生成时间: '+new Date().toLocaleString()+' | 数据: 弹幕'+m.data_counts.live+' 视觉'+m.data_counts.triage+' STT'+m.data_counts.stt+'</div>';

      // 1. 综合评分
      h += reportSection('综合评分');
      var score = ad.overall_score||0;
      var sc = score>=70?'#4ade80':score>=40?'#facc15':'#f87171';
      h += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">';
      h += '<div style="font-size:32px;font-weight:700;color:'+sc+'">'+score+'</div>';
      h += '<div style="font-size:11px;color:#888">'+((ad.summary||'').slice(0,60))+'</div></div>';

      // 2. 视觉诊断
      h += reportSection('视觉诊断');
      h += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px;margin-bottom:6px">';
      if(td.latest){
        var lt = td.latest;
        h += metricCard('亮度', lt.brightness||0, '80-180', 50);
        h += metricCard('对比度', lt.contrast||0, '60-120', 40);
        h += metricCard('暖色占比', ((lt.warm_ratio||0)*100).toFixed(1)+'%', '15-30%', 20);
        h += metricCard('纹理细节', lt.detail||0, '40-100', 30);
        h += metricCard('色彩熵', lt.color_entropy||0, '3.5-6.0', 2);
        h += metricCard('食物质量', lt.food_quality||0, '50-100', 20);
      }
      h += '</div>';
      // Scene distribution
      var scenes = td.scene_distribution||{};
      var sceneKeys = Object.keys(scenes);
      if(sceneKeys.length){
        h += '<div style="font-size:10px;font-weight:600;margin:4px 0;color:#888">场景分布 ('+td.total_snapshots+'帧)</div>';
        h += '<div style="display:flex;gap:2px;margin-bottom:4px">';
        var sceneColors = {kitchen:'#facc15',dining:'#f87171',outdoor:'#4ade80',product:'#60a5fa',freeze:'#888',general:'#666',unknown:'#444'};
        var sceneLabels = {kitchen:'厨房',dining:'餐桌',outdoor:'户外',product:'带货',freeze:'静止',general:'直播',unknown:'待识别'};
        sceneKeys.forEach(function(sk){
          var cnt = scenes[sk];
          var pct = (cnt/td.total_snapshots*100).toFixed(0);
          h += '<div style="flex:1;background:#1a1a24;border-radius:4px;padding:3px;text-align:center;border-top:2px solid '+(sceneColors[sk]||'#444')+'">';
          h += '<div style="font-size:9px;color:#ccc">'+(sceneLabels[sk]||sk)+'</div>';
          h += '<div style="font-size:12px;font-weight:700;color:'+(sceneColors[sk]||'#888')+'">'+cnt+'</div>';
          h += '<div style="font-size:8px;color:#555">'+pct+'%</div></div>';
        });
        h += '</div>';
      }

      // 3. 弹幕分析
      h += reportSection('弹幕分析');
      h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:4px">';
      h += metricCard('总弹幕', ld.total_ocr||0, '', 0);
      h += metricCard('关键词命中', (ld.keywords_top||[]).reduce(function(a,kv){return a+kv[1];},0), '', 0);
      h += metricCard('转化信号', ld.conversion_count||0, '', 0);
      h += metricCard('独立用户', ld.user_count||0, '', 0);
      h += '</div>';
      // top keywords
      var kws = ld.keywords_top||[];
      if(kws.length){
        h += '<div style="font-size:10px;font-weight:600;margin:4px 0;color:#888">关键词TOP</div>';
        h += '<div style="display:flex;gap:3px;flex-wrap:wrap;margin-bottom:4px">';
        kws.slice(0,8).forEach(function(kv){
          h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px"><span style=color:#facc15>'+kv[0]+'</span> <span style=color:#888>'+kv[1]+'</span></span>';
        });
        h += '</div>';
      }

      // 4. 语音分析
      h += reportSection('语音分析');
      var spk = sd.speaking_analysis||{};
      if(spk.stt_count>0){
        h += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px;margin-bottom:4px">';
        h += metricCard('语速', spk.speech_rate+'字/秒', '', 0);
        h += metricCard('提问', spk.question_count+'次', '', 0);
        h += metricCard('CTA', spk.cta_count+'次', '', 0);
        h += '</div>';
        h += '<div style="font-size:10px;display:flex;gap:3px;flex-wrap:wrap;margin-bottom:4px">';
        h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px">价格询问: <span style=color:#60a5fa>'+(spk.price_query_count||0)+'</span></span>';
        h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px">促销提及: <span style=color:#facc15>'+(spk.promotion_count||0)+'</span></span>';
        h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px">复购信号: <span style=color:#4ade80>'+(spk.repurchase_count||0)+'</span></span>';
        h += '</div>';
      } else {
        h += '<div style="font-size:10px;color:#555;margin-bottom:4px">暂无语音数据</div>';
      }

      // 5. 合规审查
      h += reportSection('合规审查');
      var riskScore = compliance.risk_score||100;
      var riskLevel = compliance.risk_level||'safe';
      var riskC = riskLevel==='safe'?'#4ade80':riskLevel==='low'?'#facc15':riskLevel==='warning'?'#f87171':'#ff4444';
      h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
      h += '<div style="background:#1a1a24;border-radius:6px;padding:4px 12px;text-align:center">';
      h += '<div style="font-size:20px;font-weight:700;color:'+riskC+'">'+riskScore+'</div>';
      h += '<div style="font-size:8px;color:'+riskC+'">'+riskLevel+'</div></div>';
      h += '<div style="flex:1;font-size:10px;color:#888">限流风险 '+(compliance.traffic_risk_pct||0)+'% | '+(compliance.summary||'')+'</div></div>';
      var found = compliance.found_words||[];
      if(found.length){
        h += '<div style="font-size:10px;color:#f87171;margin-bottom:4px">违规词: '+found.slice(0,8).join(', ')+'</div>';
      }
      var violations = compliance.violations||[];
      if(violations.length){
        violations.slice(0,3).forEach(function(v){
          h += '<div style="font-size:9px;padding:2px 4px;margin:1px 0;background:#1a1a24;border-radius:3px;display:flex;gap:4px">';
          h += '<span style=color:'+(v.severity==='high'?'#f87171':'#facc15')+'>['+v.severity+']</span>';
          h += '<span style=color:#ccc>'+v.word+'</span><span style=color:#888>('+v.category+')</span></div>';
        });
      }

      // 6. 维度分
      h += reportSection('维度评分');
      h += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px;margin-bottom:6px">';
      var dimLabels = {engagement:'互动',visual:'视觉',speaking:'语态',authenticity:'真实感',scene:'场景',popularity:'人气'};
      var dimOrder = ['engagement','visual','speaking','authenticity','scene','popularity'];
      dimOrder.forEach(function(k){
        var s = dims[k]?dims[k].score:0;
        var c = s>=60?'#4ade80':s>=40?'#facc15':'#f87171';
        h += '<div style="background:#1a1a24;border-radius:6px;padding:4px;text-align:center">';
        h += '<div style="font-size:8px;color:#888">'+(dimLabels[k]||k)+'</div>';
        h += '<div style="font-size:14px;font-weight:700;color:'+c+'">'+s+'</div></div>';
      });
      h += '</div>';

      // 7. 带货分析
      if(sales && sales.score !== undefined){
        h += reportSection('带货分析');
        h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
        var saleC = sales.score>=60?'#4ade80':sales.score>=40?'#facc15':'#f87171';
        h += '<div style="background:#1a1a24;border-radius:6px;padding:4px 12px;text-align:center">';
        h += '<div style="font-size:20px;font-weight:700;color:'+saleC+'">'+sales.score+'</div>';
        h += '<div style="font-size:8px;color:#888">带货分</div></div>';
        h += '<div style="background:#1a1a24;border-radius:4px;padding:4px 8px;flex:1;font-size:9px;color:#888">';
        h += '产品提及: <span style=color:#facc15>'+(sales.product_count||0)+'</span> | ';
        h += '行动号召: <span style=color:#f87171>'+Math.round((sales.action_density||0)*100)+'%</span>';
        h += '</div></div>';
        // Display durations
        if(sales.display_durations && sales.display_durations.length){
          h += '<div style="font-size:10px;font-weight:600;margin:4px 0;color:#888">产品展示时长TOP</div>';
          sales.display_durations.slice(0,3).forEach(function(pd){
            h += '<div style="display:flex;gap:4px;font-size:9px;padding:2px 4px;margin:1px 0;background:#1a1a24;border-radius:3px">';
            h += '<span style=color:#facc15>'+(pd.product||pd.category)+'</span>';
            h += '<span style=color:#888>'+Math.floor(pd.duration_sec/60)+'分'+pd.duration_sec%60+'秒</span>';
            h += '<span style=color:#555;margin-left:auto>提及'+(pd.mentions||0)+'次</span></div>';
          });
        }
      }

      // 8. 流量分析
      if(traffic && traffic.spike_count !== undefined){
        h += reportSection('流量分析');
        h += '<div style="display:flex;gap:3px;margin-bottom:4px">';
        h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px">流量脉冲: <span style=color:#facc15>'+(traffic.spike_count||0)+'</span></span>';
        h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px">自然流量: <span style=color:#4ade80>'+(traffic.organic_ratio?Math.round(traffic.organic_ratio*100):'?')+'%</span></span>';
        h += '<span style="background:#1a1a24;border-radius:4px;padding:2px 6px;font-size:10px">最佳时段: <span style=color:#60a5fa>'+(traffic.best_ad_window||'')+'</span></span>';
        h += '</div>';
        if(traffic.suggestion){
          h += '<div style="font-size:10px;color:#999;margin-bottom:4px">'+traffic.suggestion+'</div>';
        }
      }

      // 9. 平台匹配
      if(platform && platform.fit_score !== undefined){
        h += reportSection('平台匹配');
        var fitC = platform.fit_score>=60?'#4ade80':platform.fit_score>=40?'#facc15':'#f87171';
        h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
        h += '<div style="background:#1a1a24;border-radius:6px;padding:4px 12px;text-align:center">';
        h += '<div style="font-size:20px;font-weight:700;color:'+fitC+'">'+platform.fit_score+'</div>';
        h += '<div style="font-size:8px;color:#888">'+platform.platform+'匹配</div></div>';
        h += '<div style="flex:1;font-size:10px;color:#888">'+(platform.note||'')+'</div></div>';
      }

      // 10. 改进建议
      if(recs.length){
        h += reportSection('改进建议');
        recs.slice(0,6).forEach(function(rec){
          var pc = rec.priority==='high'?'#f87171':rec.priority==='medium'?'#facc15':'#60a5fa';
          h += '<div style="font-size:10px;padding:4px;margin:2px 0;background:#1a1a24;border-radius:4px;border-left:3px solid '+pc+'">';
          h += '<div style="display:flex;gap:4px;align-items:center">';
          h += '<span style=color:'+pc+';font-weight:600>'+(rec.title||'')+'</span>';
          h += '<span style=color:#666;font-size:9px>['+(rec.dim||'')+']</span>';
          h += '<span style=color:'+pc+';font-size:8px;margin-left:auto>'+(rec.priority||'')+'</span></div>';
          h += '<div style=color:#999;margin-top:1px>'+(rec.detail||'')+'</div>';
          h += '<div style=color:#4ade80;font-size:9px;margin-top:1px>→ '+(rec.action||'')+'</div></div>';
        });
      }

      // 11. 平台算法因素
      if(platform && platform.evals && platform.evals.length){
        h += reportSection('平台算法因素评估');
        platform.evals.forEach(function(ev){
          var ec = ev.score==='优'?'#4ade80':ev.score==='良'?'#facc15':'#f87171';
          h += '<div style="display:flex;gap:4px;font-size:9px;padding:1px 0"><span style=color:#888;width:60px>'+ev.factor+'</span>';
          h += '<span style=color:'+ec+';width:36px>'+ev.score+'</span>';
          h += '<span style=color:#555;width:50px>'+ev.value+'</span>';
          h += '<span style=color:#666;flex:1>'+ev.tip+'</span></div>';
        });
      }

      out.innerHTML = h;
    })
    .catch(function(e){
      out.innerHTML = '<div style="font-size:10px;color:#f87171">报告生成失败: '+e.message+'</div>';
    });
}

function reportSection(title){
  return '<div style="font-size:12px;font-weight:600;color:#ccc;margin:8px 0 4px;padding-bottom:2px;border-bottom:1px solid #2a2a34">'+title+'</div>';
}

function metricCard(label, value, range, threshold){
  var color = '#ccc';
  if(threshold > 0 && typeof value === 'number'){
    color = value >= threshold ? '#4ade80' : '#f87171';
  }
  if(typeof value === 'number' && value > 150) color = '#facc15';
  return '<div style="background:#1a1a24;border-radius:4px;padding:3px 6px"><div style="font-size:8px;color:#888">'+label+'</div><div style="font-size:14px;font-weight:700;color:'+color+'">'+value+'</div><div style="font-size:7px;color:#555">'+range+'</div></div>';
}

// Stream alive status check every 30s
function checkStreamAlive(){
  fetch('/api/stream-status').then(function(r){return r.json()}).then(function(d){
    var st = d.status[curTarget];
    if(st && !st.alive){
      document.getElementById('dot').style.color = '#f87171';
      document.getElementById('dot').textContent = '● 直播已结束('+st.age_min+'min)';
    } else if(st && st.alive){
      document.getElementById('dot').style.color = '#4ade80';
      document.getElementById('dot').textContent = '● 运行中';
    }
  }).catch(function(){});
}
setInterval(checkStreamAlive, 30000);

// Health check every 60s
function fetchHealth(){
  fetch('/api/health').then(function(r){return r.json()}).then(function(d){
    if(d.disk_free_gb){
      document.getElementById('stamp').textContent += ' | ' + d.disk_free_gb + 'GB/' + d.disk_total_gb + 'GB ' + d.cpu_percent + '%';
    }
  }).catch(function(){});
}
setInterval(fetchHealth, 60000);

function toggleHiddenStreams(){
  var hl=document.getElementById('hiddenList');
  if(hl) hl.style.display = hl.style.display==='block'?'none':'block';
}

function loadStreams(){
  fetch('/api/streams').then(function(r){return r.json()}).then(function(d){
    var bar=document.getElementById('streamBar');
    var keys=Object.keys(d.streams);
    if(keys.length<=1){if(bar)bar.style.display='none'; return;}
    if(!bar) return;
    bar.innerHTML='';
    var activeKeys=[], inactiveKeys=[];
    keys.forEach(function(k){
      var s=d.streams[k];
      // Active = has live data, OR is currently selected target, OR has triage data
      if((s.live_count||0)>0 || (s.triage_count||0)>0 || (s.stt_count||0)>0 || k===curTarget)
        activeKeys.push(k);
      else
        inactiveKeys.push(k);
    });
    // Render active chips
    activeKeys.forEach(function(k){
      var s=d.streams[k];
      var chip=document.createElement('div');
      chip.className='chip'+(k===curTarget?' on':'');
      chip.textContent=s.name+' ('+(s.live_count||0)+')';
      chip.title=s.style||'';
      chip.onclick=function(){
        document.querySelectorAll('.chip').forEach(function(t){t.className='chip'});
        chip.className='chip on';
        curTarget=k;
        fetchData();
      };
      bar.appendChild(chip);
    });
    // If no active, show all
    if(!activeKeys.length){
      activeKeys=inactiveKeys;
      inactiveKeys=[];
      activeKeys.forEach(function(k){
        var s=d.streams[k];
        var chip=document.createElement('div');
        chip.className='chip'+(k===curTarget?' on':'');
        chip.textContent=s.name;
        chip.onclick=function(){curTarget=k;fetchData();};
        bar.appendChild(chip);
      });
    }
    // Hidden streams
    var hs=document.getElementById('hiddenStreams');
    var hl=document.getElementById('hiddenList');
    if(hs&&hl){
      if(inactiveKeys.length){
        hs.style.display='block';
        hl.innerHTML='';
        inactiveKeys.forEach(function(k){
          var s=d.streams[k];
          var item=document.createElement('div');
          item.style.cssText='padding:2px 4px;cursor:pointer;border-radius:4px;font-size:10px;color:#666;background:#1a1a24;margin:1px 0';
          item.textContent=s.name+' ('+(s.style||s.name)+')';
          item.onclick=function(){curTarget=k;fetchData();loadStreams();};
          hl.appendChild(item);
        });
      } else {
        hs.style.display='none';
      }
    }
  }).catch(function(){});
}

loadStreams();
fetchData();
fetchData();
setInterval(fetchData,5000);
})();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/api/stt")
def api_stt():
    """STT 数据"""
    try:
        target = request.args.get("target", DEFAULT_TARGET)
        p = get_paths(target)
        stt = tail_jsonl(p["stt"], 200)
        return jsonify(stt)
    except Exception as e:
        return jsonify({"error": str(e), "stt": []})


# ── 直播结束自动停监控 ──
_STREAM_STATUS = {}  # target -> {"alive": bool, "last_active": ts, "ended_at": ts}

def _auto_stop_watchdog():
    """Background thread: check stream liveness, auto-stop on prolonged inactivity"""
    while True:
        time.sleep(60)
        now = time.time()
        for target, c in list(_cache.items()):
            live = c.get("live", [])
            triage = c.get("triage", [])
            if not live:
                continue
            # Check last activity timestamp
            last_ts = max((e.get("timestamp", 0) for e in live if e.get("timestamp")), default=0)
            age = now - last_ts if last_ts else 9999
            # Check freeze frames
            freeze_count = sum(1 for t in triage[-20:] if t.get("freeze_detected"))
            freeze_ratio = freeze_count / max(len(triage[-20:]), 1)

            was_alive = _STREAM_STATUS.get(target, {}).get("alive", True)
            is_alive = age < 600 and freeze_ratio < 0.5  # 10 min + <50% freeze

            _STREAM_STATUS[target] = {
                "alive": is_alive,
                "last_active": last_ts,
                "age_min": round(age / 60, 1),
                "freeze_ratio": round(freeze_ratio, 2),
                "ended_at": _STREAM_STATUS.get(target, {}).get("ended_at") if is_alive else (now if was_alive else _STREAM_STATUS.get(target, {}).get("ended_at")),
            }

            # Auto-stop: was alive → now dead, kill monitor processes
            if was_alive and not is_alive and age > 600:
                print(f"[auto-stop] {target} 直播已结束({age/60:.0f}分钟无数据), 停止监控...")
                try:
                    import subprocess, os
                    procs = ["monitor_engine", "monitor_", "audio_capture"]
                    for pname in procs:
                        subprocess.run(
                            ["powershell", "-Command",
                             f"Get-Process | Where-Object {{$_.CommandLine -match '{pname}'}} | Stop-Process -Force"],
                            capture_output=True, timeout=10)
                    print(f"[auto-stop] {target} 监控进程已停止")
                except Exception as e:
                    print(f"[auto-stop] 停止进程失败: {e}")

@app.route("/api/data-integrate")
def api_data_integrate():
    """统一数据接口: 外部系统接入用, 返回结构化后台数据"""
    try:
        token = request.args.get("token", "")
        target = request.args.get("target", DEFAULT_TARGET)
        platform = request.args.get("platform", "视频号")
        host_type = request.args.get("host_type", "friendly")
        mode = request.args.get("mode", "full")  # full | live | triage | stt | analysis
        fmt = request.args.get("format", "json")  # json | csv
        time_range = request.args.get("range", "today")  # today | week | month | all

        refresh_cache(target)
        c = _cache.get(target, {})
        live = c.get("live", [])
        triage = c.get("triage", [])
        stt = c.get("stt", [])

        # Apply time range filter
        if time_range != "all":
            now = time.time()
            if time_range == "today":
                # midnight today
                import datetime as _dt
                today_midnight = _dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff = today_midnight.timestamp()
            elif time_range == "week":
                cutoff = now - 7 * 86400
            elif time_range == "month":
                cutoff = now - 30 * 86400
            else:
                cutoff = 0
            live = [e for e in live if e.get("timestamp", 0) >= cutoff]
            triage = [t for t in triage if t.get("timestamp", 0) >= cutoff]
            stt = [s for s in stt if s.get("timestamp", 0) >= cutoff]

        result = {
            "meta": {
                "target": target,
                "range": time_range,
                "server_time": datetime.now().isoformat(),
                "api_version": "2.0",
                "platform": platform,
                "data_counts": {"live": len(live), "triage": len(triage), "stt": len(stt)},
            }
        }

        if mode in ("full", "live"):
            from behavior_analyzer import _analyze_engagement
            eng = _analyze_engagement(live)
            result["live"] = {
                "total_ocr": len(live),
                "engagement": eng,
                "chat_count": eng.get("total_chats", 0),
                "keywords_top": Counter(
                    h for e in live for h in e.get("keyword_hits", [])
                ).most_common(20),
                "conversion_count": sum(1 for e in live if e.get("conversion_hits")),
                "user_count": eng.get("unique_users", 0),
            }

        if mode in ("full", "triage"):
            from behavior_analyzer import _analyze_visual
            vis = _analyze_visual(triage)
            result["triage"] = {
                "total_snapshots": len(triage),
                "visual_summary": vis,
                "latest": triage[-1] if triage else None,
                "scene_distribution": dict(Counter(
                    t.get("scene", "unknown") for t in triage
                )),
                "avg_brightness": round(sum(t.get("brightness", 0) for t in triage) / len(triage), 1) if triage else 0,
                "avg_food_quality": round(sum(t.get("food_quality", 0) for t in triage) / len(triage), 1) if triage else 0,
                "freeze_ratio": round(sum(1 for t in triage if t.get("freeze_detected")) / len(triage), 2) if triage else 0,
            }

        if mode in ("full", "stt"):
            from behavior_analyzer import _analyze_speaking as _spk
            spk = _spk(stt)
            result["stt"] = {
                "total": len(stt),
                "speaking_analysis": spk,
                "latest": stt[-1] if stt else None,
            }

        if mode in ("full", "analysis"):
            from behavior_analyzer import analyze
            analysis = analyze(target, live, triage, stt, platform, host_type)
            result["analysis"] = {
                "overall_score": analysis.get("overall_score", 0),
                "dimensions": analysis.get("dimensions", {}),
                "compliance": analysis.get("compliance", {}),
                "platform_fit": analysis.get("platform", {}),
                "traffic": analysis.get("traffic", {}),
                "sales": analysis.get("sales", {}),
                "recommendations": analysis.get("recommendations", []),
            }

        if fmt == "csv":
            from io import StringIO
            import csv
            si = StringIO()
            w = csv.writer(si)
            w.writerow(["timestamp", "type", "field", "value", "text"])
            for e in live[-200:]:
                for t in e.get("real_texts", []):
                    w.writerow([e.get("timestamp", ""), "chat", "", "", t])
                for kw in e.get("keyword_hits", []):
                    w.writerow([e.get("timestamp", ""), "keyword", kw, "1", ""])
            for t in triage[-200:]:
                for field in ["brightness", "warm_ratio", "food_saturation", "food_quality", "scene", "score_authentic"]:
                    w.writerow([t.get("timestamp", ""), "triage", field, t.get(field, ""), ""])
            for s in stt[-200:]:
                w.writerow([s.get("timestamp", ""), "stt", "text", "", s.get("text", "")])
            return si.getvalue(), 200, {"Content-Type": "text/csv; charset=utf-8",
                                        "Content-Disposition": f'attachment; filename="{target}_data.csv"'}

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "meta": {"api_version": "2.0"}, "live": {}, "triage": {}, "stt": {}, "analysis": {}})


@app.route("/api/douyin/status")
def api_douyin_status():
    """抖音开放平台连接状态"""
    if not HAS_DOUYIN:
        return jsonify({"connected": False, "error": "douyin_api.py not loaded", "config_file": "douyin_config.json"})
    try:
        cfg = load_dy_config()
        has_creds = bool(cfg.get("client_key")) and bool(cfg.get("client_secret"))
        has_token = bool(cfg.get("access_token"))
        status = {
            "connected": has_token,
            "configured": has_creds,
            "has_token": has_token,
            "token_expires": cfg.get("token_expires_at", 0),
            "config_file": "douyin_config.json",
        }
        if has_creds and not has_token:
            token = get_dy_token()
            status["connected"] = token is not None
            status["has_token"] = token is not None
        return jsonify(status)
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)})


@app.route("/api/stream-status")
def api_stream_status():
    """Check if each stream is alive or ended"""
    try:
        return jsonify({"status": dict(_STREAM_STATUS), "auto_stop": True})
    except Exception as e:
        return jsonify({"error": str(e), "status": {}})


def start_server(port=5050, debug=False):
    print(f"[dashboard] Web 面板: http://localhost:{port}")
    print(f"[dashboard] 手机访问: http://<本机IP>:{port}")
    _auto_stop_daemon = threading.Thread(target=_auto_stop_watchdog, daemon=True)
    _auto_stop_daemon.start()
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)


def run_dashboard(port=5050, open_browser=True):
    if open_browser:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    start_server(port=port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="多直播间监控 Web 面板")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--browser", action="store_true", default=True)
    args = parser.parse_args()
    run_dashboard(port=args.port, open_browser=args.browser)
