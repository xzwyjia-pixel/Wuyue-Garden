"""
audio_capture.py — v2.0 音频监控升级版
WASAPI loopback -> VAD -> AGC -> 16kHz mono WAV
去无声, 自动增益, ASCII电平表 (兼容GBK)
配合 stt_processor.py v2.1 使用
"""
import pyaudiowpatch as pyaudio
import wave, time, os, threading, sys, math, signal, traceback
from datetime import datetime
from pathlib import Path
import numpy as np

OUT_DIR = Path("E:/MyCodeProjects/04-宝妈直播诊断系统/苏苏在浙里/audio")

CHUNK_SECONDS = 15
TARGET_SR = 16000
TARGET_CHANNELS = 1
VAD_THRESHOLD = 0.003
AGC_TARGET_RMS = 0.15
AGC_MAX_GAIN = 5.0
MAX_FILES = 480
METER_INTERVAL_SEC = 1

# 强制 UTF-8 输出, 避免 GBK 编码错误
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


class AudioCaptureV2:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.loopback = self.p.get_default_wasapi_loopback()
        self.device_rate = int(self.loopback['defaultSampleRate'])
        self.device_channels = self.loopback['maxInputChannels']
        self.running = True
        self.total_saved = 0
        self.total_skipped = 0

        print(f"[audio] device: {self.loopback['name']}")
        print(f"[audio] rate: {self.device_rate}Hz -> {TARGET_SR}Hz")
        print(f"[audio] channels: {self.device_channels} -> 1")
        print(f"[audio] VAD:{VAD_THRESHOLD} AGC:{AGC_TARGET_RMS}")
        print(f"[audio] chunk:{CHUNK_SECONDS}s max_files:{MAX_FILES}({MAX_FILES*CHUNK_SECONDS//60}min)")
        print(f"[audio] output: {OUT_DIR}")

    # -- signal processing --

    @staticmethod
    def _resample(data, orig_rate, target_rate):
        if orig_rate == target_rate:
            return data
        n_orig = len(data)
        n_target = int(n_orig * target_rate / orig_rate)
        indices = np.linspace(0, n_orig - 1, n_target)
        return np.interp(indices, np.arange(n_orig), data).astype(np.float64)

    @staticmethod
    def _to_mono(data, channels):
        if channels == 1:
            return data.astype(np.float64)
        frames = data.reshape(-1, channels).astype(np.float64)
        return frames.mean(axis=1)

    @staticmethod
    def _apply_agc(data, target_rms_norm, max_gain):
        data_f = data.astype(np.float64)
        rms = np.sqrt(np.mean(data_f ** 2))
        if rms < 1.0:
            return data, rms
        gain = min(target_rms_norm * 32768.0 / rms, max_gain)
        result = np.clip(np.round(data_f * gain), -32768, 32767).astype(np.int16)
        return result, rms

    @staticmethod
    def _rms_bar(norm_rms, width=40):
        """ASCII 电平表, GBK安全"""
        filled = max(0, min(width, int(norm_rms * width * 15)))
        return "#" * filled + "-" * (width - filled)

    # -- file mgmt --

    @staticmethod
    def _cleanup(audio_dir):
        files = sorted(audio_dir.glob("audio_20*.wav"))
        while len(files) > MAX_FILES:
            files[0].unlink(missing_ok=True)
            files = files[1:]

    # -- capture loop --

    def capture_loop(self):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        consecutive_errors = 0
        reconnect_delay = 1

        while self.running:
            try:
                self._capture_inner()
            except Exception as e:
                consecutive_errors += 1
                print(f"[audio] 采集崩溃: {e}")
                traceback.print_exc()
                if consecutive_errors >= 5:
                    print("[audio] 连续5次错误, 等待60s...")
                    time.sleep(60)
                    consecutive_errors = 0
                else:
                    print(f"[audio] 等待{reconnect_delay}s后重连...")
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 30)
                # Re-initialize PyAudio
                try:
                    self.p.terminate()
                except:
                    pass
                time.sleep(1)
                try:
                    self.p = pyaudio.PyAudio()
                    self.loopback = self.p.get_default_wasapi_loopback()
                    self.device_rate = int(self.loopback['defaultSampleRate'])
                    self.device_channels = self.loopback['maxInputChannels']
                    print(f"[audio] 重新连接: {self.loopback['name']}")
                except Exception as e2:
                    print(f"[audio] 重连失败: {e2}")

    def _capture_inner(self):

        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.device_channels,
            rate=self.device_rate,
            input=True,
            input_device_index=self.loopback['index'],
            frames_per_buffer=1024,
        )

        # ---- 噪声底噪校准 (前 3s) ----
        print("[audio] 校准环境噪声...", end=" ", flush=True)
        noise_samples = []
        for _ in range(30):
            data = stream.read(1024, exception_on_overflow=False)
            raw = np.frombuffer(data, dtype=np.int16).astype(np.float64)
            mono = self._to_mono(raw, self.device_channels)
            rms = np.sqrt(np.mean(mono ** 2)) / 32768.0
            noise_samples.append(rms)
        noise_floor = float(np.mean(noise_samples))
        # 自适应 VAD: noise_floor * 1.5, 但不低于 0.002
        adaptive_threshold = max(noise_floor * 1.5, 0.002)
        print(f"noise_floor={noise_floor:.4f} VAD={adaptive_threshold:.4f}")
        # 首次: 5s 快 chunk + 强制保存 (快速出首条数据)
        first_fast = True
        first_force_save = True

        meter_count = 0

        while self.running:
            current_chunk = 5 if first_fast else CHUNK_SECONDS
            chunk_size = int(self.device_rate / 1024 * current_chunk)
            frames = []
            for _ in range(chunk_size):
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)
                except Exception:
                    break

            if not frames:
                continue

            # PCM -> mono -> resample to 16kHz
            raw = np.frombuffer(b''.join(frames), dtype=np.int16)
            mono = self._to_mono(raw, self.device_channels)
            signal = self._resample(mono, self.device_rate, TARGET_SR)
            del raw, mono

            # RMS + VAD
            rms_val = np.sqrt(np.mean(signal ** 2))
            norm_rms = rms_val / 32768.0
            bar = self._rms_bar(norm_rms)
            stamp = datetime.now().strftime("%H:%M:%S")

            # 首次强制保存; 之后按自适应 VAD
            if not first_force_save and norm_rms < adaptive_threshold:
                self.total_skipped += 1
                if meter_count % 3 == 0:
                    print(f"[audio] {stamp} skip |{bar}| "
                          f"RMS:{norm_rms:.4f} skip:{self.total_skipped}",
                          end="\r" if self.running else "\n")
                meter_count += 1
                continue

            # AGC
            processed, orig_rms = self._apply_agc(
                signal.astype(np.int16), AGC_TARGET_RMS, AGC_MAX_GAIN
            )

            # save
            fname = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            path = OUT_DIR / fname
            with wave.open(str(path), 'wb') as wf:
                wf.setnchannels(TARGET_CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(TARGET_SR)
                wf.writeframes(processed.tobytes())

            size_kb = path.stat().st_size // 1024
            gain_db = 20 * math.log10(
                max(AGC_TARGET_RMS * 32768.0 / max(orig_rms, 1.0), 1)
            ) if orig_rms > 0 else 0
            self.total_saved += 1
            first_fast = False
            first_force_save = False

            print(f"[audio] {stamp} OK |{bar}| {size_kb}KB  "
                  f"RMS:{norm_rms:.3f} Gain:{gain_db:+.1f}dB  "
                  f"save:{self.total_saved} skip:{self.total_skipped}  ")

            self._cleanup(OUT_DIR)
            meter_count = 0

        stream.stop_stream()
        stream.close()
        print(f"\n[audio] stop. total:{self.total_saved} skip:{self.total_skipped}")

    def start(self):
        t = threading.Thread(target=self.capture_loop, daemon=True)
        t.start()
        return t

    def stop(self):
        self.running = False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="audio capture v2")
    parser.add_argument("--target", help="data dir")
    parser.add_argument("--chunk", type=int, default=CHUNK_SECONDS)
    parser.add_argument("--vad", type=float, default=VAD_THRESHOLD)
    parser.add_argument("--agc", type=float, default=AGC_TARGET_RMS)
    parser.add_argument("--max-files", type=int, default=MAX_FILES)
    args = parser.parse_args()

    if args.target:
        OUT_DIR = Path(args.target) / "audio"
    CHUNK_SECONDS = args.chunk
    VAD_THRESHOLD = args.vad
    AGC_TARGET_RMS = args.agc
    MAX_FILES = args.max_files

    _cap = None
    def _sig(s, f):
        print("\n[audio] 收到停止信号")
        if _cap:
            _cap.stop()
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)

    while True:
        try:
            _cap = AudioCaptureV2()
            cap = _cap
            print("[audio] start capture")
            cap.start().join()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[audio] 启动失败: {e}")
            traceback.print_exc()
            time.sleep(5)
