"""
Main entrypoint to run Phase 1: Voice Data Refinery.
Audits all 100 WAV clips, analyzes quality, deduplicates,
segments long clips, generates train/val/test manifests,
selects reference audio, and builds voice_report.html.
"""

import os
import sys

# Ensure package imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from packages.pipeline.quality_analyzer import analyze_directory
from packages.pipeline.deduplicator import deduplicate_voice_clips
from packages.pipeline.manifest_builder import build_pipeline_manifests
from packages.pipeline.transcribe import run_transcription_batch


def main():
    voice_dir = os.path.join(root_dir, "voice")
    data_dir = os.path.join(root_dir, "data")
    refs_dir = os.path.join(root_dir, "data", "refs")
    transcript_txt_dir = os.path.join(root_dir, "data", "transcript_asr")
    transcript_meta_dir = os.path.join(root_dir, "data", "transcript_meta")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(refs_dir, exist_ok=True)

    print("==================================================")
    print("      ALISHA BUBBZIEEE — VOICE DATA REFINERY      ")
    print("==================================================")

    # 1. Deduplication
    print("\n[Step 1/4] Running SHA-256 Deduplication...")
    unique_files, duplicates = deduplicate_voice_clips(voice_dir)
    print(f"-> Total WAV files: {len(unique_files) + len(duplicates)}")
    print(f"-> Unique clips: {len(unique_files)}, Duplicates found: {len(duplicates)}")

    # 2. Quality Analysis
    print("\n[Step 2/4] Running Audio Quality & SNR Analyzer...")
    quality_scores = analyze_directory(voice_dir)
    class_counts = {"A": 0, "B": 0, "C": 0, "R": 0}
    for q in quality_scores:
        cls = q.get("classification", "R")
        class_counts[cls] = class_counts.get(cls, 0) + 1

    print("-> Quality Classification Results:")
    print(f"   Class A (Clean Speaker Core):    {class_counts.get('A', 0)}")
    print(f"   Class B (Natural Speech):        {class_counts.get('B', 0)}")
    print(f"   Class C (Paralinguistic):        {class_counts.get('C', 0)}")
    print(f"   Class R (Rejected):              {class_counts.get('R', 0)}")

    # 3. Transcription metadata
    print("\n[Step 3/4] Initializing Transcription & Manifest System...")
    run_transcription_batch(voice_dir, transcript_meta_dir, transcript_txt_dir)

    # 4. Manifest Builder & Report Generation
    print("\n[Step 4/4] Building Train/Val/Test Splits & Listening Gallery...")
    manifest_results = build_pipeline_manifests(
        voice_dir=voice_dir,
        quality_scores=quality_scores,
        output_data_dir=data_dir,
        refs_dir=refs_dir,
    )

    print("\n=== PHASE 1 DELIVERABLES READY ===")
    print(f"1. Quality Manifest:    {manifest_results['quality_manifest']}")
    print(f"2. Train Split (70%):   {manifest_results['train_manifest']} ({manifest_results['train_count']} clips)")
    print(f"3. Val Split (15%):     {manifest_results['val_manifest']} ({manifest_results['val_count']} clips)")
    print(f"4. Test Split (15%):    {manifest_results['test_manifest']} ({manifest_results['test_count']} clips)")
    print(f"5. Interactive Report:  {manifest_results['report_html']}")
    print(f"6. Reference Voices:    {list(manifest_results['references'].keys())}")
    print("==================================================\n")


if __name__ == "__main__":
    main()
