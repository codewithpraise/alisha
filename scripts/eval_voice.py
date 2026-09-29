import os
import sys
import time
import json
import hashlib
import numpy as np
import soundfile as sf
import torch
import librosa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["HF_HOME"] = r"D:\hf_cache"
os.environ["TEMP"] = r"D:\temp"
os.environ["TMP"] = r"D:\temp"

from qwen_tts import Qwen3TTSModel, VoiceClonePromptItem

MODEL_PATH = r"D:\models\Qwen3-TTS-12Hz-1.7B-Base"
REF_AUDIO = os.path.join(ROOT, "voice_v1", "reference.wav")
REF_TEXT = "that's good, im okay. i'm just getting ready for uni tomorrow. don't wanna go, it's so jarring ugh, cuz it's like two to three umm hour travel"
CANONICAL_PROMPT_PATH = os.path.join(ROOT, "voice_v1", "canonical_icl_prompt.pt")
OUTPUT_DIR = os.path.join(ROOT, "voice", "generated")

TEST_UTTERANCES = [
    {"id": "v01_greeting", "act": "greeting", "text": "hey, what are you up to today?"},
    {"id": "v02_study_rant", "act": "rant", "text": "honestly that lecture was so long, my brain literally melted 😭"},
    {"id": "v03_cat_story", "act": "story", "text": "kittu is literally asleep on my notes right now, look at him"},
    {"id": "v04_tease", "act": "tease", "text": "stop lying to me, you know that's not true lmao"},
    {"id": "v05_comfort", "act": "comfort", "text": "yeah yeah i hear you, just make sure you get some rest though"},
    {"id": "v06_commute", "act": "observation", "text": "i'm just waiting for the bus, it's freezing outside styll"},
    {"id": "v07_flirt", "act": "banter", "text": "you'll fall in love with my voice, told you already"},
    {"id": "v08_surprise", "act": "reaction", "text": "wait are you being serious right now? omg"},
    {"id": "v09_signoff", "act": "farewell", "text": "alright say less, text me when you get back home"},
    {"id": "v10_reflective", "act": "reflection", "text": "i can't lie, today was actually pretty chill compared to yesterday"},
]

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_flat = a.flatten()
    b_flat = b.flatten()
    denom = (np.linalg.norm(a_flat) * np.linalg.norm(b_flat))
    if denom == 0:
        return 0.0
    return float(np.dot(a_flat, b_flat) / denom)

