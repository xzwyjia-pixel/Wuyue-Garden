"""
data_organizer.py — v2.0 数据分离 + 进程看门狗 + 实时仪表盘
读 jsonl 分离到子目录, 监控进程健康, 自动恢复
"""
import json, time, os, sys, subprocess
from pathlib import Path
from datetime import datetime
from collections import deque

POLL_SECONDS = 3
HEALTH_CHECK_INTERVAL = 30  # check process health every 30s

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path("E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
BASE_DIR = Path("E:/MyCodeProjects/02-审计工具")

# === process manifest ===
PROCESSES = [
    {"name": "audio_capture", "cmd": [sys.executable, "audio_capture.py", "--target", str(TARGET), "--chunk", "15", "--vad", "0.003", "--agc", "0.15"]},
    {"name": "whisper_stt", "cmd": [sys.executable, "whisper_stt.py", "--target", str(TARGET)]},
    {"name": "monitor_dual", "cmd": [sys.executable, "monitor_dual.py", "--target", str(TARGET), "--auto"]},
    {"name": "timeline_fusion", "cmd": [sys.executable, "timeline_fusion.py", "--target", str(TARGET)]},
    {"name": "audience_classifier", "cmd": [sys.executable, "audience_classifier.py", "--target", str(TARGET), "--watch"]},
    {"name": "system_monitor", "cmd": [sys.executable, "system_monitor.py", "--target", str(TARGET)]},
    {"name": "stream_health", "cmd": [sys.executable, "stream_health.py", "--target", str(TARGET)]},
    {"name": "monitor_v3", "cmd": [sys.executable, "monitor_v3.py", "--target", str(TARGET)]},
]

# === text filter ===
UI_NOISE = {
    "发四", "嫩瞎", "Ux", "士袄", "孑鸡", "聊-聊", "禁止",
    "充值", "直播推荐", "关注", "分享", "点赞",
    "与大家互动一下", "规行为请及时投诉", "进入直播间",
}
USERNAME_ONLY = {"胡美胜", "嘉蒲清", "小灰灰", "以封", "有缘人"}
MIN_TEXT_LEN = 2
MAX_NOISE_RATIO = 0.6

def is_junk(text):
    if len(text) < MIN_TEXT_LEN:
        return True
    t = text.strip()
    if t in UI_NOISE:
        return True
    for u in UI_NOISE:
        if u in t:
            return True
    if t in USERNAME_ONLY:
        return True
    punct = sum(1 for c in text if c in "?？!！。，、：；""''（）()??........【】")
    if punct / max(len(text), 1) > MAX_NOISE_RATIO:
        return True
    return False

# === platform data sources ===
PLATFORMS = {
    "SuSu": {"dir": TARGET / "视频号", "ocr": TARGET / "live_data_SuSu.jsonl",
             "triage": TARGET / "triage_log_SuSu.jsonl"},
    "DouYin": {"dir": TARGET / "抖音", "ocr": TARGET / "live_data_DouYin.jsonl",
               "triage": TARGET / "triage_log_DouYin.jsonl"},
}
STT_SRC = TARGET / "stt.jsonl"
HEARTBEAT = TARGET / "monitor_heartbeat.json"

positions = {}
buffers = {}
for k, v in PLATFORMS.items():
    for src_key in ["ocr", "triage"]:
        key = f"{k}_{src_key}"
        positions[key] = 0
        buffers[key] = deque(maxlen=50)
positions["stt"] = 0
buffers["stt"] = deque(maxlen=50)

for p in PLATFORMS.values():
    p["dir"].mkdir(parents=True, exist_ok=True)

# === file tail ===
def tail_file(path, pos, buf):
    if not path.is_file():
        return pos, 0
    try:
        fsize = path.stat().st_size
        if fsize < pos:
            pos = 0
        with open(path, "r", encoding="utf-8") as f:
            f.seek(pos)
            new_lines = f.readlines()
            new_pos = f.tell()
        count = 0
        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            try:
                buf.append(json.loads(line))
                count += 1
            except json.JSONDecodeError:
                pass
        return new_pos, count
    except Exception:
        return pos, 0

def write_platform(src_key, src_buf, plat_dir, prefix):
    if not src_buf:
        return
    last = src_buf[-1]
    out_path = plat_dir / f"{prefix}.jsonl"
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(last, ensure_ascii=False) + "\n")

def write_heartbeat(stats, proc_status):
    with open(HEARTBEAT, "w", encoding="utf-8") as f:
        json.dump({"stats": stats, "processes": proc_status,
                    "time": time.time()}, f)

# === process watchdog ===
procs = {}  # name -> Popen
restart_count = {}  # name -> consecutive restarts
last_health_check = 0
MAX_BACKOFF = 60  # max 60s between restarts

