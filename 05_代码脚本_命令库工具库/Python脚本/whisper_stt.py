"""
whisper_stt.py — Whisper STT (CUDA) 替代 Vosk
直接读 WAV (48kHz stereo) → numpy 重采样 16kHz mono → Whisper
绕过 ffmpeg 依赖
用法: python whisper_stt.py --target <直播目录>
"""
import json, time, os, sys, re, argparse, wave, signal, traceback
from pathlib import Path
from datetime import datetime
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
args = parser.parse_args()
TARGET = Path(args.target)
POLL_SECONDS = 5
CHUNK_SECONDS = 15
MODEL_NAME = "base"
LANG = "zh"

# Log file
LOG_FILE = Path("E:/MyCodeProjects/06-存档中心/logs/stt_daemon.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(msg, end="\n"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, end=end, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

running = True
def handle_signal(s, f):
    global running
    log("[whisper] 收到停止信号, 优雅退出...")
    running = False
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

log(f"加载模型 {MODEL_NAME} (CUDA)...", end="")
try:
    import whisper
    model = whisper.load_model(MODEL_NAME, device="cuda")
    log(f" 就绪, 设备: {model.device}")
except Exception as e:
    log(f" 失败: {e}")
    log("回退到 CPU...")
    try:
        model = whisper.load_model(MODEL_NAME, device="cpu")
        log(f" 就绪 (CPU)")
    except Exception as e2:
        log(f" CPU加载也失败: {e2}")
        sys.exit(1)

STT_PATH = TARGET / "stt.jsonl"
WHISPER_SR = 16000  # whisper expects 16kHz

def load_wav_for_whisper(path):
    """Read WAV (any sample rate/channels), return 16kHz mono float32 [-1,1]"""
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        nchannels = wf.getnchannels()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    # stereo → mono
    if nchannels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)
    # resample to 16kHz
    if sr != WHISPER_SR:
        ratio = WHISPER_SR / sr
        new_len = int(len(audio) * ratio)
        audio = np.interp(
            np.linspace(0, len(audio) - 1, new_len),
            np.arange(len(audio)),
            audio,
        )
    return audio

# track processed files
AUDIO_DIR = TARGET / "audio"
processed = set()
for f in sorted(AUDIO_DIR.glob("audio_*.wav")):
    processed.add(f.name)

log(f"监控 {AUDIO_DIR}/, 已跳过 {len(processed)} 旧文件")
consecutive_errors = 0
retry_delay = 1

while running:
    try:
        if not AUDIO_DIR.exists():
            log(f"音频目录不存在: {AUDIO_DIR}, 等待...")
            time.sleep(30)
            continue

        wavs = sorted(AUDIO_DIR.glob("audio_*.wav"))
        new_wavs = [f for f in wavs if f.name not in processed]

        for wav in new_wavs:
            if not running:
                break
            processed.add(wav.name)
            try:
                log(f"转写 {wav.name}...", end="")
                audio = load_wav_for_whisper(wav)
                result = model.transcribe(
                    audio,
                    language=LANG,
                    task="transcribe",
                    fp16=True,
                    no_speech_threshold=0.6,
                )
                text = result.get("text", "").strip()
                segments = result.get("segments", [])

                if not text:
                    log(" (静音)")
                    consecutive_errors = 0
                    continue

                ts_now = time.time()
                m = re.search(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})", wav.name)
                if m:
                    h, mi, s = int(m.group(4)), int(m.group(5)), int(m.group(6))
                    ts_now = datetime.now().replace(hour=h, minute=mi, second=s).timestamp()

                entry = {
                    "timestamp": ts_now,
                    "text": text,
                    "time": datetime.fromtimestamp(ts_now).strftime("%H:%M:%S"),
                    "source": "whisper",
                    "segments": len(segments),
                    "duration": CHUNK_SECONDS,
                }
                with open(STT_PATH, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                log(f" OK ({len(text)}字)")
                consecutive_errors = 0

            except Exception as e:
                consecutive_errors += 1
                log(f" 出错: {e}")
                traceback.print_exc()
                if consecutive_errors >= 3:
                    log("连续3次错误, 等待60s后重试...")
                    time.sleep(60)
                    consecutive_errors = 0

    except Exception as e:
        log(f"主循环异常: {e}")
        traceback.print_exc()
        log(f"等待{retry_delay}s后重试...")
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 60)

    if running:
        time.sleep(POLL_SECONDS)

log("[whisper] 已停止")
