"""
diarization_simple.py — 轻量级双人说话人分离
无网络环境, 基于频谱特征 + KMeans 聚类
配合 stt_processor.py 使用
"""
import numpy as np
from scipy.io import wavfile
from sklearn.cluster import KMeans

def spectral_features(samples, sr, start_sec, end_sec):
    """提取一段音频的频谱特征"""
    start_s = int(start_sec * sr)
    end_s = int(end_sec * sr)
    segment = samples[start_s:end_s]
    if len(segment) < 100:
        return None

    # 转为单声道
    if segment.ndim > 1:
        segment = segment.mean(axis=1)

    # RMS能量
    rms = float(np.sqrt(np.mean(segment.astype(float)**2)))
    if rms < 1:  # 静音段跳过
        return None

    # FFT 频谱
    fft = np.fft.rfft(segment.astype(float))
    freqs = np.fft.rfftfreq(len(segment), 1/sr)
    mag = np.abs(fft)

    if mag.sum() == 0:
        return None

    # 频谱质心 (平均频率)
    centroid = float(np.sum(freqs * mag) / mag.sum())

    # 频谱带宽 (标准差)
    bandwidth = float(np.sqrt(np.sum(((freqs - centroid)**2) * mag) / mag.sum()))

    # 低频能量比 (0-1kHz / total)
    low_mask = freqs < 1000
    low_ratio = float(mag[low_mask].sum() / mag.sum()) if mag.sum() > 0 else 0

    # 零交叉率
    zcr = float(np.sum(np.abs(np.diff(np.sign(segment)))) / (2 * len(segment)))

    return np.array([rms, centroid / 1000, bandwidth / 1000, low_ratio * 100, zcr * 1000])


def diarize(wav_path, words, n_speakers=2):
    """
    对Vosk词级结果做简单双人分离
    返回: [{"start","end","text","speaker"}, ...]
    """
    if not words or len(words) < 3:
        return None

    try:
        sr, samples = wavfile.read(wav_path)
    except:
        return None

    # 为每个词提取特征
    features = []
    valid_words = []
    for w in words:
        feat = spectral_features(samples, sr, w["start"], w["end"])
        if feat is not None:
            features.append(feat)
            valid_words.append(w)

    if len(valid_words) < 3:
        return None

    # KMeans 聚类
    X = np.array(features)
    n_clusters = min(n_speakers, len(set(tuple(f) for f in X)))
    if n_clusters < 2:
        return None

    km = KMeans(n_clusters=n_clusters, n_init=3, random_state=0)
    labels = km.fit_predict(X)

    # 分组并构建说话人段
    speaker_words = {}
    for i, w in enumerate(valid_words):
        spk = int(labels[i])
        if spk not in speaker_words:
            speaker_words[spk] = []
        speaker_words[spk].append(w)

    # 合并同一说话人的相邻词
    segments = []
    for spk in sorted(speaker_words.keys()):
        ws = sorted(speaker_words[spk], key=lambda x: x["start"])
        seg = {"start": ws[0]["start"], "end": ws[0]["end"],
               "text": ws[0]["word"], "speaker": f"speaker_{spk+1}"}
        for w in ws[1:]:
            gap = w["start"] - seg["end"]
            if gap > 0.5:  # 大间隔切新段
                segments.append(seg)
                seg = {"start": w["start"], "end": w["end"],
                       "text": w["word"], "speaker": f"speaker_{spk+1}"}
            else:
                seg["end"] = w["end"]
                seg["text"] += w["word"]
        segments.append(seg)

    # 相邻同说话人合并
    merged = []
    for s in segments:
        if merged and merged[-1]["speaker"] == s["speaker"]:
            gap = s["start"] - merged[-1]["end"]
            if gap < 1.0:
                merged[-1]["end"] = s["end"]
                merged[-1]["text"] += s["text"]
                continue
        merged.append(s)

    speakers_found = len(set(s["speaker"] for s in merged))
    return merged, speakers_found, sr
