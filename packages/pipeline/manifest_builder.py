"""
Manifest Builder & Report Generator for Alisha Bubbzieee.
Generates:
  - data/quality_manifest.jsonl
  - data/voice_train.jsonl (70%)
  - data/voice_val.jsonl (15%)
  - data/voice_test.jsonl (15%)
  - data/voice_report.html (Interactive audio listening gallery + metrics)
"""

import json
import os
import random
import shutil
from typing import List, Dict, Any


def build_pipeline_manifests(
    voice_dir: str,
    quality_scores: List[Dict[str, Any]],
    output_data_dir: str,
    refs_dir: str,
    seed: int = 42,
) -> Dict[str, Any]:
    os.makedirs(output_data_dir, exist_ok=True)
    os.makedirs(refs_dir, exist_ok=True)

    # 1. Write quality manifest
    quality_manifest_path = os.path.join(output_data_dir, "quality_manifest.jsonl")
    with open(quality_manifest_path, "w", encoding="utf-8") as f:
        for item in quality_scores:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # 2. Select Reference Clips (A-grade, 5s to 15s, top SNR)
    a_grade_candidates = [
        item for item in quality_scores
        if item.get("classification") == "A" and 5.0 <= item.get("duration_sec", 0) <= 18.0
    ]
    # Fallback to B-grade if few A-grades
    if len(a_grade_candidates) < 3:
        a_grade_candidates = [
            item for item in quality_scores
            if item.get("classification") in ("A", "B") and 4.0 <= item.get("duration_sec", 0) <= 20.0
        ]
    # Sort by quality score descending
    a_grade_candidates.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

    ref_clips = {}
    ref_names = ["ref_neutral.wav", "ref_casual.wav", "ref_expressive.wav"]
    for i, name in enumerate(ref_names):
        if i < len(a_grade_candidates):
            source_file = a_grade_candidates[i]["file"]
            src_path = os.path.join(voice_dir, source_file)
            dst_path = os.path.join(refs_dir, name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                ref_clips[name] = {
                    "source_clip": source_file,
                    "quality_score": a_grade_candidates[i]["quality_score"],
                    "duration_sec": a_grade_candidates[i]["duration_sec"],
                }

    # 3. Partition train / val / test (70 / 15 / 15)
    # Filter out rejected clips (R) from primary train sets
    trainable_clips = [
        item for item in quality_scores if item.get("classification") in ("A", "B", "C")
    ]
    rng = random.Random(seed)
    shuffled = list(trainable_clips)
    rng.shuffle(shuffled)

    n_total = len(shuffled)
    n_train = int(n_total * 0.70)
    n_val = int(n_total * 0.15)

    train_set = shuffled[:n_train]
    val_set = shuffled[n_train:n_train + n_val]
    test_set = shuffled[n_train + n_val:]

    def write_split(split_name: str, split_items: List[Dict[str, Any]]) -> str:
        out_path = os.path.join(output_data_dir, f"voice_{split_name}.jsonl")
        with open(out_path, "w", encoding="utf-8") as f:
            for item in split_items:
                fname = item["file"]
                cid = os.path.splitext(fname)[0]
                entry = {
                    "id": cid,
                    "audio": f"voice/{fname}",
                    "duration_sec": item.get("duration_sec"),
                    "quality_score": item.get("quality_score"),
                    "classification": item.get("classification"),
                    "ref_audio": f"refs/{ref_names[0]}" if ref_clips else "",
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return out_path

    train_path = write_split("train", train_set)
    val_path = write_split("val", val_set)
    test_path = write_split("test", test_set)

    # 4. Generate voice_report.html
    report_html_path = os.path.join(output_data_dir, "voice_report.html")
    generate_listening_gallery_html(quality_scores, ref_clips, report_html_path)

    return {
        "total_clips": len(quality_scores),
        "train_count": len(train_set),
        "val_count": len(val_set),
        "test_count": len(test_set),
        "rejected_count": len(quality_scores) - len(trainable_clips),
        "references": ref_clips,
        "train_manifest": train_path,
        "val_manifest": val_path,
        "test_manifest": test_path,
        "quality_manifest": quality_manifest_path,
        "report_html": report_html_path,
    }


def generate_listening_gallery_html(
    quality_scores: List[Dict[str, Any]],
    ref_clips: Dict[str, Any],
    out_path: str,
):
    """Generates a standalone, beautiful HTML listening gallery with audio players and stats."""
    count_a = sum(1 for q in quality_scores if q.get("classification") == "A")
    count_b = sum(1 for q in quality_scores if q.get("classification") == "B")
    count_c = sum(1 for q in quality_scores if q.get("classification") == "C")
    count_r = sum(1 for q in quality_scores if q.get("classification") == "R")
    total_dur = sum(q.get("duration_sec", 0) for q in quality_scores)
    avg_score = sum(q.get("quality_score", 0) for q in quality_scores) / max(1, len(quality_scores))

    cards_html = []
    for item in quality_scores:
        fname = item["file"]
        cls = item.get("classification", "B")
        score = item.get("quality_score", 0.0)
        dur = item.get("duration_sec", 0.0)
        snr = item.get("snr_db", 0.0)
        rms = item.get("rms_dbfs", 0.0)
        clip_pct = item.get("clipping_ratio", 0.0) * 100.0

        badge_color = {
            "A": "#5E7A68",  # Sage
            "B": "#D4A853",  # Amber
            "C": "#A38671",  # Warm taupe
            "R": "#C47067",  # Muted rose
        }.get(cls, "#D4A853")

        cards_html.append(f"""
        <div class="clip-card" data-class="{cls}">
          <div class="clip-header">
            <span class="clip-name">{fname}</span>
            <span class="badge" style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}44;">Class {cls} ({score:.2f})</span>
          </div>
          <div class="audio-wrap">
            <audio controls preload="none" src="../voice/{fname}"></audio>
          </div>
          <div class="metrics-grid">
            <div class="metric"><span class="lbl">Duration</span><span class="val">{dur:.1f}s</span></div>
            <div class="metric"><span class="lbl">SNR</span><span class="val">{snr:.1f} dB</span></div>
            <div class="metric"><span class="lbl">RMS</span><span class="val">{rms:.1f} dBFS</span></div>
            <div class="metric"><span class="lbl">Clipping</span><span class="val">{clip_pct:.2f}%</span></div>
          </div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Alisha Bubbzieee — Voice Refinery Report</title>
  <style>
    :root {{
      --bg: #111210;
      --card-bg: #1B1C1A;
      --text: #F2EFE8;
      --muted: #8A8880;
      --border: #2C2D2A;
      --amber: #D4A853;
      --sage: #5E7A68;
      --rose: #C47067;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 32px 20px;
      line-height: 1.5;
    }}
    .container {{ max-width: 1080px; margin: 0 auto; }}
    header {{ margin-bottom: 32px; border-bottom: 1px solid var(--border); padding-bottom: 24px; }}
    h1 {{ font-family: "Instrument Serif", Georgia, serif; font-size: 38px; font-weight: normal; color: var(--text); margin-bottom: 8px; }}
    .subtitle {{ color: var(--muted); font-size: 14px; letter-spacing: 0.05em; }}
    
    .stats-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }}
    .stat-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .stat-val {{ font-size: 26px; font-weight: 600; color: var(--amber); margin-bottom: 4px; }}
    .stat-lbl {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}

    .filter-bar {{
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }}
    .filter-btn {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.2s;
    }}
    .filter-btn:hover, .filter-btn.active {{
      border-color: var(--amber);
      color: var(--amber);
    }}

    .clips-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 18px;
    }}
    .clip-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      transition: border-color 0.2s;
    }}
    .clip-card:hover {{ border-color: #444; }}
    .clip-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .clip-name {{ font-size: 12px; font-family: monospace; color: var(--muted); }}
    .badge {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }}
    .audio-wrap audio {{ width: 100%; height: 32px; margin-bottom: 12px; }}
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      background: #141513;
      padding: 8px;
      border-radius: 6px;
    }}
    .metric {{ text-align: center; }}
    .metric .lbl {{ display: block; font-size: 10px; color: var(--muted); }}
    .metric .val {{ font-size: 11px; font-weight: 600; color: var(--text); }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Alisha Bubbzieee — Voice Refinery</h1>
      <p class="subtitle">100 CLIPS AUDITED &middot; ZERO EXTERNAL CLOUD &middot; SPEECH QUALITY ANALYSIS</p>
    </header>

    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-val">{len(quality_scores)}</div>
        <div class="stat-lbl">Total Clips</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">{total_dur/60.0:.1f}m</div>
        <div class="stat-lbl">Total Speech</div>
      </div>
      <div class="stat-box">
        <div class="stat-val" style="color: var(--sage)">{count_a}</div>
        <div class="stat-lbl">Class A (Core)</div>
      </div>
      <div class="stat-box">
        <div class="stat-val" style="color: var(--amber)">{count_b}</div>
        <div class="stat-lbl">Class B (Natural)</div>
      </div>
      <div class="stat-box">
        <div class="stat-val" style="color: #A38671">{count_c}</div>
        <div class="stat-lbl">Class C (Paralinguistic)</div>
      </div>
      <div class="stat-box">
        <div class="stat-val" style="color: var(--rose)">{count_r}</div>
        <div class="stat-lbl">Class R (Rejected)</div>
      </div>
    </div>

    <div class="filter-bar">
      <button class="filter-btn active" onclick="filterClips('ALL')">All Clips ({len(quality_scores)})</button>
      <button class="filter-btn" onclick="filterClips('A')">Class A: Core ({count_a})</button>
      <button class="filter-btn" onclick="filterClips('B')">Class B: Natural ({count_b})</button>
      <button class="filter-btn" onclick="filterClips('C')">Class C: Paralinguistic ({count_c})</button>
      <button class="filter-btn" onclick="filterClips('R')">Class R: Rejected ({count_r})</button>
    </div>

    <div class="clips-grid" id="clipsGrid">
      {''.join(cards_html)}
    </div>
  </div>

  <script>
    function filterClips(cls) {{
      document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');
      document.querySelectorAll('.clip-card').forEach(card => {{
        if (cls === 'ALL' || card.getAttribute('data-class') === cls) {{
          card.style.display = 'block';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}
  </script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