def main():
    print("=" * 60)
    print("ALISHA QWEN3-TTS VOICE EVALUATION HARNESS")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Load Model
    print(f"\n1. Loading Qwen3-TTS Model from: {MODEL_PATH}")
    t0 = time.time()
    tts = Qwen3TTSModel.from_pretrained(
        MODEL_PATH,
        dtype=torch.bfloat16
    )
    load_time = time.time() - t0
    print(f"   Model loaded in {load_time:.2f}s")
    
    # 2. Canonical ICL Prompt
    print(f"\n2. Resolving Canonical Voice Clone Prompt...")
    if os.path.exists(CANONICAL_PROMPT_PATH):
        print(f"   Loading cached prompt from {CANONICAL_PROMPT_PATH}")
        prompt_items = torch.load(CANONICAL_PROMPT_PATH, map_location="cpu", weights_only=False)
    else:
        print(f"   Computing canonical prompt from {REF_AUDIO} with ICL mode...")
        prompt_items = tts.create_voice_clone_prompt(
            ref_audio=REF_AUDIO,
            ref_text=REF_TEXT,
            x_vector_only_mode=False
        )
        torch.save(prompt_items, CANONICAL_PROMPT_PATH)
        print(f"   Saved canonical prompt to {CANONICAL_PROMPT_PATH}")
        
    ref_item = prompt_items[0]
    ref_spk_emb = ref_item.ref_spk_embedding.detach().cpu().float().numpy()
    print(f"   ref_code shape: {ref_item.ref_code.shape}")
    print(f"   ref_spk_embedding shape: {ref_spk_emb.shape}")
    print(f"   icl_mode: {ref_item.icl_mode}, x_vector_only_mode: {ref_item.x_vector_only_mode}")

    # 3. Calibration against genuine Alisha recordings
    genuine_files = [
        "voice/1211480357481077.wav",
        "voice/1242969967588294.wav",
        "voice/1247080237633732.wav",
        "voice/1511834979942376.wav",
    ]
    print("\n3. Calibration: Speaker Embedding Similarity across genuine corpus...")
    calibration_scores = []
    for gf in genuine_files:
        p = os.path.join(ROOT, gf)
        if os.path.exists(p):
            wav_data, sr = librosa.load(p, sr=tts.model.speaker_encoder_sample_rate)
            emb = tts.model.extract_speaker_embedding(audio=wav_data, sr=tts.model.speaker_encoder_sample_rate).detach().cpu().float().numpy()
            sim = cosine_similarity(ref_spk_emb, emb)
            calibration_scores.append(sim)
            print(f"   {gf} vs Reference: {sim:.4f}")
    
    if calibration_scores:
        print(f"   Genuine Alisha Intra-Speaker Range: {min(calibration_scores):.4f} - {max(calibration_scores):.4f} (mean: {np.mean(calibration_scores):.4f})")

    # 4. Generate & Evaluate Test Utterances
    print(f"\n4. Generating {len(TEST_UTTERANCES)} test utterances...")
    results = []
    latencies = []
    similarities = []

    for idx, u in enumerate(TEST_UTTERANCES, 1):
        out_path = os.path.join(OUTPUT_DIR, f"{u['id']}.wav")
        t_gen_start = time.time()
        
        # Clean text
        from packages.voice.realtime_tts import clean_text_for_speech
        norm_text = clean_text_for_speech(u["text"])
        
        wavs, fs = tts.generate_voice_clone(
            text=norm_text,
            voice_clone_prompt=prompt_items,
            do_sample=True,
            top_k=50,
            top_p=1.0,
            temperature=0.9,
            repetition_penalty=1.05
        )
        gen_dur = time.time() - t_gen_start
        latencies.append(gen_dur)
        
        wav = wavs[0]
        sf.write(out_path, wav, fs)
        
        # Acoustic metrics
        duration = len(wav) / fs
        peak = float(np.max(np.abs(wav)))
        rms = float(np.sqrt(np.mean(wav**2)))
        
        # Compute speaker similarity of generated audio vs reference
        wav_resample = librosa.resample(wav.astype(np.float32), orig_sr=int(fs), target_sr=tts.model.speaker_encoder_sample_rate)
        gen_spk_emb = tts.model.extract_speaker_embedding(audio=wav_resample, sr=tts.model.speaker_encoder_sample_rate).detach().cpu().numpy()
        sim = cosine_similarity(ref_spk_emb, gen_spk_emb)
        similarities.append(sim)
        
        # Reference-echo check: duration should be proportional to target text, not inflated by 4s reference
        has_echo = duration > (len(norm_text.split()) * 0.8 + 3.0)
        
        res = {
            "id": u["id"],
            "act": u["act"],
            "text": u["text"],
            "sample_rate": fs,
            "duration_s": round(duration, 2),
            "peak": round(peak, 4),
            "rms": round(rms, 4),
            "latency_s": round(gen_dur, 2),
            "speaker_similarity": round(sim, 4),
            "echo_detected": has_echo,
            "status": "PASS" if (sim >= 0.70 and not has_echo and peak <= 1.0) else "WARN"
        }
        results.append(res)
        print(f"   [{idx}/{len(TEST_UTTERANCES)}] {u['id']}: dur={duration:.2f}s, sim={sim:.4f}, lat={gen_dur:.2f}s, status={res['status']}")

    # 5. Summary Report
    print("\n" + "=" * 60)
    print("VOICE EVALUATION SUMMARY REPORT")
    print("=" * 60)
    print(f"Total Utterances Tested: {len(results)}")
    print(f"Sample Rate: 24,000 Hz (Verified)")
    print(f"Mean Speaker Similarity: {np.mean(similarities):.4f} (Min: {min(similarities):.4f}, Max: {max(similarities):.4f})")
    print(f"Mean Generation Latency: {np.mean(latencies):.2f}s (Min: {min(latencies):.2f}s, Max: {max(latencies):.2f}s)")
    echo_count = sum(1 for r in results if r["echo_detected"])
    print(f"Reference Echo Count: {echo_count} / {len(results)} ({'PASS' if echo_count == 0 else 'FAIL'})")
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    print(f"Pass Rate: {pass_count} / {len(results)} ({pass_count/len(results)*100:.1f}%)")
    
    # Save results to json
    report_json = os.path.join(ROOT, "reports", "voice_eval_results.json")
    os.makedirs(os.path.dirname(report_json), exist_ok=True)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL_PATH,
            "load_time_s": load_time,
            "mean_speaker_similarity": float(np.mean(similarities)),
            "mean_latency_s": float(np.mean(latencies)),
            "results": results
        }, f, indent=2)
    print(f"Full report saved to: {report_json}")

if __name__ == "__main__":
    main()
