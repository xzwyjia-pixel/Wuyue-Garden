"""
stt_processor.py — v2.1 简化版
直接处理 16kHz mono WAV (audio_capture v2 输出)
无中间转换, 更快轮询, 可选说话人分离
"""
import json, os, time, wave, argparse
from pathlib import Path
from datetime import datetime
from vosk import Model, KaldiRecognizer

DEFAULT_BASE = Path("E:/MyCodeProjects/04-宝妈直播诊断系统/苏苏在浙里")
MODEL_CHDIR = DEFAULT_BASE
MODEL_RELPATH = "vosk_model/vosk-model-cn-kaldi-multicn-0.15"
POLL_SECONDS = 5

# 尝试导入说话人分离
try:
    from diarization_simple import diarize as _diarize
    HAS_DIARIZE = True
except ImportError:
    HAS_DIARIZE = False


def load_model():
    os.chdir(str(MODEL_CHDIR))
    print(f"[STT] Loading Vosk from {os.getcwd()}/{MODEL_RELPATH}")
    model = Model(MODEL_RELPATH)
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    return rec


def transcribe(rec, wav_path):
    wf = wave.open(str(wav_path), "rb")
    data = wf.readframes(wf.getnframes())
    wf.close()
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
    else:
        result = json.loads(rec.FinalResult())
    text = result.get("text", "").strip()
    words = result.get("result", []) if result.get("result") else []
    return text, words


def get_processed_ids(stt_log):
    if not stt_log.is_file():
        return set()
    seen = set()
    with open(stt_log, encoding="utf-8") as f:
        for line in f:
            try:
                seen.add(json.loads(line).get("source", ""))
            except json.JSONDecodeError:
                pass
    return seen


def process_audio_files(rec, audio_dir, stt_log):
    processed = get_processed_ids(stt_log)
    for wav in sorted(audio_dir.glob("audio_20*.wav")):
        if wav.name in processed:
            continue

        # 验证格式 (必须 16kHz mono)
        try:
            with wave.open(str(wav), "rb") as wf:
                if wf.getnchannels() != 1 or wf.getframerate() != 16000:
                    print(f"[STT] 跳过 {wav.name} — 非16kHz单声道")
                    continue
        except Exception as e:
            print(f"[STT] 跳过 {wav.name} — {e}")
            continue

        try:
            text, words = transcribe(rec, wav)
            record = {
                "timestamp": time.time(),
                "time": datetime.now().strftime("%H:%M:%S"),
                "source": wav.name,
                "text": text,
            }

            # 说话人分离 (如果可用且识别到文字)
            if HAS_DIARIZE and words and len(words) >= 3:
                try:
                    mono_wav = str(wav)
                    d_result = _diarize(mono_wav, words)
                    if d_result:
                        segments, speaker_count, _ = d_result
                        record["segments"] = segments
                        record["speaker_count"] = speaker_count
                        record["speakers"] = sorted(set(
                            s["speaker"] for s in segments
                        ))
                except Exception:
                    pass

            if words:
                record["words"] = words

            with open(stt_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            prefix = ""
            if "speakers" in record:
                prefix = f" [{','.join(record['speakers'])}]"
            preview = text[:120] if text else "(无声)"
            print(f"[STT] {record['time']}{prefix} — {preview}")

        except Exception as e:
            print(f"[STT] 错误 {wav.name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="STT处理器 v2.1")
    parser.add_argument("--target", help="数据目录, 默认苏苏在浙里")
    args = parser.parse_args()

    base = Path(args.target) if args.target else DEFAULT_BASE
    audio_dir = base / "audio"
    stt_log = base / "stt.jsonl"
    audio_dir.mkdir(parents=True, exist_ok=True)

    if HAS_DIARIZE:
        print("[STT] 说话人分离: 可用")
    else:
        print("[STT] 说话人分离: 不可用 (需 diarization_simple.py)")

    rec = load_model()
    print(f"[STT] 监控 {audio_dir}/  轮询间隔: {POLL_SECONDS}s")
    print(f"[STT] 输出: {stt_log}")

    while True:
        process_audio_files(rec, audio_dir, stt_log)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
