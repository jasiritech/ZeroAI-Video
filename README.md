# 🎬 ZeroAI-Video

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)
![FFmpeg](https://img.shields.io/badge/Engine-FFmpeg-red.svg)
![Zero Cost](https://img.shields.io/badge/Cost-%240.00%20(No%20AI%20APIs)-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**Autonomous, zero-cost programmatic video creation engine powered by pure open source.**  
*Turn any topic into an engaging, high-definition video in seconds without paying for OpenAI, Sora, or cloud GPUs.*

[Features](#-key-features) • [Quickstart](#-quickstart) • [Web Studio](#-web-studio-dashboard) • [Architecture](#-architecture) • [Roadmap](#-roadmap)

</div>

---

## 💡 The Philosophy

Most automated video tools today force you into expensive subscriptions ($30–$100/mo) and proprietary cloud APIs (OpenAI, Runway, Pika, Midjourney) that take minutes to render a single short clip.

**ZeroAI-Video** proves that by combining battle-tested legacy open-source powerhouses (**FFmpeg**, **Windows SAPI**, **Wikimedia Commons**, **Wikipedia**) with modern programmatic video workflows, you can generate complete, high-definition videos with motion, sound, voice, and animated subtitles **in under 45 seconds—100% free, offline, and open-source.**

---

## ⚡ Key Features

- **🌐 Autonomous Open Asset Harvester:**  
  Type any topic (e.g., `"Mount Kilimanjaro"`, `"Serengeti Lion"`, `"Ancient Egypt"`). The engine automatically discovers and downloads high-resolution (HD/4K) Creative Commons & Public Domain imagery and encyclopedic summaries without any API keys.

- **🎥 Cinematic Ken Burns Suite:**  
  Still images are transformed into dynamic cinematic sequences using 5 distinct procedural camera motions:
  - *Hero Push-In* (smooth zoom to center)
  - *Epic Reveal* (slow outward zoom)
  - *Pan Left-to-Right* (horizontal tracking)
  - *Pan Right-to-Left* (reverse tracking)
  - *Upward Tilt / Rise* (vertical tracking)

- **🔥 TikTok / Alex Hormozi Dynamic Subtitles:**  
  Native ASS (*Advanced SubStation Alpha*) word-by-word animated subtitles. Words light up in vibrant neon yellow and scale dynamically with speech rhythm.

- **🎙️ Zero-Cost Offline Voice & Audio Ducking:**  
  - Offline text-to-speech narration (via built-in Windows SAPI or speech synthesis).
  - Procedural harmonic ambient soundtrack generated mathematically on-the-fly with FFmpeg audio filters.
  - Intelligent audio ducking: background music volume dips automatically when the narrator speaks.

- **📱 Multi-Format Export:**  
  - **9:16 Vertical (1080x1920):** Optimized for TikTok, YouTube Shorts, and Instagram Reels.
  - **16:9 Landscape (1920x1080):** Optimized for YouTube documentaries and cinema.
  - **1:1 Square (1080x1080):** Optimized for Instagram posts.

- **💻 Built-in Local Web Studio Dashboard:**  
  A sleek, modern glassmorphic web dashboard that runs directly in your browser with live video preview and 1-click downloads.

---

## 🏗️ Architecture

```text
[Topic / Prompt]
       │
       ▼
┌────────────────────────────────────────────────────────┐
│ 1. Autonomous Fetcher (Wikimedia & Wikipedia)          │
│    - Extracts high-res photos & curated text summary    │
└───────────────────────┬────────────────────────────────┘
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│ 2. Audio Engine (Offline)    │  │ 3. Subtitle Engine (ASS)     │
│    - TTS Voice Narration     │  │    - Word-by-word highlights │
│    - Ambient Music Synthesis │  │    - Bold TikTok / Hormozi   │
│    - Automatic Audio Ducking │  │      typography              │
└──────────────┬───────────────┘  └──────────────┬───────────────┘
               │                                 │
               └────────────────┬────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────┐
│ 4. FFmpeg Master Compositor                            │
│    - Ken Burns Camera Choreography                     │
│    - Title Card Badges & ASS Subtitle Burning          │
│    - H.264 & AAC Hardware-Accelerated Export           │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
         🎉 Finished MP4 in < 45 Seconds!
```

---

## 🚀 Quickstart

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg** installed and added to your system `PATH`.  
  *(Verify by running `ffmpeg -version` in your terminal)*

### 2. Clone the Repository
```bash
git clone https://github.com/jasiritech/ZeroAI-Video.git
cd ZeroAI-Video
```

### 3. Run the Interactive Wizard
```bash
python main.py
```
*Follow the interactive prompts to choose a topic, format, and generate your video!*

---

## 🖥️ Web Studio Dashboard

Launch the local web dashboard for a visual, 1-click video studio experience:

```bash
python main.py --web
```
Or on Windows, simply double-click **`start.bat`**.

Then open your browser at **`http://localhost:7860`**.

---

## ⌨️ CLI Usage Examples

#### Create a TikTok / Shorts Video (9:16 Vertical)
```bash
python main.py --topic "Mount Kilimanjaro" --format shorts --images 4
```

#### Create a YouTube Documentary Video (16:9 Landscape)
```bash
python main.py --topic "Serengeti Lion" --format landscape --images 5
```

#### Provide a Custom Script
```bash
python main.py --topic "Zanzibar" --format shorts --script "Zanzibar is a paradise of white sandy beaches and rich historic architecture."
```

#### Music Only (No Narration)
```bash
python main.py --topic "Deep Space" --format landscape --no-narration
```

---

## 📁 Repository Structure

```text
ZeroAI-Video/
├── engine/
│   ├── __init__.py      # Engine exports
│   ├── fetcher.py       # Open-source scraper & asset downloader
│   ├── audio.py         # Offline TTS, ambient music synthesis & ducking
│   ├── subtitles.py     # Animated TikTok ASS subtitle generator
│   ├── video.py         # FFmpeg Ken Burns compositor & typography
│   └── pipeline.py      # Master orchestrator connecting all modules
├── web_ui.py            # Zero-dependency local Web Studio GUI
├── main.py              # CLI entry point & interactive wizard
├── start.bat            # Windows 1-click launcher
├── LICENSE              # MIT License
└── README.md            # Documentation
```

---

## 🤝 Contributing

Contributions are warmly welcome! If you have ideas for:
- Sourcing free B-roll video clips (e.g. Internet Archive / Pexels)
- Additional subtitle animations and transitions
- Multilingual voice support

Feel free to fork the repository, open an issue, or submit a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details. Built with ❤️ by **[Jasiri Tech](https://github.com/jasiritech)**.
