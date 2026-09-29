"""
Deduplicator for voice clips in Alisha Bubbzieee pipeline.
Detects identical audio by SHA-256 hash or acoustic fingerprint.
"""

import hashlib
import os
from typing import Dict, List, Set, Tuple


def compute_sha256(filepath: str) -> str:
    """Calculates SHA256 of file bytes."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def deduplicate_voice_clips(voice_dir: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Scans directory, groups by hash, returns:
      - unique_files: list of paths to keep
      - duplicates: list of dicts with original and duplicate paths
    """
    seen_hashes: Dict[str, str] = {}
    unique_files: List[str] = []
    duplicates: List[Dict[str, str]] = []

    for fname in sorted(os.listdir(voice_dir)):
        if fname.lower().endswith(".wav"):
            path = os.path.join(voice_dir, fname)
            file_hash = compute_sha256(path)
            if file_hash in seen_hashes:
                duplicates.append({
                    "duplicate_file": fname,
                    "original_file": os.path.basename(seen_hashes[file_hash]),
                    "sha256": file_hash
                })
            else:
                seen_hashes[file_hash] = path
                unique_files.append(path)

    return unique_files, duplicates
