"""
Audio Quality Analyzer for Alisha Bubbzieee Voice Pipeline.
Ultra-fast C-accelerated implementation using Python 3.11's built-in audioop.
Analyzes WAV files without external cloud dependencies.
Calculates SNR, RMS loudness (dBFS), clipping percentage, speech ratio, and duration.
Classifies clips into:
  - A (>= 0.80): Clean Speaker Core (primary TTS training)
  - B (0.55-0.79): Natural Speech (prosody & robustness)
  - C (0.30-0.54): Paralinguistic Archive (laughs, sighs, reactions)
  - R (< 0.30): Rejected
"""

import audioop
import math
import os
import wave
from typing import Dict, Any, List


def compute_audio_metrics(wav_path: str) -> Dict[str, Any]:
    """
    Computes all audio quality metrics for a given WAV file using C-accelerated audioop.
    """
    if not os.path.exists(wav_path):
        return {"error": f"File not found: {wav_path}", "quality_score": 0.0, "classification": "R"}

    with wave.open(wav_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    duration = n_frames / float(framerate) if framerate > 0 else 0.0
    if duration == 0 or len(raw_bytes) == 0:
        return {
            "file": os.path.basename(wav_path),
            "duration_sec": 0.0,
            "rms_dbfs": -100.0,
            "peak_dbfs": -100.0,
            "clipping_ratio": 0.0,
            "speech_ratio": 0.0,
            "snr_db": 0.0,
            "quality_score": 0.0,
            "classification": "R",
        }

    # If stereo, convert to mono
    if n_channels == 2:
        mono_bytes = audioop.tomono(raw_bytes, sampwidth, 0.5, 0.5)
    else:
        mono_bytes = raw_bytes

    # 1. Peak & RMS
    max_val = audioop.max(mono_bytes, sampwidth)
    max_possible = (1 << (8 * sampwidth - 1)) - 1
    peak_ratio = max_val / float(max_possible) if max_possible > 0 else 0.0
    peak_dbfs = 20 * math.log10(peak_ratio) if peak_ratio > 1e-5 else -100.0

    rms_val = audioop.rms(mono_bytes, sampwidth)
    rms_ratio = rms_val / float(max_possible) if max_possible > 0 else 0.0
    rms_dbfs = 20 * math.log10(rms_ratio) if rms_ratio > 1e-5 else -100.0

    # 2. Clipping estimation (samples >= 99.5% of max)
    # Using audioop findmax or byte scan
    clip_thresh = int(0.995 * max_possible)
    # Fast count
    clipping_ratio = 0.0
    if max_val >= clip_thresh:
        # Check clipping count in chunks
        clipped_count = 0
        step = sampwidth
        for i in range(0, len(mono_bytes), step):
            val = abs(int.from_bytes(mono_bytes[i:i+step], byteorder="little", signed=True))
            if val >= clip_thresh:
                clipped_count += 1
        clipping_ratio = clipped_count / float(n_frames)

    # 3. Frame-based analysis for VAD and SNR (30ms frames)
    frame_ms = 30
    frame_bytes_len = int((frame_ms / 1000.0) * framerate) * sampwidth
    if frame_bytes_len <= 0:
        frame_bytes_len = 720 * sampwidth

    frame_energies = []
    for i in range(0, len(mono_bytes) - frame_bytes_len + 1, frame_bytes_len // 2):
        chunk = mono_bytes[i:i + frame_bytes_len]
        f_rms = audioop.rms(chunk, sampwidth)
        f_ratio = f_rms / float(max_possible) if max_possible > 0 else 0.0
        f_db = 20 * math.log10(f_ratio) if f_ratio > 1e-5 else -100.0
        frame_energies.append(f_db)

    if not frame_energies:
        frame_energies = [rms_dbfs]

    sorted_energies = sorted(frame_energies)
    noise_idx = max(0, int(len(sorted_energies) * 0.15))
    noise_floor_db = sorted_energies[noise_idx]

    speech_threshold_db = max(noise_floor_db + 9.0, -44.0)
    speech_frames = [e for e in frame_energies if e >= speech_threshold_db]
    speech_ratio = len(speech_frames) / float(len(frame_energies))

    speech_avg_db = (
        sum(speech_frames) / float(len(speech_frames)) if speech_frames else rms_dbfs
    )
    snr_db = max(0.0, speech_avg_db - noise_floor_db)

    # 4. Normalized Quality Score
    # SNR norm (10dB to 25dB)
    snr_norm = min(1.0, max(0.0, (snr_db - 5.0) / 20.0))
    # Speech ratio norm
    speech_ratio_norm = min(1.0, max(0.0, speech_ratio / 0.85))

    # Loudness norm (-28 to -14 optimal)
    if -28.0 <= rms_dbfs <= -14.0:
        loudness_norm = 1.0
    elif rms_dbfs < -28.0:
        loudness_norm = max(0.0, 1.0 - (abs(rms_dbfs - (-28.0)) / 25.0))
    else:
        loudness_norm = max(0.0, 1.0 - ((rms_dbfs - (-14.0)) / 10.0))

    # Clipping penalty
    clipping_penalty = max(0.0, 1.0 - (clipping_ratio * 100.0))

    # Duration norm
    if 2.0 <= duration <= 35.0:
        duration_norm = 1.0
    elif duration < 2.0:
        duration_norm = max(0.2, duration / 2.0)
    else:
        duration_norm = max(0.5, 1.0 - ((duration - 35.0) / 100.0))

    quality_score = (
        (0.30 * snr_norm)
        + (0.25 * speech_ratio_norm)
        + (0.20 * loudness_norm)
        + (0.15 * clipping_penalty)
        + (0.10 * duration_norm)
    )
    quality_score = round(min(1.0, max(0.0, quality_score)), 4)

    if quality_score >= 0.78 and clipping_ratio < 0.005 and duration >= 2.0:
        classification = "A"
    elif quality_score >= 0.55:
        classification = "B"
    elif quality_score >= 0.30:
        classification = "C"
    else:
        classification = "R"

    return {
        "file": os.path.basename(wav_path),
        "duration_sec": round(duration, 3),
        "sample_rate": framerate,
        "rms_dbfs": round(rms_dbfs, 2),
        "peak_dbfs": round(peak_dbfs, 2),
        "clipping_ratio": round(clipping_ratio, 5),
        "speech_ratio": round(speech_ratio, 3),
        "snr_db": round(snr_db, 2),
        "noise_floor_db": round(noise_floor_db, 2),
        "quality_score": quality_score,
        "classification": classification,
    }


def analyze_directory(voice_dir: str) -> List[Dict[str, Any]]:
    results = []
    for fname in sorted(os.listdir(voice_dir)):
        if fname.lower().endswith(".wav"):
            path = os.path.join(voice_dir, fname)
            metrics = compute_audio_metrics(path)
            results.append(metrics)
    return results
