"""
main.py - ZeroAI-Video Entry Point
Automated Video Creation Engine using Open Source Legacy & Modern Tools.
"""

import os
import sys
import argparse
import subprocess

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from engine.pipeline import create_video_from_topic

def open_file_in_player(filepath: str):
    """Opens the generated video in the system default media player."""
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])
    except Exception as e:
        print(f"[Player] Could not auto-launch video player: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="ZeroAI-Video: Tengeneza video kiotomatiki kwa kutumia open-source bila AI ya kulipia."
    )
    parser.add_argument("--web", action="store_true", help="Fungua kiolesura cha kisasa cha Web (Web UI Dashboard)")
    parser.add_argument("--port", type=int, default=7860, help="Port ya Web UI (chaguo-msingi: 7860)")
    parser.add_argument("--topic", "-t", type=str, help="Mada ya video (mfano: 'Mount Kilimanjaro', 'Serengeti lion', 'Solar System')")
    parser.add_argument("--format", "-f", choices=["shorts", "landscape", "square"], default=None, help="Muundo wa video: shorts (9:16), landscape (16:9), square (1:1)")
    parser.add_argument("--no-narration", action="store_true", help="Zima maelezo ya sauti (tumia muziki pekee)")
    parser.add_argument("--no-subtitles", action="store_true", help="Zima maandishi yanayocheza (TikTok subtitles)")
    parser.add_argument("--script", "-s", type=str, default=None, help="Maandishi yako mwenyewe ya maelezo ya sauti (hiari)")
    parser.add_argument("--images", "-i", type=int, default=4, help="Idadi ya picha zitakazopakuliwa na kutumiwa (chaguo-msingi: 4)")
    parser.add_argument("--open", "-o", action="store_true", default=True, help="Fungua video moja kwa moja ikimaliza kuandaliwa")

    args = parser.parse_args()

    # Launch Web UI if requested
    if args.web:
        from web_ui import start_server
        start_server(args.port)
        return

    topic = args.topic
    format_type = args.format
    include_narration = not args.no_narration
    enable_subtitles = not args.no_subtitles
    custom_script = args.script
    num_images = args.images

    if not topic:
        print("\n" + "="*65)
        print("🎥 KARIBU KWENYE ZEROAI-VIDEO (100% BURE & OPEN SOURCE) 🎥")
        print("Inachanganya zana thabiti za Open Source (FFmpeg, Wikipedia, SAPI)")
        print("="*65)
        
        default_topic = "Mount Kilimanjaro"
        user_input = input(f"\n👉 Unataka video kuhusu mada gani? (Bonyeza Enter kwa '{default_topic}'): ").strip()
        topic = user_input if user_input else default_topic

        print("\nChagua Muundo wa Video:")
        print(" [1] Shorts / TikTok / Reels (Wima - 9:16) [Chaguo-msingi]")
        print(" [2] YouTube / Cinema (Mlalo - 16:9)")
        print(" [3] Instagram Post (Mraba - 1:1)")
        choice = input("Namba (1/2/3) au bonyeza Enter: ").strip()
        if choice == "2":
            format_type = "landscape"
        elif choice == "3":
            format_type = "square"
        else:
            format_type = "shorts"

        voice_choice = input("\n🎙️ Je, unataka maelezo ya sauti ya kiotomatiki (Narration)? (Ndio/Hapana, bonyeza Enter kwa Ndio): ").strip().lower()
        if voice_choice in ["h", "hapana", "no", "n"]:
            include_narration = False

    if not format_type:
        format_type = "shorts"

    # Run the automated pipeline
    result = create_video_from_topic(
        topic=topic,
        format_type=format_type,
        include_narration=include_narration,
        custom_script=custom_script,
        num_images=num_images,
        enable_subtitles=enable_subtitles
    )

    if args.open and os.path.exists(result["video_path"]):
        print(f"🚀 Inafungua video yako kwenye player...")
        open_file_in_player(result["video_path"])

if __name__ == "__main__":
    main()
