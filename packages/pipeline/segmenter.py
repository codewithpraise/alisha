"""
Voice Segmenter for Alisha Bubbzieee.
For clips > 15 seconds, detects natural pauses (> 0.7s) and segments them into
clean utterance units suitable for TTS fine-tuning.
"""

import math
import os
import struct
import wave
from typing import List, Tuple


def find_pause_boundaries(
    samples: List[float],
    sample_rate: int,
    frame_ms: int = 30,
    min_silence_ms: int = 700,
    silence_threshold_db: float = -38.0,
) -> List[Tuple[float, float]]:
    """
    Finds speech utterance segments [start_sec, end_sec].
    """
    frame_size = int(frame_ms * sample_rate / 1000)
    if frame_size <= 0:
        frame_size = 720
    hop_size = frame_size // 2

    # Compute frame energy
    energies = []
    times = []
    for i in range(0, len(samples) - frame_size + 1, hop_size):
        frame = samples[i:i + frame_size]
        f_rms = math.sqrt(sum(s * s for s in frame) / float(frame_size))
        f_db = 20 * math.log10(f_rms) if f_rms > 1e-6 else -100.0
        energies.append(f_db)
        times.append(i / float(sample_rate))

    # Mark speech vs silence
    is_speech = [e >= silence_threshold_db for e in energies]

    # Convert to segments
    min_silence_frames = int(min_silence_ms / (hop_size * 1000.0 / sample_rate))
    segments = []
    in_speech = False
    start_time = 0.0
    silence_count = 0

    for idx, speech in enumerate(is_speech):
        t = times[idx]
        if speech:
            if not in_speech:
                in_speech = True
                start_time = max(0.0, t - 0.1)  # small lead-in margin
            silence_count = 0
        else:
            if in_speech:
                silence_count += 1
                if silence_count >= min_silence_frames:
                    in_speech = False
                    end_time = t
                    if end_time - start_time >= 1.5:  # at least 1.5s
                        segments.append((start_time, end_time))
                    silence_count = 0

    if in_speech:
        end_time = len(samples) / float(sample_rate)
        if end_time - start_time >= 1.5:
            segments.append((start_time, end_time))

    return segments


def segment_wav_file(
    input_wav: str,
    output_dir: str,
    max_duration_threshold: float = 15.0,
) -> List[str]:
    """
    If input_wav duration > max_duration_threshold, segments it and writes to output_dir.
    Returns list of paths created (or original if not segmented).
    """
    os.makedirs(output_dir, exist_ok=True)

    with wave.open(input_wav, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    duration = n_frames / float(framerate) if framerate > 0 else 0.0

    if duration <= max_duration_threshold:
        return [input_wav]

    # Decode mono float samples for boundary detection
    total_samples = n_frames * n_channels
    if sampwidth == 2:
        fmt = f"<{total_samples}h"
        int_samples = struct.unpack(fmt, raw_bytes)
        mono_samples = [int_samples[i * n_channels] / 32768.0 for i in range(n_frames)]
    else:
        mono_samples = [0.0] * n_frames

    segments = find_pause_boundaries(mono_samples, framerate)
    if not segments or len(segments) <= 1:
        return [input_wav]

    base_id = os.path.splitext(os.path.basename(input_wav))[0]
    output_files = []

    bytes_per_frame = n_channels * sampwidth

    for seg_idx, (start_sec, end_sec) in enumerate(segments, 1):
        start_frame = max(0, int(start_sec * framerate))
        end_frame = min(n_frames, int(end_sec * framerate))
        seg_bytes = raw_bytes[start_frame * bytes_per_frame : end_frame * bytes_per_frame]

        out_fname = f"{base_id}_{seg_idx:03d}.wav"
        out_path = os.path.join(output_dir, out_fname)

        with wave.open(out_path, "wb") as out_wf:
            out_wf.setnchannels(n_channels)
            out_wf.setsampwidth(sampwidth)
            out_wf.setframerate(framerate)
            out_wf.writeframes(seg_bytes)

        output_files.append(out_path)

    return output_files