def start_process(proc_def):
    name = proc_def["name"]
    # backoff: skip if too soon since last restart
    last_restart = restart_count.get(name, {}).get("last_time", 0)
    attempts = restart_count.get(name, {}).get("attempts", 0)
    if attempts > 0:
        backoff = min(2 ** (attempts - 1), MAX_BACKOFF)
        if time.time() - last_restart < backoff:
            return False  # skip, still in backoff
    try:
        p = subprocess.Popen(proc_def["cmd"], cwd=str(BASE_DIR),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs[name] = p
        restart_count[name] = {"attempts": attempts + 1, "last_time": time.time()}
        return True
    except Exception as e:
        print(f"[看门狗] {name} 启动失败: {e}")
        return False

def check_health():
    global last_health_check
    now = time.time()
    if now - last_health_check < HEALTH_CHECK_INTERVAL:
        return {}
    last_health_check = now

    status = {}
    for proc_def in PROCESSES:
        name = proc_def["name"]
        p = procs.get(name)
        alive = p and p.poll() is None
        if alive:
            status[name] = "alive"
            # reset backoff after 2 stable checks
            rc = restart_count.get(name, {})
            if rc.get("attempts", 0) > 0 and now - rc.get("last_time", 0) > HEALTH_CHECK_INTERVAL * 2:
                restart_count[name] = {"attempts": 0, "last_time": 0}
        else:
            code = p.returncode if p else -1
            if p:
                print(f"[看门狗] {name} 退出(code={code}), 重启(第{restart_count.get(name,{}).get('attempts',0)+1}次)...")
            ok = start_process(proc_def)
            if ok:
                status[name] = "restarted"
            else:
                rc = restart_count.get(name, {})
                backoff_remaining = max(0, min(2 ** (rc.get("attempts", 0) - 1), MAX_BACKOFF) - (now - rc.get("last_time", 0)))
                status[name] = f"backoff({int(backoff_remaining)}s)"
    return status

# start all
for proc_def in PROCESSES:
    start_process(proc_def)

sys.stdout.reconfigure(encoding="utf-8")
cycle = 0
start_time = time.time()

while True:
    now_str = datetime.now().strftime("%H:%M:%S")
    stats = {}

    # watchdog
    proc_status = check_health()

    # Poll each source
    for k, v in PLATFORMS.items():
        ok, cnt = tail_file(v["ocr"], positions.get(f"{k}_ocr", 0),
                            buffers.get(f"{k}_ocr", deque()))
        positions[f"{k}_ocr"] = ok
        stats[f"{k}_ocr"] = cnt

        if cnt > 0:
            buf = buffers.get(f"{k}_ocr", deque())
            if buf:
                last = buf[-1].copy()
                texts = last.get("texts", [])
                last["texts"] = [t for t in texts if not is_junk(t)]
                if last["texts"] != texts:
                    buf[-1] = last
            # dedup across last 10
            if buf:
                seen = set()
                deduped = []
                for entry in list(buf)[-10:]:
                    texts = entry.get("texts", [])
                    unique = [t for t in texts if t not in seen]
                    if unique:
                        seen.update(unique)
                        deduped.append({**entry, "texts": unique})
                if deduped:
                    buf.clear()
                    buf.extend(deduped)
            write_platform(f"{k}_ocr", buf, v["dir"], "live_data")

        tk, tcnt = tail_file(v["triage"], positions.get(f"{k}_triage", 0),
                             buffers.get(f"{k}_triage", deque()))
        positions[f"{k}_triage"] = tk
        stats[f"{k}_triage"] = tcnt
        if tcnt > 0:
            write_platform(f"{k}_triage", buffers.get(f"{k}_triage", deque()),
                           v["dir"], "triage_log")

    sk, scnt = tail_file(STT_SRC, positions.get("stt", 0),
                         buffers.get("stt", deque()))
    positions["stt"] = sk
    stats["stt"] = scnt

    write_heartbeat(stats, proc_status)

    # status
    if cycle % 5 == 0:
        runtime = int(time.time() - start_time)
        alive_count = sum(1 for s in proc_status.values() if s == "alive")
        print(f"[组织] [{now_str}] 运行{runtime}s "
              f"进程:{alive_count}/{len(PROCESSES)} "
              f"视频OCR:{stats.get('SuSu_ocr',0)} "
              f"抖音OCR:{stats.get('DouYin_ocr',0)} "
              f"STT:{stats.get('stt',0)}")

        for plat, label in [("SuSu", "视频号"), ("DouYin", "抖音")]:
            buf = buffers.get(f"{plat}_ocr", deque())
            if buf:
                texts = buf[-1].get("texts", [])[:1]
                if texts:
                    print(f"  [{label}] {texts[0][:60]}")

        stt_buf = buffers.get("stt", deque())
        if stt_buf:
            text = stt_buf[-1].get("text", "")[:80]
            if text.strip():
                print(f"  [语音] {text}")

        if any(s != "alive" for s in proc_status.values()):
            dead = [k for k, v in proc_status.items() if v != "alive"]
            print(f"  [看门狗] 异常进程: {dead}")

    cycle += 1
    time.sleep(POLL_SECONDS)
