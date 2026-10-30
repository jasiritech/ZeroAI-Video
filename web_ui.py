"""
web_ui.py - ZeroAI-Video Web Dashboard
A modern, zero-dependency browser interface for creating automated videos.
Runs locally using Python standard library http.server.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from engine.pipeline import create_video_from_topic

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroAI-Video Studio | 100% Open Source Video Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(22, 30, 49, 0.7);
            --border: rgba(255, 255, 255, 0.08);
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.35);
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body {
            background-color: var(--bg);
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.12) 0px, transparent 50%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 20px;
        }
        .container {
            max-width: 1050px;
            width: 100%;
        }
        header {
            text-align: center;
            margin-bottom: 35px;
        }
        .badge {
            display: inline-block;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #818cf8;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }
        h1 {
            font-size: 2.75rem;
            font-weight: 800;
            background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        p.subtitle {
            color: var(--text-muted);
            font-size: 1.05rem;
        }
        .grid {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 25px;
        }
        @media (max-width: 860px) {
            .grid { grid-template-columns: 1fr; }
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px;
            backdrop-filter: blur(16px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 8px;
            color: #e2e8f0;
        }
        input[type="text"], textarea, select {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 13px 16px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }
        input[type="text"]:focus, textarea:focus, select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }
        .format-selector {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .format-card {
            border: 1px solid var(--border);
            background: rgba(15, 23, 42, 0.5);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .format-card:hover { border-color: rgba(99, 102, 241, 0.5); }
        .format-card.active {
            border-color: var(--accent);
            background: rgba(99, 102, 241, 0.15);
            box-shadow: 0 0 0 1px var(--accent);
        }
        .format-card .icon { font-size: 1.5rem; margin-bottom: 4px; }
        .format-card .title { font-size: 0.82rem; font-weight: 700; }
        .format-card .sub { font-size: 0.7rem; color: var(--text-muted); }
        
        .toggle-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 12px;
        }
        .toggle-label {
            font-size: 0.9rem;
            font-weight: 600;
        }
        .toggle-desc {
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #334155; transition: .3s; border-radius: 24px;
        }
        .slider:before {
            position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px;
            background-color: white; transition: .3s; border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--accent); }
        input:checked + .slider:before { transform: translateX(20px); }

        .btn-submit {
            width: 100%;
            background: var(--accent-gradient);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 16px;
            font-size: 1.05rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 10px 25px var(--accent-glow);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px var(--accent-glow);
        }
        .btn-submit:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        /* Right Preview Column */
        .preview-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 420px;
            background: rgba(10, 15, 26, 0.8);
            border: 2px dashed rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        video {
            width: 100%;
            max-height: 480px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            background: #000;
        }
        .status-container {
            margin-top: 15px;
            width: 100%;
            display: none;
        }
        .spinner {
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255,255,255,0.2);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .log-box {
            background: #0f172a;
            border-radius: 8px;
            padding: 12px;
            font-family: monospace;
            font-size: 0.8rem;
            color: #38bdf8;
            max-height: 120px;
            overflow-y: auto;
            text-align: left;
            margin-top: 10px;
            border: 1px solid rgba(255,255,255,0.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge">🚀 100% Open Source & Zero Cost</div>
            <h1>ZeroAI-Video Studio</h1>
            <p class="subtitle">Tengeneza video za ubora wa juu kiotomatiki kwa FFmpeg bila kutumia AI ya gharama</p>
        </header>

        <div class="grid">
            <!-- Left Config Form -->
            <div class="card">
                <div class="form-group">
                    <label>Mada ya Video (Topic / Subject):</label>
                    <input type="text" id="topicInput" placeholder="mfano: Mount Kilimanjaro, Serengeti Lion, Zanzibar, Ferrari..." value="Mount Kilimanjaro">
                </div>

                <div class="form-group">
                    <label>Muundo wa Video (Aspect Ratio):</label>
                    <div class="format-selector">
                        <div class="format-card active" onclick="selectFormat('shorts', this)">
                            <div class="icon">📱</div>
                            <div class="title">Shorts / TikTok</div>
                            <div class="sub">9:16 Wima (1080x1920)</div>
                        </div>
                        <div class="format-card" onclick="selectFormat('landscape', this)">
                            <div class="icon">🖥️</div>
                            <div class="title">YouTube HD</div>
                            <div class="sub">16:9 Mlalo (1920x1080)</div>
                        </div>
                        <div class="format-card" onclick="selectFormat('square', this)">
                            <div class="icon">⏹️</div>
                            <div class="title">Instagram</div>
                            <div class="sub">1:1 Mraba (1080x1080)</div>
                        </div>
                    </div>
                </div>

                <div class="toggle-row">
                    <div>
                        <div class="toggle-label">🎙️ Maelezo ya Sauti (Voice Narration)</div>
                        <div class="toggle-desc">Sauti ya binadamu isiyotumia mtandao (Offline SAPI)</div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="narrationToggle" checked>
                        <span class="slider"></span>
                    </label>
                </div>

                <div class="toggle-row">
                    <div>
                        <div class="toggle-label">⚡ Maandishi ya TikTok (Dynamic Subtitles)</div>
                        <div class="toggle-desc">Maneno yanayong'aa moja kwa moja kwa mdundo wa sauti</div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="subtitlesToggle" checked>
                        <span class="slider"></span>
                    </label>
                </div>

                <div class="form-group" style="margin-top: 15px;">
                    <label>Maandishi Yako ya Simulizi (Hiari):</label>
                    <textarea id="customScript" rows="3" placeholder="Acha wazi ili mfumo uchukue taarifa kiotomatiki kutoka Wikipedia..."></textarea>
                </div>

                <button class="btn-submit" id="btnGenerate" onclick="generateVideo()">
                    <span>🎬 Tengeneza Video Sasa (Create Video)</span>
                </button>
            </div>

            <!-- Right Preview Column -->
            <div class="card">
                <label>Matokeo ya Video (Video Preview):</label>
                <div class="preview-box" id="previewArea">
                    <div id="placeholderText">
                        <div style="font-size: 3rem; margin-bottom: 10px;">🎥</div>
                        <p style="color: var(--text-muted); font-size: 0.9rem;">
                            Jaza mada upande wa kushoto kisha bonyeza <b>Tengeneza Video</b>. Video yako itaonekana hapa ikiwa tayari kuangaliwa na kupakuliwa.
                        </p>
                    </div>
                    <video id="videoPlayer" controls style="display: none;"></video>
                </div>

                <div class="status-container" id="statusArea">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <div class="spinner"></div>
                        <span id="statusText" style="font-size: 0.9rem; font-weight: 600;">Inatafuta picha na kutayarisha sauti...</span>
                    </div>
                    <div class="log-box" id="logBox">Inaanza mchakato...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFormat = 'shorts';

        function selectFormat(fmt, el) {
            selectedFormat = fmt;
            document.querySelectorAll('.format-card').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
        }

        async function generateVideo() {
            const topic = document.getElementById('topicInput').value.trim();
            if (!topic) {
                alert('Tafadhali andika mada ya video kwanza!');
                return;
            }

            const btn = document.getElementById('btnGenerate');
            const statusArea = document.getElementById('statusArea');
            const statusText = document.getElementById('statusText');
            const logBox = document.getElementById('logBox');
            const placeholder = document.getElementById('placeholderText');
            const videoPlayer = document.getElementById('videoPlayer');

            btn.disabled = true;
            statusArea.style.display = 'block';
            statusText.innerText = 'Inachakata video... tafadhali subiri sekunde chache...';
            logBox.innerText = `[1/4] Inatafuta picha za bure za '${topic}'...`;
            placeholder.style.display = 'none';
            videoPlayer.style.display = 'none';

            const payload = {
                topic: topic,
                format: selectedFormat,
                narration: document.getElementById('narrationToggle').checked,
                subtitles: document.getElementById('subtitlesToggle').checked,
                script: document.getElementById('customScript').value.trim()
            };

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (data.success) {
                    statusText.innerText = '✨ Video Imekamilika!';
                    logBox.innerText = `Imekamilika kwa sekunde ${data.elapsed.toFixed(1)}s! Saizi: ${data.size_mb.toFixed(2)} MB`;
                    videoPlayer.src = data.video_url + '?t=' + new Date().getTime();
                    videoPlayer.style.display = 'block';
                    videoPlayer.play();
                } else {
                    statusText.innerText = 'Hitilafu imetokea!';
                    logBox.innerText = 'Error: ' + data.error;
                    placeholder.style.display = 'block';
                }
            } catch (err) {
                statusText.innerText = 'Hitilafu ya mtandao!';
                logBox.innerText = err.message;
                placeholder.style.display = 'block';
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

class VideoStudioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path).path
        if url_path == "/" or url_path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif url_path.startswith("/output/"):
            # Serve video from output folder
            rel_file = url_path.replace("/output/", "").split("?")[0]
            file_path = os.path.join("output", rel_file)
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(os.path.getsize(file_path)))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/generate":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                topic = data.get("topic", "Mount Kilimanjaro")
                format_type = data.get("format", "shorts")
                narration = data.get("narration", True)
                subtitles = data.get("subtitles", True)
                script = data.get("script", None)

                result = create_video_from_topic(
                    topic=topic,
                    format_type=format_type,
                    include_narration=narration,
                    custom_script=script,
                    enable_subtitles=subtitles
                )

                rel_video_url = "/output/" + os.path.basename(result["video_path"])
                response_data = {
                    "success": True,
                    "video_url": rel_video_url,
                    "elapsed": result["elapsed_seconds"],
                    "size_mb": result["size_mb"],
                    "duration": result["duration"]
                }
            except Exception as e:
                response_data = {
                    "success": False,
                    "error": str(e)
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

def start_server(port=7860):
    server = HTTPServer(("127.0.0.1", port), VideoStudioHandler)
    print(f"\n=======================================================")
    print(f"🌐 ZeroAI-Video Web Dashboard imewashwa!")
    print(f"👉 Fungua browser yako kwa: http://localhost:{port}")
    print(f"=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStudio server stopped.")

if __name__ == "__main__":
    port = 7860
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    start_server(port)
