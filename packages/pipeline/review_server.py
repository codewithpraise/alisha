"""
Local Human Review Server for Voice Refinery Pipeline.
Runs on localhost:5000 with zero external dependencies.
Allows reviewing clips, editing transcripts, and accepting/rejecting clips.
"""

import http.server
import json
import os
import urllib.parse
from typing import Dict, Any


PORT = 5000
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
VOICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "voice"))
DECISIONS_FILE = os.path.join(DATA_DIR, "review_decisions.json")


def load_manifest() -> list:
    manifest_path = os.path.join(DATA_DIR, "quality_manifest.jsonl")
    items = []
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
    return items


def load_decisions() -> Dict[str, Any]:
    if os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_decisions(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class ReviewHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.render_ui()
        elif parsed.path.startswith("/voice/"):
            # Serve WAV file
            fname = os.path.basename(parsed.path)
            wav_path = os.path.join(VOICE_DIR, fname)
            if os.path.exists(wav_path):
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(os.path.getsize(wav_path)))
                self.end_headers()
                with open(wav_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Audio file not found")
        elif parsed.path == "/api/status":
            items = load_manifest()
            decisions = load_decisions()
            res = {
                "total": len(items),
                "reviewed": len(decisions),
                "remaining": len(items) - len(decisions),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/decision":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8"))
            cid = payload.get("id")
            if cid:
                decisions = load_decisions()
                decisions[cid] = {
                    "action": payload.get("action"),
                    "transcript": payload.get("transcript", ""),
                    "tag": payload.get("tag", "normal"),
                }
                save_decisions(decisions)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            else:
                self.send_error(400, "Missing id")
        else:
            self.send_error(404)

    def render_ui(self):
        items = load_manifest()
        decisions = load_decisions()

        # Find items that need review (either low confidence or B/C/R class)
        review_queue = [
            it for it in items
            if os.path.splitext(it["file"])[0] not in decisions
        ]

        current_item = review_queue[0] if review_queue else None
        current_id = os.path.splitext(current_item["file"])[0] if current_item else ""
        current_file = current_item["file"] if current_item else ""

        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Alisha Bubbzieee — Voice Review Queue</title>
  <style>
    body {{ background: #111210; color: #F2EFE8; font-family: sans-serif; padding: 40px 20px; }}
    .container {{ max-width: 680px; margin: 0 auto; background: #1B1C1A; padding: 28px; border-radius: 12px; border: 1px solid #2C2D2A; }}
    h2 {{ font-family: Georgia, serif; color: #D4A853; margin-top: 0; }}
    .meta {{ font-size: 13px; color: #8A8880; margin-bottom: 20px; }}
    audio {{ width: 100%; margin: 16px 0; }}
    textarea {{ width: 100%; background: #141513; border: 1px solid #333; color: #F2EFE8; padding: 12px; border-radius: 6px; box-sizing: border-box; font-size: 15px; }}
    .btn-row {{ display: flex; gap: 10px; margin-top: 20px; }}
    button {{ flex: 1; padding: 12px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; }}
    .btn-accept {{ background: #5E7A68; color: white; }}
    .btn-reject {{ background: #C47067; color: white; }}
    .btn-para {{ background: #A38671; color: white; }}
  </style>
</head>
<body>
  <div class="container">
    <h2>Voice Review Queue</h2>
    <div class="meta">Remaining: {len(review_queue)} of {len(items)} &middot; Reviewed: {len(decisions)}</div>
    {f'''
    <h3>Clip ID: {current_id}</h3>
    <p>Duration: {current_item.get("duration_sec", 0)}s &middot; Score: {current_item.get("quality_score", 0)} ({current_item.get("classification")})</p>
    <audio controls src="/voice/{current_file}"></audio>
    <p>Correct Transcript:</p>
    <textarea id="tx" rows="3" placeholder="Enter transcript..."></textarea>
    <div class="btn-row">
      <button class="btn-accept" onclick="decide('accept')">Accept (Core)</button>
      <button class="btn-para" onclick="decide('paralinguistic')">Flag Paralinguistic</button>
      <button class="btn-reject" onclick="decide('reject')">Reject</button>
    </div>
    ''' if current_item else '<p>All clips have been reviewed!</p>'}
  </div>
  <script>
    function decide(action) {{
      fetch('/api/decision', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          id: '{current_id}',
          action: action,
          transcript: document.getElementById('tx').value
        }})
      }}).then(() => location.reload());
    }}
  </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


def start_server():
    server = http.server.HTTPServer(("0.0.0.0", PORT), ReviewHandler)
    print(f"Review server running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    start_server()
