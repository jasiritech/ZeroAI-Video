"""
engine/pipeline.py
Master orchestrator connecting Fetcher, Audio, Subtitles, and Video modules.
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from engine.fetcher import fetch_images_for_topic, search_topic_and_summary
from engine.audio import create_complete_audio_track
from engine.subtitles import generate_animated_ass
from engine.video import compose_final_video, RESOLUTIONS

def create_video_from_topic(
    topic: str,
    format_type: str = "shorts",
    include_narration: bool = True,
    custom_script: Optional[str] = None,
    num_images: int = 4,
    enable_subtitles: bool = True,
    output_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the entire automated video pipeline:
    1. Researches the topic & retrieves high-res open-source photos.
    2. Composes narration with word boundary timestamps & cinematic ambient soundtrack.
    3. Builds animated TikTok-style dynamic ASS subtitles.
    4. Renders Ken Burns camera motion & typography.
    5. Exports high-definition MP4.
    """
    start_time = time.time()
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    clean_topic = topic.strip()
    safe_name = "".join(c if c.isalnum() else "_" for c in clean_topic).lower()
    
    if not output_filename:
        output_filename = os.path.join("output", f"{safe_name}_{format_type}.mp4")

    print("\n" + "="*60)
    print(f"🎬 [ZeroAI-Video] Inaanza kutengeneza video: '{clean_topic}'")
    print(f"📐 Muundo: {format_type.upper()} | 🎙️ Sauti: {'Ndio' if include_narration else 'Muziki pekee'} | 📝 Subtitles: {'Ndio' if enable_subtitles else 'Hapana'}")
    print("="*60)

    # Step 1: Research & Media Fetching
    print("\n[Hatua 1/4] 🔍 Inatafuta picha na taarifa za open-source...")
    resolved_title, summary = search_topic_and_summary(clean_topic)
    print(f" -> Mada iliyopatikana: '{resolved_title}'")
    
    narration_text = ""
    if include_narration:
        if custom_script and custom_script.strip():
            narration_text = custom_script.strip()
        else:
            sentences = [s.strip() for s in summary.split(".") if len(s.strip()) > 15]
            narration_text = ". ".join(sentences[:2]) + "." if sentences else f"This is an overview of {resolved_title}."
        print(f" -> Maelezo ya Sauti (Narration): \"{narration_text[:120]}...\"")

    images = fetch_images_for_topic(clean_topic, max_images=num_images, download_dir="downloads")
    if not images:
        raise RuntimeError(f"Hakuna picha zilizopatikana mtandaoni kwa mada '{clean_topic}'. Jaribu mada nyingine au ongeza picha zako.")

    print(f" -> Picha zilizopakuliwa kwa mafanikio: {len(images)}")

    # Step 2: Audio Synthesis & Mixing
    print("\n[Hatua 2/4] 🎵 Inatengeneza sauti na muziki wa chinichini (Ducking)...")
    audio_path = os.path.join("output", f"temp_master_{safe_name}.m4a")
    default_duration = float(len(images) * 4.0)
    
    master_audio, final_duration, words_data = create_complete_audio_track(
        narration_text=narration_text if include_narration else None,
        total_duration=default_duration,
        output_path=audio_path
    )
    print(f" -> Sauti kamili tayari! Urefu wa video: {final_duration:.1f} sekunde")

    # Step 3: Dynamic TikTok/Hormozi Subtitles
    ass_subtitle_path = None
    if enable_subtitles and narration_text:
        print("\n[Hatua 3/4] 📝 Inatengeneza maandishi yanayocheza (TikTok Dynamic Subtitles)...")
        w, h = RESOLUTIONS.get(format_type.lower(), RESOLUTIONS["shorts"])
        ass_path = os.path.join("output", f"temp_subs_{safe_name}.ass")
        ass_subtitle_path = generate_animated_ass(
            words_data=words_data,
            output_ass_path=ass_path,
            video_width=w,
            video_height=h,
            raw_text=narration_text,
            total_duration=final_duration
        )
        print(f" -> Subtitles za ASS zimeandaliwa kwa mafanikio.")

    # Step 4: Video Animation & Compositing
    print("\n[Hatua 4/4] 🎥 Inachakata mwendo wa picha (Ken Burns Pan & Zoom), maneno na kuunganisha...")
    final_video = compose_final_video(
        image_paths=images,
        audio_path=master_audio,
        output_path=output_filename,
        title_text=resolved_title,
        format_type=format_type,
        total_duration=final_duration,
        subtitles_ass_path=ass_subtitle_path
    )

    # Clean up temp files
    for tmp in [audio_path, ass_subtitle_path]:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(final_video) / (1024 * 1024)

    print("\n" + "="*60)
    print("✨ MAFANIKIO MAKUBWA! VIDEO IMETENGENEZWA!")
    print(f"📁 Faili: {os.path.abspath(final_video)}")
    print(f"⏱️ Muda uliotumika: {elapsed:.1f} sekunde")
    print(f"📦 Saizi ya Video: {file_size_mb:.2f} MB")
    print(f"🕒 Urefu wa Video: {final_duration:.1f}s")
    print("="*60 + "\n")

    return {
        "video_path": os.path.abspath(final_video),
        "duration": final_duration,
        "size_mb": file_size_mb,
        "elapsed_seconds": elapsed,
        "title": resolved_title,
        "images_count": len(images)
    }
